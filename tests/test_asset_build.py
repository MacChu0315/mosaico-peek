#!/usr/bin/env python3
"""Exercise asset generation in isolated source/build trees."""

import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

import PIL
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
APPROVED = Path("review-inputs/peek-phase2-inputs/approved-dragon")
INCLUDE_SHA256 = "e0c0a4c5c8fa4d7c2c9feb47d2e51430bb339ccd980e3067bb92e9fb32d1e3e0"


class AssetBuildTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="peek-asset-build-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / "source"
        (self.root / "tools").mkdir(parents=True)
        shutil.copy2(ROOT / "tools/bake_dragon.py", self.root / "tools")
        shutil.copytree(ROOT / "assets/dragon", self.root / "assets/dragon")
        self.output = Path(self.temporary.name) / "build/dragon_assets.inc"

    def source_state(self):
        return {str(path.relative_to(self.root)): (path.read_bytes(), path.stat().st_mtime_ns)
                for path in self.root.rglob("*") if path.is_file()}

    def run_bake(self, *arguments, pillow_version=None):
        script = self.root / "tools/bake_dragon.py"
        command = [sys.executable, str(script)]
        if pillow_version is not None:
            command = [sys.executable, "-c",
                       "import PIL,runpy,sys; from PIL import Image; "
                       "sys.argv.pop(0); PIL.__version__=sys.argv.pop(0); "
                       "runpy.run_path(sys.argv[0],run_name='__main__')",
                       pillow_version, str(script)]
        return subprocess.run(command + list(arguments), cwd=self.root,
                              text=True, capture_output=True)

    def assert_success(self, result):
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_build_ignores_originals_and_preserves_source_bytes_and_mtimes(self):
        # A normal build must never decode these original reference files.
        originals = self.root / APPROVED / "assets"
        originals.mkdir(parents=True)
        for name in ("skin", "iris"):
            (originals / f"{name}.png").write_bytes(b"unreadable original reference")
        before = self.source_state()
        self.assert_success(self.run_bake("--output", str(self.output)))
        self.assertEqual(self.source_state(), before)
        self.assertEqual(hashlib.sha256(self.output.read_bytes()).hexdigest(), INCLUDE_SHA256)
        report = self.output.with_suffix(".generation.json")
        self.assertTrue(report.is_file(), "build generation record is missing")
        generation = json.loads(report.read_text())
        self.assertEqual(generation["generated_include"]["sha256"], INCLUDE_SHA256)
        self.assertEqual(generation["generated_include"]["path"], str(self.output))
        self.assertEqual(generation["source_pillow_version"], "10.4.0")

    def test_default_output_is_in_build_tree(self):
        before = self.source_state()
        self.assert_success(self.run_bake())
        output = self.root / "build-host/dragon-generated/dragon_assets.inc"
        self.assertTrue(output.is_file(), "default include must be under the build tree")
        self.assertEqual(hashlib.sha256(output.read_bytes()).hexdigest(), INCLUDE_SHA256)
        after = {path: state for path, state in self.source_state().items()
                 if not path.startswith("build-host/")}
        self.assertEqual(after, before)

    def test_tampered_retained_png_is_rejected_without_writing(self):
        path = self.root / "assets/dragon/skin.png"
        path.write_bytes(path.read_bytes() + b"tampered")
        before = self.source_state()
        result = self.run_bake("--output", str(self.output))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("sha256", result.stderr)
        self.assertEqual(self.source_state(), before)
        self.assertFalse(self.output.exists())

    def test_tampered_provenance_is_rejected_without_writing(self):
        path = self.root / "assets/dragon/metadata.json"
        metadata = json.loads(path.read_text())
        del metadata["textures"]["skin"]["approved_source"]["sha256"]
        path.write_text(json.dumps(metadata))
        before = self.source_state()
        result = self.run_bake("--output", str(self.output))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("provenance", result.stderr.lower())
        self.assertEqual(self.source_state(), before)

    def test_include_hash_mismatch_is_rejected_without_replacing_metadata(self):
        path = self.root / "assets/dragon/metadata.json"
        metadata = json.loads(path.read_text())
        metadata["generated_include"]["sha256"] = "0" * 64
        path.write_text(json.dumps(metadata))
        before = self.source_state()
        result = self.run_bake("--output", str(self.output), pillow_version="other-version")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("sha256", result.stderr)
        self.assertEqual(self.source_state(), before)
        self.assertFalse(self.output.exists())

    def test_other_pillow_version_with_identical_bytes_preserves_provenance(self):
        before = self.source_state()
        self.assert_success(self.run_bake("--output", str(self.output),
                                          pillow_version="other-version"))
        self.assertEqual(self.source_state(), before)
        self.assertEqual(hashlib.sha256(self.output.read_bytes()).hexdigest(), INCLUDE_SHA256)
        generation = json.loads(self.output.with_suffix(".generation.json").read_text())
        self.assertEqual(generation["pillow_version"], "other-version")
        self.assertEqual(generation["source_pillow_version"], "10.4.0")

    def test_check_is_read_only_and_rejects_changed_output(self):
        self.assert_success(self.run_bake("--output", str(self.output)))
        before = self.source_state()
        include_state = (self.output.read_bytes(), self.output.stat().st_mtime_ns)
        report = self.output.with_suffix(".generation.json")
        self.assertTrue(report.is_file(), "build generation record is missing")
        report_state = (report.read_bytes(), report.stat().st_mtime_ns)
        self.assert_success(self.run_bake("--check", "--output", str(self.output)))
        self.assertEqual(self.source_state(), before)
        self.assertEqual((self.output.read_bytes(), self.output.stat().st_mtime_ns), include_state)
        self.assertEqual((report.read_bytes(), report.stat().st_mtime_ns), report_state)
        self.output.write_bytes(b"changed include")
        result = self.run_bake("--check", "--output", str(self.output))
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.output.read_bytes(), b"changed include")
        self.assertEqual(self.source_state(), before)

    def test_explicit_update_requires_originals(self):
        # Exercise missing-original validation independently of host Pillow.
        before = self.source_state()
        result = self.run_bake("--update-assets", "--output", str(self.output),
                               pillow_version="10.4.0")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("approved source", result.stderr.lower())
        self.assertEqual(self.source_state(), before)
        self.assertFalse(self.output.exists())

    def test_explicit_update_rejects_unpinned_pillow_before_writing(self):
        before = self.source_state()
        result = self.run_bake("--update-assets", "--output", str(self.output),
                               pillow_version="other-version")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("requires Pillow 10.4.0", result.stderr)
        self.assertEqual(self.source_state(), before)
        self.assertFalse(self.output.exists())

    @unittest.skipUnless(PIL.__version__ == "10.4.0", "explicit updates require pinned Pillow")
    def test_explicit_update_resizes_originals_and_records_new_provenance(self):
        originals = self.root / APPROVED / "assets"
        originals.mkdir(parents=True)
        for name in ("skin", "iris"):
            image = Image.new("RGB", (32, 32))
            image.putdata([(x * 8, y * 8, (x + y) * 4)
                           for y in range(32) for x in range(32)])
            image.save(originals / f"{name}.png")
        self.assert_success(self.run_bake("--update-assets", "--output", str(self.output)))
        metadata = json.loads((self.root / "assets/dragon/metadata.json").read_text())
        for name, size in (("skin", 480), ("iris", 640)):
            source = originals / f"{name}.png"
            description = metadata["textures"][name]
            self.assertEqual(description["approved_source"]["sha256"],
                             hashlib.sha256(source.read_bytes()).hexdigest())
            self.assertEqual(description["approved_source"]["width"], 32)
            with Image.open(self.root / f"assets/dragon/{name}.png") as image:
                self.assertEqual(image.size, (size, size))
                self.assertEqual(image.mode, "RGB")
        before = self.source_state()
        include = self.output.read_bytes()
        self.assert_success(self.run_bake("--output", str(self.output)))
        self.assertEqual(self.source_state(), before)
        self.assertEqual(self.output.read_bytes(), include)


if __name__ == "__main__":
    unittest.main()
