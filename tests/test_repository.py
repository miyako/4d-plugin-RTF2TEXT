"""Raw-byte and POSIX-mode checks stay independent of Git's stat cache."""

from unittest.mock import patch

from helper_support import GitFixture, cwd
import repository


class RepositoryTests(GitFixture):
    def test_windows_only_executable_bit_compatibility_still_checks_raw_bytes_and_index(self):
        relative = ".github/hooks/pre-push"
        target = self.local / relative
        expected = repository.actual_blob(target)
        self.assertEqual(expected[0], "100755")
        real_blob = repository.actual_blob

        def windows_blob(path):
            mode, oid = real_blob(path)
            return ("100644" if mode == "100755" else mode), oid

        with cwd(self.local), patch.object(repository, "actual_blob", side_effect=windows_blob):
            with self.assertRaisesRegex(ValueError, "Working source"):
                repository.verify_checkout(self.sha)
            with patch.object(repository, "WINDOWS", True):
                repository.verify_checkout(self.sha)
                target.write_bytes(target.read_bytes() + b"# raw mutation\n")
                with self.assertRaisesRegex(ValueError, "Working source"):
                    repository.verify_checkout(self.sha)
