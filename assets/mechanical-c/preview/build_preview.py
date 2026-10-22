#!/usr/bin/env python3
"""Embed the local mechanical-C PNG assets and deterministic timeline into HTML.

Python 3 standard library only. This creates a browser reference, not native
C/GSP integration or sensor validation. It never installs dependencies.
"""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import struct


def png_data(path: Path, expected_size: tuple[int, int]) -> tuple[str, dict]:
    raw = path.read_bytes()
    if raw[:8] != b"\x89PNG\r\n\x1a\n" or raw[12:16] != b"IHDR":
        raise ValueError(f"Not a PNG: {path}")
    width, height = struct.unpack(">II", raw[16:24])
    if (width, height) != expected_size:
        raise ValueError(f"{path}: {(width, height)} != {expected_size}")
    return "data:image/png;base64," + base64.b64encode(raw).decode("ascii"), {
        "name": path.name, "size": [width, height], "bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
    }


def main() -> None:
    here = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package-root", type=Path, default=here.parent,
                        help="Package containing assets/processed/")
    parser.add_argument("--timeline", type=Path, default=here / "timeline.json")
    parser.add_argument("--template", type=Path, default=here / "index.template.html")
    parser.add_argument("--output", type=Path, default=here / "index.html")
    args = parser.parse_args()
    asset_dir = args.package_root.resolve() / "assets" / "processed"
    records = []
    data = {}
    for key in ("eye_surface", "frame"):
        data[key], record = png_data(asset_dir / f"{key}.png", (480, 480))
        records.append(record)
    data["shutter"] = []
    for index in range(9):
        value, record = png_data(asset_dir / "shutter" / f"shutter_{index:02d}.png", (240, 240))
        data["shutter"].append(value)
        records.append(record)
    timeline = json.loads(args.timeline.read_text(encoding="utf-8"))
    frames = timeline["frames"]
    required = {"t_ms", "state", "active", "valid", "confirmed", "candidate", "gaze_x", "gaze_y", "shutter"}
    if not frames or frames[0]["t_ms"] != 0 or frames[-1]["t_ms"] != timeline["duration_ms"]:
        raise ValueError("Timeline must cover [0,duration_ms].")
    if any(a["t_ms"] >= b["t_ms"] for a, b in zip(frames, frames[1:])):
        raise ValueError("Timeline times must be strictly increasing.")
    for frame in frames:
        if not required <= frame.keys():
            raise ValueError(f"Missing required fields at {frame.get('t_ms')} ms.")
        if not (-.78 <= frame["gaze_x"] <= .78 and -.58 <= frame["gaze_y"] <= .58 and 0 <= frame["shutter"] <= 1):
            raise ValueError(f"Out-of-range pose at {frame['t_ms']} ms.")
    html = args.template.read_text(encoding="utf-8")
    asset_marker = "/*__ASSET_DATA__*/ {}"
    timeline_marker = "/*__TIMELINE_DATA__*/ {duration_ms:28000,cases:[],frames:[]}"
    if html.count(asset_marker) != 1 or html.count(timeline_marker) != 1:
        raise ValueError("Template markers missing or repeated.")
    html = html.replace(asset_marker, json.dumps(data, ensure_ascii=False, separators=(",", ":")))
    html = html.replace(timeline_marker, json.dumps(timeline, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/"))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_name(args.output.name + ".tmp")
    temporary.write_text(html, encoding="utf-8")
    temporary.replace(args.output)
    print(json.dumps({
        "output": str(args.output.resolve()), "bytes": args.output.stat().st_size,
        "duration_ms": timeline["duration_ms"], "timeline_frames": len(frames),
        "inputs": records, "native_verified": False, "device_verified": False,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
