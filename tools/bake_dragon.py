#!/usr/bin/env python3
"""Build deterministic renderer data from the retained approved dragon textures.

Normal generation and --check read and validate retained PNGs/provenance without
opening the original references or writing sources. Only --update-assets uses
the approved originals to resize PNGs and update provenance (Pillow 10.4.0).
The generated C include and generation report belong in a local build tree.
"""

import argparse
import hashlib
import io
import json
import math
from pathlib import Path
import sys

import PIL
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
APPROVED = Path("review-inputs/peek-phase2-inputs/approved-dragon")
ASSETS = Path("assets/dragon")
OUTPUT = Path("src/dragon_assets.inc")
DEFAULT_OUTPUT = Path("build-host/dragon-generated/dragon_assets.inc")
METADATA = ASSETS / "metadata.json"
TEXTURES = (("skin", 480), ("iris", 640))


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def rounded(value):
    """Round ties away from zero, including signed Q15 sine samples."""
    return int(math.copysign(math.floor(abs(value) + 0.5), value))


def rgb565(red, green, blue):
    return (((red * 31 + 127) // 255) << 11
            | ((green * 63 + 127) // 255) << 5
            | (blue * 31 + 127) // 255)


def c_array(name, ctype, values, columns=16):
    values = list(values)
    lines = [f"static const {ctype} {name}[{len(values)}] = {{"]
    for start in range(0, len(values), columns):
        lines.append("    " + ", ".join(map(str, values[start:start + columns])) + ",")
    lines.append("};\n")
    return "\n".join(lines)


def prepare_texture(name, size, retained_metadata, update_assets):
    source_path = APPROVED / "assets" / f"{name}.png"
    prepared_path = ASSETS / f"{name}.png"
    source = ROOT / source_path
    if update_assets:
        if not source.is_file():
            raise ValueError(f"Missing approved source for --update-assets: {source_path}")
        source_bytes = source.read_bytes()
        with Image.open(io.BytesIO(source_bytes)) as original:
            source_info = {
                "path": source_path.as_posix(),
                "sha256": sha256(source_bytes),
                "width": original.width,
                "height": original.height,
                "mode": original.mode,
            }
            image = original.convert("RGB").resize((size, size), Image.Resampling.LANCZOS)
        buffer = io.BytesIO()
        image.save(buffer, format="PNG", optimize=False, compress_level=9)
        prepared_bytes = buffer.getvalue()
    else:
        # Do not inspect original references during ordinary builds.
        try:
            source_info = retained_metadata["textures"][name]["approved_source"]
            source_hash = source_info["sha256"]
            valid_source = (source_info["path"] == source_path.as_posix()
                            and isinstance(source_hash, str) and len(source_hash) == 64
                            and all(char in "0123456789abcdef" for char in source_hash)
                            and type(source_info["width"]) is int and source_info["width"] > 0
                            and type(source_info["height"]) is int and source_info["height"] > 0
                            and isinstance(source_info["mode"], str) and source_info["mode"])
        except (KeyError, TypeError) as error:
            raise ValueError(f"Missing approved-source provenance: {source_path}") from error
        if not valid_source:
            raise ValueError(f"Invalid approved-source provenance: {source_path}")
        prepared_bytes = (ROOT / prepared_path).read_bytes()
        expected_hash = retained_metadata["textures"][name]["preprocessed"]["sha256"]
        if sha256(prepared_bytes) != expected_hash:
            raise ValueError(f"Retained PNG sha256 mismatch: {prepared_path}; "
                             "restore the approved asset, do not replace its recorded hash")
        with Image.open(io.BytesIO(prepared_bytes)) as retained:
            if retained.size != (size, size) or retained.mode != "RGB":
                raise ValueError(f"Expected {size}x{size} RGB: {prepared_path}")
            image = retained.copy()
    quantized = image.quantize(colors=256, method=Image.Quantize.MEDIANCUT,
                               dither=Image.Dither.NONE)
    palette = quantized.getpalette()
    colors = [rgb565(*palette[index:index + 3]) for index in range(0, 768, 3)]
    indices = quantized.tobytes()
    description = {
        "approved_source": source_info,
        "preprocessed": {
            "path": prepared_path.as_posix(),
            "sha256": sha256(prepared_bytes),
            "pixel_sha256": sha256(image.tobytes()),
            "width": size,
            "height": size,
            "mode": "RGB",
            "resize_filter": "Pillow LANCZOS",
        },
        "quantization": {
            "method": "Pillow MEDIANCUT",
            "colors": 256,
            "dither": "NONE",
            "indices_sha256": sha256(indices),
            "index_bytes": len(indices),
            "palette_format": "RGB565, each channel rounded to nearest",
            "palette_bytes": 512,
        },
    }
    code = c_array(f"dragon_{name}_indices", "uint8_t", indices)
    code += c_array(f"dragon_{name}_palette", "uint16_t", colors)
    return prepared_path, prepared_bytes, description, code


def verify_metadata(expected, actual, field="metadata"):
    """Report the first provenance/data mismatch without repairing its record."""
    if isinstance(expected, dict) and isinstance(actual, dict):
        if expected.keys() != actual.keys():
            raise ValueError(f"Retained {field} fields differ; restore the approved metadata")
        for key in expected:
            verify_metadata(expected[key], actual[key], f"{field}.{key}")
    elif expected != actual:
        raise ValueError(f"Retained {field} mismatch (Pillow {PIL.__version__}); "
                         "use Pillow 10.4.0 for byte identity; do not automatically replace source hashes")


def bake(check, output=None, update_assets=False):
    if update_assets and PIL.__version__ != "10.4.0":
        raise ValueError("--update-assets requires Pillow 10.4.0; do not upgrade the shared environment")
    metadata_path = ROOT / METADATA
    retained = json.loads(metadata_path.read_text()) if metadata_path.is_file() else {}
    outputs = {}
    descriptions = {}
    code = ["/* Generated by tools/bake_dragon.py; do not edit. */\n",
            "#include <stdint.h>\n\n"]
    for name, size in TEXTURES:
        path, png, description, arrays = prepare_texture(name, size, retained, update_assets)
        if update_assets:
            outputs[path] = png
        descriptions[name] = description
        code.append(arrays)
    code.append(c_array("dragon_sqrt_q15", "uint16_t",
                        (rounded(math.sqrt(1 - i / 4096) * 32767) for i in range(4097))))
    code.append(c_array("dragon_pupil_q15", "uint16_t",
                        (rounded((1 - (i / 256) ** 1.7) ** .76 * 32767) for i in range(257))))
    code.append(c_array("dragon_sin_q15", "int16_t",
                        (rounded(math.sin(i * math.tau / 1024) * 32767) for i in range(1024))))
    include_bytes = "\n".join(code).encode()
    include_path = output.resolve() if output is not None else ROOT / DEFAULT_OUTPUT
    outputs[include_path] = include_bytes
    metadata = {
        "format_version": 1,
        "generator": "tools/bake_dragon.py",
        "pillow_version": PIL.__version__ if update_assets else retained.get("pillow_version"),
        "provenance": {
            "reference_readme": (APPROVED / "README.txt").as_posix(),
            "source_readme": (APPROVED / "SOURCE_README.md").as_posix(),
            "basis": "The supplied README.txt identifies this as the user-approved single dragon eye reference. SOURCE_README.md states these textures were generated with imagegen for this project.",
            "scope": "Records supplied provenance; does not assert additional licenses or permissions.",
        },
        "textures": descriptions,
        "lookup_tables": {
            "dragon_sqrt_q15": {"type": "uint16_t", "entries": 4097, "formula": "round(sqrt(1-i/4096)*32767)"},
            "dragon_pupil_q15": {"type": "uint16_t", "entries": 257, "formula": "round((1-(i/256)^1.7)^0.76*32767)"},
            "dragon_sin_q15": {"type": "int16_t", "entries": 1024, "formula": "round(sin(i*2*pi/1024)*32767)"},
        },
        "generated_include": {
            "path": OUTPUT.as_posix(),
            "sha256": sha256(include_bytes),
            "texture_data_bytes": 480 * 480 + 640 * 640 + 2 * 512,
            "lookup_table_bytes": (4097 + 257 + 1024) * 2,
            "total_data_bytes": 480 * 480 + 640 * 640 + 2 * 512 + (4097 + 257 + 1024) * 2,
        },
    }
    if update_assets:
        outputs[METADATA] = (json.dumps(metadata, indent=2) + "\n").encode()
    else:
        if not isinstance(retained.get("pillow_version"), str) or not retained["pillow_version"]:
            raise ValueError("Missing Pillow version in retained provenance")
        verify_metadata(retained, metadata)
    if not check:
        generation = {
            "generator": "tools/bake_dragon.py",
            "pillow_version": PIL.__version__,
            "source_pillow_version": metadata["pillow_version"],
            "generated_include": {**metadata["generated_include"], "path": include_path.as_posix()},
        }
        outputs[include_path.with_suffix(".generation.json")] = (json.dumps(generation, indent=2) + "\n").encode()
    mismatches = []
    for relative, expected in outputs.items():
        path = ROOT / relative
        if check:
            if not path.is_file() or path.read_bytes() != expected:
                mismatches.append(relative.as_posix())
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(expected)
    if mismatches:
        print("Regeneration differs: " + ", ".join(mismatches), file=sys.stderr)
        return 1
    generated = metadata["generated_include"]
    action = "Verified" if check else "Baked"
    print(f"{action}: textures {generated['texture_data_bytes']} bytes; "
          f"LUTs {generated['lookup_table_bytes']} bytes; "
          f"total C data {generated['total_data_bytes']} bytes")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="verify retained assets and existing include without writing")
    mode.add_argument("--update-assets", action="store_true",
                      help="explicitly resize approved originals and update retained PNGs/provenance (Pillow 10.4.0)")
    parser.add_argument("--output", type=Path, metavar="PATH",
                        help="write/check the C include at PATH (default: project build-host/dragon-generated/dragon_assets.inc)")
    arguments = parser.parse_args()
    try:
        sys.exit(bake(arguments.check, arguments.output, arguments.update_assets))
    except (OSError, ValueError, KeyError) as error:
        parser.exit(1, f"bake_dragon: {error}\n")
