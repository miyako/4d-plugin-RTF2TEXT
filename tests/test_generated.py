"""The final publication exemption is smaller than the bundle or build roots."""

import unittest

from helper_support import source
import native


class GeneratedOutputTests(unittest.TestCase):
    def test_exact_native_files_and_controlled_directory_descendants(self):
        expected = (
            "RTF2TEXT.4dbase/Plugins/RTF2TEXT.bundle/Contents/MacOS/RTF2TEXT",
            "RTF2TEXT.4dbase/Plugins/RTF2TEXT.bundle/Contents/Info.plist",
            "RTF2TEXT.4dbase/Plugins/RTF2TEXT.bundle/Contents/Resources/English.lproj/InfoPlist.strings",
            "RTF2TEXT.4dbase/Plugins/RTF2TEXT.bundle/Contents/_CodeSignature/CodeResources",
            "RTF2TEXT.4dbase/Plugins/RTF2TEXT.bundle/Contents/Resources/constants.xlf",
            "RTF2TEXT.4dbase/Plugins/RTF2TEXT.bundle/Contents/Resources/manifest.json",
            "build/XCBuildData/build.db",
            "build/XCBuildData/build.db-wal",
            "build/XCBuildData/build.db-shm",
            "build/XCBuildData/0123456789abcdef0123456789abcdef.xcbuilddata/build-request.json",
            "build/RTF2TEXT.build/Objects-normal/arm64/main.o",
            "build/Default/RTF2TEXT.build/build.db",
            "RTF2TEXT.4dbase/Plugins/RTF2TEXT.build/Objects/file.o",
            "RTF2TEXT.4dbase/Plugins/Default/RTF2TEXT.build/Objects/file.o",
            "RTF2TEXT.4dbase/Plugins/RTF2TEXT.bundle/Contents/Windows64/RTF2TEXT.4DX",
            *(str(path) for path in native.DOWNLOADS),
        )
        for path in expected:
            with self.subTest(path=path):
                self.assertTrue(native.generated(path))

    def test_every_resource_source_or_unproven_output_stays_protected(self):
        excluded = (
            "RTF2TEXT.4dbase/Plugins/RTF2TEXT.bundle/Contents/Windows/RTF2TEXT.4DX",
            "RTF2TEXT.4dbase/Plugins/RTF2TEXT.bundle/Contents/MacOS/runtime.dylib",
            "RTF2TEXT.4dbase/Plugins/RTF2TEXT.bundle/Contents/QuickLook/Thumbnail.png",
            "RTF2TEXT.4dbase/Plugins/Default/RTF2TEXT.bundle/Contents/Info.plist",
            "RTF2TEXT.4dbase/Plugins/Default/keep", "build/XCBuildData-evil/build.db",
            "build/unexpected-source.cpp",
            "build/XCBuildData/unexpected-source.cpp",
            "build/XCBuildData/build.db-evil",
            "build/XCBuildData/evil.xcbuilddata/build-request.json",
            "build/RTF2TEXT.build-evil/injected.cpp",
            "RTF2TEXT.4dbase/Plugins/RTF2TEXT.bundle/Contents/_CodeSignature-evil/file",
            "RTF2TEXT.4dbase/Plugins/RTF2TEXT.bundle/Contents/Info.plist.backup",
            *map(str, source.SOURCE_PATHS),
        )
        for path in excluded:
            with self.subTest(path=path):
                self.assertFalse(native.generated(path))
