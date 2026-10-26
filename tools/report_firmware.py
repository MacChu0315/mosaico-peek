#!/usr/bin/env python3
"""Inspect existing IDF artifacts; never build, flash or inspect device logs."""
import argparse
import hashlib
import json
import re
import struct
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = {
    "dragon_skin_indices", "dragon_skin_palette", "dragon_iris_indices",
    "dragon_iris_palette", "dragon_sqrt_q15", "dragon_pupil_q15", "dragon_sin_q15", "dragon_sclera_rgb",
}
# Only these memory/build selectors may leave sdkconfig. Never copy its full text.
CONFIG_ALLOW = re.compile(
    r"CONFIG_(?:SPIRAM(?:_[A-Z0-9_]+)?|IDF_TARGET(?:_[A-Z0-9_]+)?|"
    r"PEEK_(?:DIAGNOSTIC_VIEW|EYE_SAMPLE_STEP|GAZE_FLIP_[XY])|ESPTOOLPY_FLASH(?:MODE|FREQ|SIZE)[A-Z0-9_]*|"
    r"PARTITION_TABLE_(?:CUSTOM|CUSTOM_FILENAME|FILENAME|OFFSET)|"
    r"FREERTOS_(?:HZ|UNICORE|TASK_CREATE_ALLOW_EXT_MEM|IDLE_TASK_STACKSIZE)|"
    r"ESP_(?:MAIN_TASK_STACK_SIZE|SYSTEM_EVENT_TASK_STACK_SIZE|DEFAULT_CPU_FREQ_MHZ)|"
    r"CACHE_[A-Z0-9_]+|HEAP_[A-Z0-9_]+)\Z"
)


def run(argv):
    return subprocess.run([str(x) for x in argv], check=True, text=True,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout


def fingerprint(path):
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    try:
        label = str(path.relative_to(ROOT))
    except ValueError:
        label = str(path)
    return {"path": label, "bytes": path.stat().st_size, "sha256": digest.hexdigest()}


def read_config(path):
    result = {}
    for line in path.read_text().splitlines():
        match = re.fullmatch(r"(CONFIG_[A-Z0-9_]+)=(.*)", line)
        disabled = re.fullmatch(r"# (CONFIG_[A-Z0-9_]+) is not set", line)
        if match and CONFIG_ALLOW.fullmatch(match[1]):
            result[match[1]] = match[2]
        elif disabled and CONFIG_ALLOW.fullmatch(disabled[1]):
            result[disabled[1]] = "n"
    return result


def read_sections(readelf, elf):
    result = []
    for line in run([readelf, "-W", "-S", elf]).splitlines():
        match = re.match(r"\s*\[\s*(\d+)\]\s+(\.[\w.]+)\s+(\S+)\s+"
                         r"([0-9a-fA-F]+)\s+([0-9a-fA-F]+)\s+([0-9a-fA-F]+)"
                         r"\s+\S+\s+([A-Z]*)\s+", line)
        if match and "A" in match[7]:
            result.append({"name": match[2], "type": match[3],
                           "address": int(match[4], 16), "address_hex": "0x" + match[4],
                           "file_offset": int(match[5], 16), "bytes": int(match[6], 16),
                           "flags": match[7]})
    if not result:
        raise ValueError("No allocated ELF sections parsed")
    return result


def read_symbols(nm, elf, sections):
    result = []
    for line in run([nm, "-a", "-S", "--defined-only", elf]).splitlines():
        match = re.fullmatch(r"([0-9a-fA-F]+)\s+(?:([0-9a-fA-F]+)\s+)?(\S)\s+(\S+)", line)
        if not match:
            continue
        address, size, kind, name = match.groups()
        if name not in ASSETS and not re.search(r"(?:rodata|ext_ram|spiram|psram|instruction).*"
                                                r"(?:start|end|size|offset)|"
                                                r"(?:start|end).*(?:rodata|ext_ram)", name):
            continue
        address = int(address, 16)
        containing = [s["name"] for s in sections
                      if s["address"] <= address < s["address"] + s["bytes"]
                      and "dummy" not in s["name"]]
        result.append({"name": name, "address": address, "address_hex": hex(address),
                       "bytes": int(size, 16) if size else None, "nm_type": kind,
                       "sections_at_address": containing})
    return result


def partitions(build):
    # The generated binary is authoritative for this build, not a guessed CSV.
    path = build / "partition_table/partition-table.bin"
    result = {}
    data = path.read_bytes()
    for offset in range(0, len(data) - 31, 32):
        magic, kind, subtype, address, size, label, flags = struct.unpack_from("<HBBII16sI", data, offset)
        if magic != 0x50AA:
            break  # MD5 entry or erased padding
        name = label.rstrip(b"\0").decode("ascii")
        result[name] = {"offset": address, "bytes": size, "type": kind,
                        "subtype": subtype, "flags": flags}
    for name in ("main_app", "ui_apps", "vibe_mode"):
        if name not in result:
            raise ValueError(f"Missing {name} in built partition table")
    return path, result


def warnings_from_logs(paths):
    result = {"logs": [], "matched_warning_lines": [],
              "scope": "Only supplied build logs; matches are lines, not distinct diagnostics. "
                       "No log supplied does not mean a warning-free build."}
    pattern = re.compile(r"\bwarning\b", re.IGNORECASE)
    for path in paths:
        result["logs"].append(fingerprint(path))
        for number, line in enumerate(path.read_text(errors="replace").splitlines(), 1):
            clean = re.sub(r"\x1b\[[0-9;]*m", "", line)
            if pattern.search(clean):
                result["matched_warning_lines"].append(
                    {"log": str(path), "line": number, "text": clean})
    result["matched_line_count"] = len(result["matched_warning_lines"]) if paths else None
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build-dir", type=Path, default=ROOT / "projects/peek/build")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "evidence/followup")
    parser.add_argument("--build-log", type=Path, action="append", default=[],
                        help="Explicit IDF build log, repeatable; never scans device logs")
    parser.add_argument("--static-budget", type=Path,
                        default=ROOT / "evidence/phase2/resource-budget.json",
                        help="Existing report_budget.py result; inherited estimates are labelled")
    args = parser.parse_args()
    build, out = args.build_dir.resolve(), args.out_dir.resolve()
    compiler_files = sorted((build / "CMakeFiles").glob("*/CMakeCCompiler.cmake"))
    compilers = set()
    for path in compiler_files:
        match = re.search(r'set\(CMAKE_C_COMPILER "([^"]+)"', path.read_text())
        if match:
            compilers.add(match[1])
    if len(compilers) != 1:
        raise ValueError("Expected one compiler in build CMake compiler metadata")
    compiler = Path(compilers.pop())
    if not compiler.name.endswith("-gcc"):
        raise ValueError("Expected cross GCC compiler")
    prefix = compiler.name[:-3]
    nm, readelf = compiler.with_name(prefix + "nm"), compiler.with_name(prefix + "readelf")
    files = {name: build / name for name in ("peek.bin", "ui_apps.bin", "peek.elf", "peek.map", "sdkconfig")}
    description=json.loads((build/'project_description.json').read_text())
    files['sdkconfig']=Path(description['config_file'])
    artifacts = {name: fingerprint(path) for name, path in files.items()}
    config = read_config(files["sdkconfig"])
    sections = read_sections(readelf, files["peek.elf"])
    symbols = read_symbols(nm, files["peek.elf"], sections)
    assets = [symbol for symbol in symbols if symbol["name"] in ASSETS]
    required=ASSETS-{"dragon_sin_q15"} # Legacy generated table is now unused and can be link-stripped.
    if not required.issubset({symbol["name"] for symbol in assets}):
        raise ValueError("Required dragon texture/palette/LUT symbols are missing")
    if any(symbol["bytes"] is None for symbol in assets):
        raise ValueError("Dragon asset symbols have no nm size")
    partition_path, table = partitions(build)
    artifacts["partition-table.bin"] = fingerprint(partition_path)
    ota, ui, factory = (table[name]["bytes"] for name in ("main_app", "ui_apps", "vibe_mode"))
    fits_ota = artifacts["peek.bin"]["bytes"] <= ota
    fits_ui = artifacts["ui_apps.bin"]["bytes"] <= ui
    map_text = files["peek.map"].read_text(errors="replace")
    map_sections = {name: {"address": int(address, 16), "bytes": int(size, 16)}
                    for name, address, size in re.findall(
                        r"(?m)^(\.\S+)\s+(0x[0-9a-fA-F]+)\s+(0x[0-9a-fA-F]+)", map_text)}
    for section in sections:
        if section["name"] in (".flash.text", ".flash.rodata", ".ext_ram.bss"):
            mapped = map_sections.get(section["name"])
            if mapped != {"address": section["address"], "bytes": section["bytes"]}:
                raise ValueError(f"ELF/map section mismatch: {section['name']}")
    map_lines = map_text.splitlines()
    selected_map = []
    for index, line in enumerate(map_lines):
        if (re.match(r"^\.(?:flash|ext_ram|dram0|iram0|rtc|noinit)", line)
                or re.search(r"\b_(?:rodata|instruction|ext_ram)[A-Za-z0-9_]*\s*=", line)
                or re.match(r"\s+\.rodata\.dragon_", line)):
            selected_map.append(line)
            if index + 1 < len(map_lines) and not re.search(r"0x[0-9a-fA-F]+", line):
                selected_map.append(map_lines[index + 1])
    xip = config.get("CONFIG_SPIRAM_XIP_FROM_PSRAM") == "y"
    rodata = config.get("CONFIG_SPIRAM_RODATA") == "y"
    fetch = config.get("CONFIG_SPIRAM_FETCH_INSTRUCTIONS") == "y"
    by_name = {symbol["name"]: symbol for symbol in symbols}

    def span(start, end):
        if start in by_name and end in by_name:
            return by_name[end]["address"] - by_name[start]["address"]
        return None

    report = {
        "schema_version": 1,
        "scope": "Read-only inspection of existing local artifacts. No build, flash, installation or device measurement.",
        "toolchain": {"compiler": str(compiler), "compiler_version": run([compiler, "--version"]).splitlines()[0],
                      "readelf": str(readelf), "nm": str(nm)},
        "artifacts": artifacts,
        "final_sdkconfig_allowlisted": config,
        "flash": {"partitions_from_built_binary": table, "ui_apps_partition_bytes": ui,
                  "ui_apps_partition_is_1MiB": ui == 0x100000,
                  "ui_apps_free_bytes": ui - artifacts["ui_apps.bin"]["bytes"],
                  "normal_app_fits_main_app": fits_ota, "main_app_partition_bytes": ota,
                  "main_app_free_bytes": ota - artifacts["peek.bin"]["bytes"],
                  "retained_vibe_mode_partition_bytes": factory,
                  "normal_app_fits_retained_vibe_mode": artifacts["peek.bin"]["bytes"] <= factory,
                  "retained_vibe_mode_note": "Normal app targets main_app/ota_0; the retained vibe_mode/test image is separate. "
                                              "This tool does not change partitions or authorize flashing.",
                  "indexed_textures_palettes_LUT_bytes_in_app": sum(s["bytes"] for s in assets),
                  "texture_cost_is_included_in_peek_bin": True},
        "elf_allocated_sections": sections,
        "elf_map_memory_sections_match": True,
        "memory_symbols": symbols,
        "dragon_asset_symbols": assets,
        "psram": {
            "xip_from_psram_enabled": xip, "rodata_to_psram_enabled": rodata,
            "instruction_fetch_from_psram_enabled": fetch,
            "dragon_assets_all_in_flash_rodata": all(".flash.rodata" in s["sections_at_address"] for s in assets),
            "linker_rodata_reserved_span_bytes": span("_rodata_reserved_start", "_rodata_reserved_end"),
            "linker_instruction_reserved_span_bytes": span("_instruction_reserved_start", "_instruction_reserved_end"),
            "interpretation": "ELF section names beginning .flash describe linked image segments, not proof of flash-only runtime residency. "
                              "If CONFIG_SPIRAM_RODATA and XIP are enabled, the configured boot path requires PSRAM mapping/copy "
                              "budget for linked read-only textures/LUTs; instruction fetch configuration similarly requires code budget. "
                              "These are configuration/linker deductions; successful startup, actual residency and free heap were not observed. "
                              "Linker spans include alignment/reservations and are not measured heap consumption. "
                              "Zero texture decoding allocation does not mean zero PSRAM cost.",
            "startup_free_heap_measured": False, "device_peak_RAM_measured": False,
            "additional_not_measured": ["startup segment copying and MMU/alignment overhead",
                                        "GSP caches, Canvas surfaces, fonts and scratch",
                                        "presenter/DMA/framebuffers and task/SDK allocation overlaps"],
        },
        "build_warnings": warnings_from_logs([p.resolve() for p in args.build_log]),
    }
    if args.static_budget.exists():
        prior = json.loads(args.static_budget.read_text())
        report["prior_static_RAM_estimate"] = {
            "source": fingerprint(args.static_budget.resolve()),
            "status": "Inherited report_budget.py estimate; not recompiled or device-measured by this read-only tool. "
                      "texture_decode_to_RAM_bytes excludes XIP read-only residency and must not be used as total PSRAM usage.",
            "ram_static_estimate": prior.get("ram_static_estimate"),
        }
    out.mkdir(parents=True, exist_ok=True)
    (out / "sdkconfig-memory.txt").write_text(
        "# Allowlisted final build/sdkconfig selectors; full config intentionally omitted.\n" +
        "\n".join(f"{key}={value}" for key, value in sorted(config.items())) + "\n")
    summary = ["# Existing ELF/map memory summary (bytes; not measured runtime RAM)",
               "# ELF/map/sdkconfig SHA-256 and sizes are in firmware-budget.json.",
               "# .flash.rodata names do not imply flash-only runtime residency with PSRAM XIP."]
    summary += [f"{s['name']}: address={s['address_hex']} bytes={s['bytes']} type={s['type']} flags={s['flags']}"
                for s in sections]
    summary += ["", "# Dragon textures/palettes/LUTs (local static symbols included by nm -a -S)"]
    summary += [f"{s['name']}: address={s['address_hex']} bytes={s['bytes']} sections={','.join(s['sections_at_address'])}"
                for s in assets]
    summary += ["", "# Selected actual linker map lines", *selected_map]
    (out / "map-summary.txt").write_text("\n".join(summary) + "\n")
    (out / "firmware-budget.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"report": str(out / "firmware-budget.json"),
                      "peek_bin_bytes": artifacts["peek.bin"]["bytes"],
                      "ui_apps_bin_bytes": artifacts["ui_apps.bin"]["bytes"],
                      "dragon_asset_bytes": report["flash"]["indexed_textures_palettes_LUT_bytes_in_app"],
                      "fits_ota_0": fits_ota, "fits_ui_apps": fits_ui,
                      "xip_from_psram": xip, "rodata_to_psram": rodata}, indent=2))
    if not fits_ota or not fits_ui:
        raise SystemExit("Image exceeds actual built partition capacity; report retained")


if __name__ == "__main__":
    main()
