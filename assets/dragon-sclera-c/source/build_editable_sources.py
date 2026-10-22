#!/usr/bin/env python3
"""Wrap the selected, unchanged AI raster in editable PSD/OpenRaster files.

No painting, recolouring or runtime resizing is performed. Dependencies are
Python 3 and Pillow. ImageMagick is used only for an extra PSD readback check
when its `convert` command is already installed; nothing is downloaded.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import zipfile
from xml.etree import ElementTree as ET

from PIL import Image, ImageDraw, __version__ as PILLOW_VERSION

RUNTIME_SHA256 = "5775c62ce834c1e3573148241f2589e434d0226a9cea4d88ad78348d2c4c9887"
ORIGINAL_SHA256 = "a3033cd38dffeb06125b6ff7d8081d58eedfe8c66b46d8f67f357a2ece20fd66"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def png_bytes(image):
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def check_pixels(actual, expected):
    assert actual.size == expected.size
    assert actual.convert("RGBA").tobytes() == expected.convert("RGBA").tobytes()
    return {"different_pixels": 0, "max_channel_difference": 0}


def packbits(row):
    result = bytearray()
    i, size = 0, len(row)
    while i < size:
        run = 1
        while i + run < size and run < 128 and row[i + run] == row[i]:
            run += 1
        if run >= 3:
            result.extend((257 - run, row[i]))
            i += run
            continue
        start = i
        i += run
        while i < size and i - start < 128:
            run = 1
            while i + run < size and run < 3 and row[i + run] == row[i]:
                run += 1
            if run >= 3:
                break
            i += min(run, 128 - (i - start))
        result.append(i - start - 1)
        result.extend(row[start:i])
    return bytes(result)


def unpackbits(data, width):
    output = bytearray()
    pos = 0
    while pos < len(data):
        count = data[pos]
        pos += 1
        if count <= 127:
            output.extend(data[pos:pos + count + 1])
            pos += count + 1
        elif count >= 129:
            output.extend(bytes([data[pos]]) * (257 - count))
            pos += 1
    assert len(output) == width
    return bytes(output)


def channel_rle(image, channel):
    width, height = image.size
    data = image.getchannel(channel).tobytes()
    rows = [packbits(data[y * width:(y + 1) * width]) for y in range(height)]
    return struct.pack(">H", 1) + struct.pack(">" + "H" * height, *(len(r) for r in rows)) + b"".join(rows)


def write_psd(path, layers, merged):
    width, height = merged.size
    records, channel_data = [], []
    for name, image, visible in layers:
        channels = [(cid, channel_rle(image, key)) for cid, key in ((0, "R"), (1, "G"), (2, "B"), (-1, "A"))]
        label = name.encode("ascii")
        pascal = bytes([len(label)]) + label
        pascal += b"\0" * ((-len(pascal)) % 4)
        extra = struct.pack(">II", 0, 0) + pascal
        record = struct.pack(">iiiiH", 0, 0, height, width, len(channels))
        record += b"".join(struct.pack(">hI", cid, len(data)) for cid, data in channels)
        record += b"8BIMnorm" + bytes([255, 0, 0 if visible else 2, 0])
        record += struct.pack(">I", len(extra)) + extra
        records.append(record)
        channel_data.extend(data for _, data in channels)
    layer_info = struct.pack(">h", len(layers)) + b"".join(records) + b"".join(channel_data)
    layer_info += b"\0" * (len(layer_info) % 2)
    layer_mask = struct.pack(">I", len(layer_info)) + layer_info + struct.pack(">I", 0)
    rgb_rle = [channel_rle(merged, key) for key in "RGB"]
    table_size = height * 2
    composite = struct.pack(">H", 1) + b"".join(c[2:2 + table_size] for c in rgb_rle)
    composite += b"".join(c[2 + table_size:] for c in rgb_rle)
    header = b"8BPS" + struct.pack(">H", 1) + b"\0" * 6
    header += struct.pack(">HIIHH", 3, height, width, 8, 3)
    path.write_bytes(header + struct.pack(">II", 0, 0) + struct.pack(">I", len(layer_mask)) + layer_mask + composite)


def read_rle(stream, width, height):
    assert struct.unpack(">H", stream.read(2))[0] == 1
    sizes = struct.unpack(">" + "H" * height, stream.read(height * 2))
    raw = b"".join(unpackbits(stream.read(size), width) for size in sizes)
    return Image.frombytes("L", (width, height), raw)


def verify_psd(path, expected_layers, original):
    stream = io.BytesIO(path.read_bytes())
    assert stream.read(4) == b"8BPS"
    assert struct.unpack(">H", stream.read(2))[0] == 1
    stream.read(6)
    channels, height, width, depth, mode = struct.unpack(">HIIHH", stream.read(14))
    assert (channels, depth, mode) == (3, 8, 3)
    assert (width, height) == original.size
    for _ in range(2):
        stream.read(struct.unpack(">I", stream.read(4))[0])
    layer_mask_length = struct.unpack(">I", stream.read(4))[0]
    layer_mask_end = stream.tell() + layer_mask_length
    layer_length = struct.unpack(">I", stream.read(4))[0]
    layer_end = stream.tell() + layer_length
    layer_count = struct.unpack(">h", stream.read(2))[0]
    assert layer_count == len(expected_layers) == 3
    records = []
    for _ in range(layer_count):
        top, left, bottom, right, count = struct.unpack(">iiiiH", stream.read(18))
        assert (top, left, bottom, right) == (0, 0, height, width)
        infos = [struct.unpack(">hI", stream.read(6)) for _ in range(count)]
        assert stream.read(8) == b"8BIMnorm"
        opacity, clipping, flags, _ = stream.read(4)
        assert opacity == 255 and clipping == 0
        extra_length = struct.unpack(">I", stream.read(4))[0]
        extra_end = stream.tell() + extra_length
        stream.read(struct.unpack(">I", stream.read(4))[0])
        stream.read(struct.unpack(">I", stream.read(4))[0])
        name = stream.read(stream.read(1)[0]).decode("ascii")
        stream.seek(extra_end)
        records.append((name, infos, not bool(flags & 2)))
    reconstructed = []
    for (name, infos, visible), (expected_name, expected_image, expected_visible) in zip(records, expected_layers):
        assert (name, visible) == (expected_name, expected_visible)
        decoded = {}
        for cid, length in infos:
            end = stream.tell() + length
            decoded[cid] = read_rle(stream, width, height)
            assert stream.tell() == end
        image = Image.merge("RGBA", [decoded[c] for c in (0, 1, 2, -1)])
        check_pixels(image, expected_image)
        reconstructed.append((image, visible))
    assert stream.tell() <= layer_end
    stream.seek(layer_mask_end)
    assert struct.unpack(">H", stream.read(2))[0] == 1
    sizes = struct.unpack(">" + "H" * (height * 3), stream.read(height * 6))
    composite_channels = []
    for c in range(3):
        raw = b"".join(unpackbits(stream.read(s), width) for s in sizes[c * height:(c + 1) * height])
        composite_channels.append(Image.frombytes("L", (width, height), raw))
    merged_check = check_pixels(Image.merge("RGB", composite_channels), original)
    composite = Image.new("RGBA", original.size)
    for image, visible in reversed(reconstructed):
        if visible:
            composite.alpha_composite(image)
    composition_check = check_pixels(composite, original)
    return {"layers_read_back": 3, "individual_layer_pixels": "identical", "hidden_guide_flag": "verified", "default_composite": composition_check, "merged_preview": merged_check}


def write_and_verify_ora(path, layers, original):
    width, height = original.size
    root = ET.Element("image", {"version": "0.0.3", "w": str(width), "h": str(height), "name": "Dragon C sclera - editable raster master"})
    stack = ET.SubElement(root, "stack")
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("mimetype", "image/openraster", compress_type=zipfile.ZIP_STORED)
        for i, (name, image, visible) in enumerate(layers):
            src = f"data/layer-{i}.png"
            ET.SubElement(stack, "layer", {"name": name, "src": src, "x": "0", "y": "0", "opacity": "1.0", "visibility": "visible" if visible else "hidden", "composite-op": "svg:src-over"})
            archive.writestr(src, png_bytes(image), compress_type=zipfile.ZIP_DEFLATED)
        archive.writestr("stack.xml", ET.tostring(root, encoding="utf-8", xml_declaration=True), compress_type=zipfile.ZIP_DEFLATED)
        archive.writestr("mergedimage.png", png_bytes(original), compress_type=zipfile.ZIP_DEFLATED)
        thumbnail = original.copy()
        thumbnail.thumbnail((256, 256))
        archive.writestr("Thumbnails/thumbnail.png", png_bytes(thumbnail), compress_type=zipfile.ZIP_DEFLATED)
    with zipfile.ZipFile(path) as archive:
        assert archive.testzip() is None
        assert archive.infolist()[0].filename == "mimetype"
        parsed = ET.fromstring(archive.read("stack.xml"))
        composite = Image.new("RGBA", original.size)
        decoded = []
        for element, (name, image, visible) in zip(parsed.find("stack"), layers):
            assert element.attrib["name"] == name
            assert element.attrib["visibility"] == ("visible" if visible else "hidden")
            readback = Image.open(io.BytesIO(archive.read(element.attrib["src"]))).convert("RGBA")
            check_pixels(readback, image)
            decoded.append((readback, visible))
        assert len(decoded) == 3
        for image, visible in reversed(decoded):
            if visible:
                composite.alpha_composite(image)
        composition_check = check_pixels(composite, original)
        merged_check = check_pixels(Image.open(io.BytesIO(archive.read("mergedimage.png"))), original)
    return {"ZIP_CRC": "passed", "layers_read_back": 3, "individual_layer_pixels": "identical", "guide_visibility": "hidden", "default_composite": composition_check, "merged_preview": merged_check}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--original", type=Path, help="Copy this selected original once; default uses packaged PNG")
    parser.add_argument("--runtime", type=Path, help="Read-only final PNG check; default is ../submission/sclera.png")
    args = parser.parse_args()
    root = args.source_root.resolve()
    (root / "layers").mkdir(parents=True, exist_ok=True)
    original_path = root / "layers/01-ai-original.png"
    if args.original and args.original.resolve() != original_path:
        assert digest(args.original) == ORIGINAL_SHA256
        shutil.copyfile(args.original, original_path)
    assert digest(original_path) == ORIGINAL_SHA256
    original = Image.open(original_path).convert("RGBA")
    assert original.size == (1254, 1254)
    runtime = args.runtime or root.parent / "submission/sclera.png"
    assert digest(runtime) == RUNTIME_SHA256
    with Image.open(runtime) as image:
        assert image.size == (480, 480) and image.mode == "RGB"
    retouch = Image.new("RGBA", original.size)
    guide = Image.new("RGBA", original.size)
    draw = ImageDraw.Draw(guide)
    scale = original.width / 480
    cx = cy = 240 * scale
    radius = 233 * scale
    iris = (233 * 26870 / 32768) * scale
    line_width = max(1, round(scale))
    for r, colour in ((radius, (255, 72, 72, 220)), (iris, (255, 221, 62, 220))):
        draw.ellipse((cx - r, cy - r, cx + r, cy + r), outline=colour, width=line_width)
    draw.line((cx - 12 * scale, cy, cx + 12 * scale, cy), fill=(255, 255, 255, 220), width=line_width)
    draw.line((cx, cy - 12 * scale, cx, cy + 12 * scale), fill=(255, 255, 255, 220), width=line_width)
    retouch.save(root / "layers/02-retouch-blank.png")
    guide.save(root / "layers/03-geometry-guide-hidden.png")
    layers = [("03 Geometry guide - HIDDEN", guide, False), ("02 Retouch - initially blank", retouch, True), ("01 AI original - flattened raster", original, True)]
    psd_path, ora_path = root / "sclera-master.psd", root / "sclera-master.ora"
    write_psd(psd_path, layers, original)
    psd_check = verify_psd(psd_path, layers, original)
    ora_check = write_and_verify_ora(ora_path, layers, original)
    converter = shutil.which("convert")
    independent_check = {"performed": False}
    if converter:
        checks = []
        for i, expected in enumerate([original] + [layer[1] for layer in layers]):
            data = subprocess.check_output([converter, f"{psd_path}[{i}]", "-depth", "8", "PNG32:-"], stderr=subprocess.PIPE)
            checks.append(check_pixels(Image.open(io.BytesIO(data)), expected))
        independent_check = {"performed": True, "tool": subprocess.check_output([converter, "-version"], text=True).splitlines()[0], "merged_and_three_layers": checks}
    report = {"master_size": list(original.size), "runtime_size": [480, 480], "type": "Editable raster container; original AI image is flattened and fibers are not separate layers", "original_sha256": digest(original_path), "runtime_sha256": digest(runtime), "runtime_rewritten": False, "geometry_in_480_coordinates": {"centre": [240, 240], "sphere_radius": 233, "iris_radius": 233 * 26870 / 32768}, "layers_top_to_bottom": [{"name": name, "visible": visible} for name, _, visible in layers], "PSD": psd_check, "ORA": ora_check, "independent_ImageMagick_PSD_readback": independent_check, "versions": {"Python": sys.version.split()[0], "Pillow": PILLOW_VERSION}, "GUI_roundtrip_verified": False, "native_GSP_or_hardware_verified": False, "outputs": {p.name: {"bytes": p.stat().st_size, "sha256": digest(p)} for p in (psd_path, ora_path)}}
    (root / "editable-checks.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"master_size": report["master_size"], "outputs": report["outputs"], "PSD_default_composite": psd_check["default_composite"], "ORA_default_composite": ora_check["default_composite"], "independent_PSD_readback": independent_check["performed"], "runtime_rewritten": False}, indent=2))


if __name__ == "__main__":
    main()
