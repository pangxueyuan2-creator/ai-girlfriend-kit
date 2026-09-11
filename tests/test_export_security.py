from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from aigf.export import export_plain


class ExportSecurityTests(unittest.TestCase):
    def test_plain_export_preserves_content(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "context.txt"
            with patch("aigf.export.build_context", return_value="private context"):
                result = export_plain(dest=dest)

            self.assertEqual(result, "private context")
            self.assertEqual(dest.read_text(encoding="utf-8"), "private context")

    @unittest.skipUnless(os.name == "posix", "POSIX file modes are required")
    def test_export_is_owner_only_on_posix(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "context.txt"
            dest.write_text("old", encoding="utf-8")
            dest.chmod(0o644)

            with patch("aigf.export.build_context", return_value="private context"):
                export_plain(dest=dest)

            self.assertEqual(dest.stat().st_mode & 0o777, 0o600)

    @unittest.skipUnless(os.name == "posix", "symlink semantics vary across platforms")
    def test_export_replaces_symlink_instead_of_overwriting_target(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            victim = root / "victim.txt"
            victim.write_text("do not overwrite", encoding="utf-8")
            dest = root / "context.txt"
            dest.symlink_to(victim)

            with patch("aigf.export.build_context", return_value="private context"):
                export_plain(dest=dest)

            self.assertFalse(dest.is_symlink())
            self.assertEqual(dest.read_text(encoding="utf-8"), "private context")
            self.assertEqual(victim.read_text(encoding="utf-8"), "do not overwrite")


if __name__ == "__main__":
    unittest.main()
