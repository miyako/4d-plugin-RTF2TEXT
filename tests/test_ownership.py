"""Actual first-party sources and full unchanged SDK; no native release target."""

import os
from pathlib import Path
import platform
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
BASELINE = "c669cd5c1ea4e90dd854fe794a324b4533f11472"
PICTURE = "4D Plugin API/Classes/C_PICTURE.cpp"


@unittest.skipUnless(platform.system() == "Darwin", "native Cocoa shim requires macOS")
class OwnershipTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix="rtf2text-ownership-")
        cls.addClassCleanup(cls.temp.cleanup)
        out = Path(cls.temp.name)
        original = out / "C_PICTURE.cpp"
        original.write_bytes(subprocess.check_output(
            ["git", "show", f"{BASELINE}:{PICTURE}"], cwd=ROOT))
        sdk = "4D Plugin API/4DPluginAPI.c"
        if subprocess.check_output(["git", "show", f"{BASELINE}:{sdk}"], cwd=ROOT) != (
                ROOT / sdk).read_bytes():
            raise AssertionError("Regression must use the full unchanged baseline SDK")
        common = [
            "clang++", "-std=c++11", "-x", "objective-c++", "-include", "Carbon/Carbon.h",
            "-I", str(ROOT / "4D Plugin API"),
            "-I", str(ROOT / "4D Plugin API/Classes"),
            "-fsanitize=address,undefined", "-fno-sanitize=alignment",
            "-fno-omit-frame-pointer", "-g", "-O1",
            "-Wno-deprecated-declarations", "-Wno-parentheses",
            "-framework", "Cocoa", "-framework", "Carbon",
        ]
        # Every tracked native translation unit in the plugin target, including
        # the real dispatcher and dormant wrappers, is compiled and linked.
        sources = [ROOT / sdk, ROOT / "4DPlugin.cpp", ROOT / "tests/ownership_host.mm"]
        sources += sorted(p for p in (ROOT / "4D Plugin API/Classes").glob("*.cpp")
                          if p.name != "C_PICTURE.cpp")
        cls.binaries = {}
        for version, picture in (("baseline", original), ("fixed", ROOT / PICTURE)):
            binary = out / version
            result = subprocess.run(common + [str(p) for p in sources + [picture]] +
                                    ["-o", str(binary)], capture_output=True, text=True)
            if result.returncode:
                raise AssertionError(result.stdout + result.stderr)
            cls.binaries[version] = binary

    def run_case(self, version, case, empty="allocated", outcome="success"):
        env = dict(os.environ, ASAN_OPTIONS="detect_leaks=0:halt_on_error=1",
                   UBSAN_OPTIONS="halt_on_error=1:print_stacktrace=1")
        return subprocess.run([str(self.binaries[version]), case, empty, outcome],
                              capture_output=True, text=True, env=env)

    def test_immutable_baseline_named_defects(self):
        failures = {
            "file": "double disposal or borrowed string disposal",
            "copy": "AddressSanitizer: heap-buffer-overflow",
            "gray": "picture reference balance",
            "size": "picture reference balance",
            "thumbnail": "picture reference balance",
            "bytes": "picture reference balance",
        }
        for case, message in failures.items():
            with self.subTest(case=case):
                result = self.run_case("baseline", case)
                self.assertNotEqual(result.returncode, 0, result.stdout)
                self.assertIn(message, result.stderr)

    def test_fixed_exact_content_and_balances(self):
        for case in ("file", "copy", "gray", "size", "thumbnail", "bytes", "array", "scalar",
                     "dispatcher"):
            for empty in ("allocated", "null"):
                for outcome in ("success", "failure"):
                    with self.subTest(case=case, empty=empty, outcome=outcome):
                        result = self.run_case("fixed", case, empty, outcome)
                        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                        self.assertIn("strings=0 handles=0 picture-refs=0", result.stdout)

    def test_unchanged_array_and_scalar_paths_on_baseline(self):
        for case in ("array", "scalar", "dispatcher"):
            for empty in ("allocated", "null"):
                with self.subTest(case=case, empty=empty):
                    result = self.run_case("baseline", case, empty)
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
