"""1.33: moderner Stand aus Linux AIO – gemeinsame Paletten, Zurücksetzen pro Bereich, Walker/Tofi."""
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from hyprstudio import hyprlock, kitty, launcher, packages, palettes, theme  # noqa: E402


class SharedPalettes(unittest.TestCase):
    def test_same_names_everywhere(self):
        for presets in (kitty.PRESETS, launcher.PRESETS, hyprlock.PRESETS):
            self.assertEqual(list(presets)[:len(palettes.ORDER)], list(palettes.ORDER))
        self.assertEqual(list(theme.THEMES), list(palettes.ORDER))

    def test_same_colours(self):
        for key in palettes.ORDER:
            p = palettes.PALETTES[key]
            self.assertEqual(len(p["ansi"]), 16)
            self.assertEqual(launcher.PRESETS[key]["bg"], p["bg"] + "f0")
            self.assertEqual(hyprlock.PRESETS[key]["accent"], p["accent"] + "ff")

    def test_unify_keeps_shapes_and_others(self):
        out = palettes.unify({"tokyo": {"radius": 9, "bg": "x"}, "glass": {"bg": "y"}}, lambda p: {"bg": p["bg"]})
        self.assertEqual(out["tokyo"], {"radius": 9, "bg": palettes.PALETTES["tokyo"]["bg"]})
        self.assertEqual(out["01"]["radius"], 9)        # 01 übernimmt die Form von Tokyo Night
        self.assertEqual(out["glass"], {"bg": "y"})


class NewLaunchers(unittest.TestCase):
    def test_walker_tofi(self):
        self.assertEqual(packages.PACKAGES["walker"][2]["pacman"], ["walker"])
        self.assertIn("walker", packages.UPDATE_GROUPS["launcher"])
        self.assertIn("tofi", packages.PACKAGES)


class SectionReset(unittest.TestCase):
    def test_reset_only_section(self):
        from hyprstudio import dialogs, section_reset
        from hyprstudio.qt import QtWidgets
        app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
        sec = QtWidgets.QWidget()
        lb = QtWidgets.QLabel("Rand", sec)
        lb.setProperty("skey", "border")

        class Ed:
            state = {"border": 5, "gaps": 9}
            refresh_controls = changed = lambda self: None

            class win:
                @staticmethod
                def set_status(_):
                    pass

        ed, old = Ed(), dialogs.confirm
        dialogs.confirm = lambda *a, **k: True
        with tempfile.TemporaryDirectory() as d:
            home, os.environ["HOME"] = os.environ.get("HOME"), d
            try:
                self.assertTrue(section_reset.reset(ed, sec, {"border": 2, "gaps": 5}, "Rand", "hypr-border"))
                self.assertEqual(ed.state, {"border": 2, "gaps": 9})
                self.assertTrue(list(Path(d).glob(".config/LabtosoStudios/backups/*/hypr-border.json")))
            finally:
                dialogs.confirm = old
                os.environ["HOME"] = home
        self.assertFalse(section_reset.button(lambda: None).icon().isNull())
        del app


if __name__ == "__main__":
    unittest.main()
