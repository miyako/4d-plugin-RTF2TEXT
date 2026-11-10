"""Selective Windows phases and real workflow PowerShell, without native tools."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import unittest
import xml.etree.ElementTree as ET

import yaml

from helper_support import Fixture, ROOT, original


PWSH = "/usr/local/bin/pwsh" if Path("/usr/local/bin/pwsh").exists() else shutil.which("pwsh")
CONTENTS = Path("RTF2TEXT.4dbase/Plugins/RTF2TEXT.bundle/Contents")
OUTPUT = CONTENTS / "Windows64/RTF2TEXT.4DX"
DLLS = ("rtfconv.dll", "cnstbl.dll", "mbctbl.dll", "sbctbl.dll")
MSBUILD = (
    'msbuild "%PRODUCT_NAME%.sln" /p:Configuration=Release /p:Platform=x64 '
    '/p:PlatformToolset=v143 /p:WindowsTargetPlatformVersion=10.0 /m'
)
WORKFLOW = ROOT / ".github/workflows/release.yml"

STUB = r'''#!PYTHON
import json, os, pathlib, sys
tool = pathlib.Path(sys.argv[0]).name
args = sys.argv[1:]
with open(os.environ["WINDOWS_LOG"], "a") as stream:
    stream.write(json.dumps([tool, *args]) + "\n")
if tool in ("python", "python3"):
    assert args[:2] == [".github/scripts/release.py", "preflight"], args
    assert args[2:] == ["--sha", os.environ["GITHUB_SHA"]], args
    assert os.environ["GH_TOKEN"] == "offline-only"
    sys.exit(9 if os.environ.get("FAIL_PREFLIGHT") else 0)
assert tool == "dumpbin", tool
assert args[:1] == ["/nologo"], args
name = pathlib.Path(args[-1]).name
if (os.environ.get("FAIL_DUMPBIN") == args[1] and
        name == os.environ.get("FAIL_DUMPBIN_IMAGE", "RTF2TEXT.4DX")):
    sys.exit(23)
if args[1] == "/headers":
    print("8664 machine (x64)" if os.environ.get("NON_X64") != name else "14C machine (x86)")
elif args[1] == "/dependents":
    if name == "RTF2TEXT.4DX":
        print("    rtfconv.dll\n    KERNEL32.dll")
    elif name == "rtfconv.dll":
        print("    mbctbl.dll")
    if os.environ.get("MISSING_IMPORT") == name:
        print("    unavailable.dll")
else:
    sys.exit("Unexpected dumpbin arguments")
'''


class WindowsTests(Fixture):
    @classmethod
    def setUpClass(cls):
        if not PWSH:
            raise RuntimeError("PowerShell is required for Windows phase regression tests")

    def setUp(self):
        super().setUp()
        self.checkout = self.root / "checkout"
        self.checkout.mkdir()
        self.tools = self.root / "tools"
        self.tools.mkdir()
        self.log = self.root / "windows.jsonl"
        for tool in ("dumpbin", "python", "python3"):
            path = self.tools / tool
            path.write_text(STUB.replace("PYTHON", sys.executable))
            path.chmod(0o755)
        self.env = {
            "PATH": str(self.tools), "HOME": str(self.root),
            "SystemRoot": str(self.root / "system"), "WINDOWS_LOG": str(self.log),
            "PRODUCT_NAME": "RTF2TEXT", "RUNTIME_DLLS": " ".join(DLLS),
            "BASE_DIR": "RTF2TEXT.4dbase", "GITHUB_SHA": "a" * 40,
            "GH_TOKEN": "offline-only", "GITHUB_REPOSITORY": "miyako/4d-plugin-RTF2TEXT",
            "PYTHONDONTWRITEBYTECODE": "1", "POWERSHELL_TELEMETRY_OPTOUT": "1",
            "DOTNET_CLI_TELEMETRY_OPTOUT": "1",
        }
        system = self.root / "system/System32"
        system.mkdir(parents=True)
        (system / "KERNEL32.dll").write_bytes(b"offline system DLL")
        for name in ("windows.ps1", "verify-windows-deps.ps1"):
            self.file(".github/scripts/" + name, (ROOT / ".github/scripts" / name).read_bytes())
        self.file(OUTPUT, b"stale committed plugin")
        self.runtime = {}
        for name in DLLS:
            data = original(str(CONTENTS / "Windows64" / name))
            self.runtime[name] = data
            self.file(CONTENTS / "Windows64" / name, data)
        self.file("Objs/Release/nested/old.obj", b"stale intermediate")
        self.protected = {}
        for relative in (
            CONTENTS / "Windows/RTF2TEXT.4DX", CONTENTS / "Windows64/RTF2TEXT.html",
            CONTENTS / "MacOS/RTF2TEXT", CONTENTS / "Resources/custom.txt",
            CONTENTS / "QuickLook/Thumbnail.png",
            "RTF2TEXT.4dbase/Plugins/Default/keep", "Default/keep",
            "RTF2TEXT.4dbase/Plugins/Other.bundle/keep", "Objs/Debug/keep",
            "4DPlugin.cpp", "lib/Windows64/rtfconv.lib",
        ):
            path = self.file(relative, b"preserved")
            self.protected[path] = path.read_bytes()

    def file(self, relative, data):
        path = self.checkout / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return path

    def calls(self):
        return [json.loads(line) for line in self.log.read_text().splitlines()] if self.log.exists() else []

    def powershell(self, script, success=True):
        # An absolute executable and a closed PATH prevent accidental access to
        # real compiler, dumpbin, publication or credential tools.
        script = ("$ErrorActionPreference = 'Stop'\n" + script +
                  "\nif (Test-Path variable:LASTEXITCODE) { exit $LASTEXITCODE }")
        result = subprocess.run(
            [PWSH, "-NoLogo", "-NoProfile", "-NonInteractive", "-Command", script],
            cwd=self.checkout, env=self.env, text=True, capture_output=True, timeout=30,
        )
        if success is True:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        elif success is False:
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        return result

    def phase(self, phase, success=True, prefix=""):
        return self.powershell(
            prefix + f"\n& ./.github/scripts/windows.ps1 -Phase {phase}", success=success,
        )

    def assert_preserved(self):
        for path, data in self.protected.items():
            self.assertEqual(path.read_bytes(), data, str(path))
        for name, data in self.runtime.items():
            self.assertEqual((self.checkout / CONTENTS / "Windows64" / name).read_bytes(), data)

    def fresh(self):
        self.file(OUTPUT, b"fresh x64 plugin")

    def test_selective_cleanup_and_canonical_existing_casing(self):
        self.phase("prepare")
        self.phase("prepare")
        self.assertFalse((self.checkout / OUTPUT).exists())
        self.assertFalse((self.checkout / "Objs/Release").exists())
        self.assert_preserved()
        self.assertFalse(any(call[0] == "dumpbin" for call in self.calls()))

    def test_fresh_output_and_exact_committed_runtime_copies(self):
        self.phase("prepare")
        self.fresh()
        self.phase("collect")
        self.phase("verify")
        stage = self.checkout / "winbin"
        self.assertEqual({p.name for p in stage.iterdir()}, {"RTF2TEXT.4DX", *DLLS})
        self.assertEqual((stage / "RTF2TEXT.4DX").read_bytes(), b"fresh x64 plugin")
        for name, data in self.runtime.items():
            self.assertEqual((stage / name).read_bytes(), data)
        headers = [Path(call[-1]).name for call in self.calls() if call[2] == "/headers"]
        self.assertEqual(set(headers), {"RTF2TEXT.4DX", *DLLS})
        self.assert_preserved()

    def test_missing_and_empty_fresh_output_cannot_fall_back_to_other_plugin(self):
        self.phase("prepare")
        self.file("unrelated/Windows64/RTF2TEXT.4DX", b"misleading candidate")
        self.phase("collect", success=False)
        self.file(OUTPUT, b"")
        self.phase("collect", success=False)
        self.assertFalse((self.checkout / "winbin").exists())

    def test_missing_and_empty_runtime_dll_are_fatal_before_copy(self):
        self.phase("prepare")
        self.fresh()
        path = self.checkout / CONTENTS / "Windows64/cnstbl.dll"
        path.unlink()
        self.phase("collect", success=False)
        self.assertFalse((self.checkout / "winbin").exists())
        path.write_bytes(b"")
        self.phase("collect", success=False)
        self.assertFalse((self.checkout / "winbin").exists())

    def test_binary_and_runtime_reparse_targets_rejected_before_deletion(self):
        outside = self.file("outside/keep", b"outside")
        for relative in (OUTPUT, CONTENTS / "Windows64/cnstbl.dll"):
            with self.subTest(relative=relative):
                path = self.checkout / relative
                data = path.read_bytes()
                path.unlink()
                path.symlink_to(outside)
                self.phase("prepare", success=False)
                self.assertEqual(outside.read_bytes(), b"outside")
                self.assertTrue((self.checkout / "Objs/Release/nested/old.obj").exists())
                path.unlink()
                path.write_bytes(data)
        self.assertEqual((self.checkout / OUTPUT).read_bytes(), b"stale committed plugin")

    def test_symlink_ancestor_rejected_without_touching_target(self):
        plugins = self.checkout / "RTF2TEXT.4dbase/Plugins"
        moved = self.checkout / "outside-plugins"
        plugins.rename(moved)
        plugins.symlink_to(moved, target_is_directory=True)
        self.phase("prepare", success=False)
        self.assertEqual((self.checkout / OUTPUT).read_bytes(), b"stale committed plugin")
        self.assertTrue((self.checkout / "Objs/Release/nested/old.obj").exists())
        self.assert_preserved()

    def test_intermediate_ancestor_nested_and_dangling_symlinks_prevalidated(self):
        outside = self.file("outside/keep", b"outside")
        for relative in ("Objs/Release/nested/link", "Objs/Release/nested/dangling"):
            with self.subTest(relative=relative):
                path = self.checkout / relative
                path.symlink_to(outside if not relative.endswith("dangling") else self.checkout / "absent")
                self.phase("prepare", success=False)
                self.assertEqual((self.checkout / OUTPUT).read_bytes(), b"stale committed plugin")
                self.assertEqual(outside.read_bytes(), b"outside")
                path.unlink()
        objs = self.checkout / "Objs"
        moved = self.checkout / "outside-objs"
        objs.rename(moved)
        objs.symlink_to(moved, target_is_directory=True)
        self.phase("prepare", success=False)
        self.assertEqual((self.checkout / OUTPUT).read_bytes(), b"stale committed plugin")
        self.assertTrue((moved / "Release/nested/old.obj").exists())

    def test_cleanup_io_error_is_fatal(self):
        self.phase("prepare", success=False, prefix=(
            "function Remove-Item { throw 'offline fixture cleanup denied' }"
        ))
        self.assertEqual((self.checkout / OUTPUT).read_bytes(), b"stale committed plugin")
        self.assertTrue((self.checkout / "Objs/Release/nested/old.obj").exists())

    def test_staging_reparse_or_unexpected_entry_is_not_overwritten(self):
        self.phase("prepare")
        self.fresh()
        outside = self.file("outside/keep", b"outside")
        entry = self.file("winbin/rtfconv.dll", b"old")
        entry.unlink()
        entry.symlink_to(outside)
        self.phase("collect", success=False)
        self.assertEqual(outside.read_bytes(), b"outside")
        entry.unlink()
        self.file("winbin/unexpected.dll", b"unknown")
        self.phase("collect", success=False)
        self.assertFalse((self.checkout / "winbin/RTF2TEXT.4DX").exists())

    def test_verify_missing_binary_or_runtime_is_fatal(self):
        self.phase("prepare")
        self.fresh()
        self.phase("collect")
        for name in ("RTF2TEXT.4DX", *DLLS):
            with self.subTest(name=name):
                path = self.checkout / "winbin" / name
                data = path.read_bytes()
                path.unlink()
                self.phase("verify", success=False)
                path.write_bytes(data)

    def test_each_runtime_image_must_be_x64_and_have_closed_imports(self):
        self.phase("prepare")
        self.fresh()
        self.phase("collect")
        for name in ("RTF2TEXT.4DX", *DLLS):
            with self.subTest(non_x64=name):
                self.env["NON_X64"] = name
                self.phase("verify", success=False)
        del self.env["NON_X64"]
        # A dynamically loaded table's imports must be checked, not just 4DX.
        self.env["MISSING_IMPORT"] = "sbctbl.dll"
        self.phase("verify", success=False)

    def test_dumpbin_failures_are_fatal(self):
        self.phase("prepare")
        self.fresh()
        self.phase("collect")
        for operation in ("/headers", "/dependents"):
            with self.subTest(operation=operation):
                self.env["FAIL_DUMPBIN"] = operation
                self.phase("verify", success=False)

    def workflow(self, *, fresh=True, empty=False, cleanup_failure=False):
        job = yaml.safe_load(WORKFLOW.read_text())["jobs"]["build-windows"]
        build_seen = False
        upload_seen = False
        for step in job["steps"]:
            if "run" in step:
                script = step["run"]
                self.assertNotIn("${{", script)
                if step.get("shell") == "cmd":
                    # The actual Windows CMD invocation is pinned verbatim.
                    # On this macOS harness only the native output is modeled;
                    # there is no invented CMD-to-PowerShell adapter.
                    self.assertEqual(script.strip(), MSBUILD)
                    self.assertFalse((self.checkout / OUTPUT).exists())
                    self.assertFalse((self.checkout / "Objs/Release").exists())
                    self.assert_preserved()
                    build_seen = True
                    if fresh:
                        self.file(OUTPUT, b"" if empty else b"fresh workflow plugin")
                    continue
                self.assertEqual(step.get("shell", "pwsh"), "pwsh")
                if cleanup_failure and "-Phase prepare" in script:
                    script = "function Remove-Item { throw 'offline denied' }\n" + script
                result = self.powershell(script, success=None)
                if result.returncode:
                    return False, build_seen, upload_seen, result
            elif step.get("uses", "").startswith("actions/upload-artifact@"):
                upload_seen = True
                self.assertTrue(build_seen)
                self.assertEqual(step["with"]["path"].rstrip("/"), "winbin")
                self.assertEqual(step["with"]["if-no-files-found"], "error")
        return True, build_seen, upload_seen, None

    def test_actual_workflow_powershell_collects_fresh_artifact(self):
        succeeded, build, upload, result = self.workflow()
        self.assertTrue(succeeded, result)
        self.assertTrue(build)
        self.assertTrue(upload)
        self.assertEqual((self.checkout / "winbin/RTF2TEXT.4DX").read_bytes(), b"fresh workflow plugin")
        for name, data in self.runtime.items():
            self.assertEqual((self.checkout / "winbin" / name).read_bytes(), data)
        self.assert_preserved()

    def test_workflow_stops_without_upload_after_preflight_or_cleanup_failure(self):
        self.env["FAIL_PREFLIGHT"] = "1"
        succeeded, build, upload, _ = self.workflow()
        self.assertFalse(succeeded)
        self.assertFalse(build)
        self.assertFalse(upload)
        del self.env["FAIL_PREFLIGHT"]
        succeeded, build, upload, _ = self.workflow(cleanup_failure=True)
        self.assertFalse(succeeded)
        self.assertFalse(build)
        self.assertFalse(upload)
        self.assertEqual((self.checkout / OUTPUT).read_bytes(), b"stale committed plugin")

    def test_workflow_missing_fresh_output_stops_without_upload(self):
        succeeded, build, upload, _ = self.workflow(fresh=False)
        self.assertFalse(succeeded)
        self.assertTrue(build)
        self.assertFalse(upload)

    def test_workflow_empty_fresh_output_stops_without_upload(self):
        succeeded, build, upload, _ = self.workflow(empty=True)
        self.assertFalse(succeeded)
        self.assertTrue(build)
        self.assertFalse(upload)

    def test_workflow_dependency_failure_stops_without_upload(self):
        self.env["MISSING_IMPORT"] = "sbctbl.dll"
        succeeded, build, upload, _ = self.workflow()
        self.assertFalse(succeeded)
        self.assertTrue(build)
        self.assertFalse(upload)

    def test_workflow_non_x64_runtime_stops_without_upload(self):
        self.env["NON_X64"] = "cnstbl.dll"
        succeeded, build, upload, _ = self.workflow()
        self.assertFalse(succeeded)
        self.assertTrue(build)
        self.assertFalse(upload)

    def test_workflow_missing_runtime_stops_without_upload(self):
        (self.checkout / CONTENTS / "Windows64/mbctbl.dll").unlink()
        # Preserve checks only apply to files that existed at native entry.
        del self.runtime["mbctbl.dll"]
        succeeded, build, upload, _ = self.workflow()
        self.assertFalse(succeeded)
        self.assertTrue(build)
        self.assertFalse(upload)


class WindowsTopologyTests(unittest.TestCase):
    def test_real_msbuild_command_solution_project_and_runtime_environment(self):
        workflow = yaml.safe_load(WORKFLOW.read_text())
        intake = yaml.safe_load(original(".github/workflows/release.yml"))
        windows = workflow["jobs"]["build-windows"]
        original_build = next(step for step in intake["jobs"]["build-windows"]["steps"]
                              if step.get("shell") == "cmd")
        build = next(step for step in windows["steps"] if step.get("shell") == "cmd")
        self.assertEqual(build, original_build)
        self.assertEqual(build["run"].strip(), MSBUILD)
        self.assertEqual(workflow["env"]["PRODUCT_NAME"], "RTF2TEXT")
        self.assertEqual(workflow["env"]["RUNTIME_DLLS"].split(), list(DLLS))
        self.assertEqual(windows["runs-on"], "windows-latest")
        self.assertIn("build-windows", workflow["jobs"]["build-macos"]["needs"])
        self.assertTrue(any(step.get("uses") == "microsoft/setup-msbuild@v2"
                            for step in windows["steps"]))
        self.assertEqual((ROOT / "RTF2TEXT.sln").read_bytes(), original("RTF2TEXT.sln"))
        self.assertEqual((ROOT / "RTF2TEXT.vcxproj").read_bytes(), original("RTF2TEXT.vcxproj"))
        solution = (ROOT / "RTF2TEXT.sln").read_text(encoding="utf-8-sig")
        self.assertIn('"RTF2TEXT", "RTF2TEXT.vcxproj"', solution)
        self.assertIn(".Release|x64.Build.0 = Release|x64", solution)
        ns = {"m": "http://schemas.microsoft.com/developer/msbuild/2003"}
        project = ET.fromstring(original("RTF2TEXT.vcxproj"))
        for element, value in (
            ("OutDir", r"$(ProjectDir)$(ProjectName).4dbase\plugins\$(ProjectName).bundle\contents\windows64\\"),
            ("IntDir", r"$(SolutionDir)Objs\$(Configuration)\\"),
            ("TargetExt", ".4DX"),
        ):
            found = [node.text for node in project.findall(f".//m:{element}", ns)
                     if node.get("Condition") == "'$(Configuration)|$(Platform)'=='Release|x64'"]
            self.assertEqual(found, [value.replace("\\\\", "\\")])
        scripts = [step["run"] for step in windows["steps"] if step.get("shell") == "pwsh"]
        phases = [phase for phase in ("prepare", "collect", "verify")
                  if any(f"windows.ps1 -Phase {phase}" in script for script in scripts)]
        self.assertEqual(phases, ["prepare", "collect", "verify"])
        topology = []
        for step in windows["steps"]:
            script = step.get("run", "")
            if "release.py preflight" in script:
                topology.append("preflight")
            elif step.get("shell") == "cmd":
                topology.append("build")
            elif "windows.ps1 -Phase " in script:
                topology.append(script.split("windows.ps1 -Phase ", 1)[1].strip())
            elif step.get("uses", "").startswith("actions/upload-artifact@"):
                topology.append("upload")
        self.assertEqual(topology, ["preflight", "prepare", "build", "collect", "verify", "upload"])
        self.assertFalse(any("windlls" in script or "Get-ChildItem -Recurse" in script
                             for script in scripts))


if __name__ == "__main__":
    unittest.main()
