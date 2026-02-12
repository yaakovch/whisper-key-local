import importlib.util
import pathlib
import unittest
from unittest import mock


def load_windows_language_module():
    project_root = pathlib.Path(__file__).resolve().parents[1]
    module_path = project_root / "src" / "whisper_key" / "platform" / "windows" / "language.py"
    spec = importlib.util.spec_from_file_location("whisper_key_windows_language_test", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class WindowsLanguageDetectionTests(unittest.TestCase):
    def setUp(self):
        self.language_module = load_windows_language_module()

    def test_map_langid_to_whisper_english_and_hebrew(self):
        self.assertEqual(self.language_module.map_langid_to_whisper(0x0409), "en")
        self.assertEqual(self.language_module.map_langid_to_whisper(0x040D), "he")

    def test_map_langid_to_whisper_primary_fallback(self):
        self.assertEqual(self.language_module.map_langid_to_whisper(0xF00D), "he")

    def test_map_langid_to_whisper_unknown_returns_none(self):
        self.assertIsNone(self.language_module.map_langid_to_whisper(0xFFFF))

    def test_detect_foreground_window_language_success(self):
        fake_win32gui = mock.Mock()
        fake_win32process = mock.Mock()
        fake_win32api = mock.Mock()

        fake_win32gui.GetForegroundWindow.return_value = 123
        fake_win32process.GetWindowThreadProcessId.return_value = (321, 999)
        fake_win32api.GetKeyboardLayout.return_value = 0x040D

        with mock.patch.object(self.language_module.platform, "system", return_value="Windows"), \
             mock.patch.object(self.language_module, "WIN32_MODULES_AVAILABLE", True), \
             mock.patch.object(self.language_module, "win32gui", fake_win32gui), \
             mock.patch.object(self.language_module, "win32process", fake_win32process), \
             mock.patch.object(self.language_module, "win32api", fake_win32api):
            result = self.language_module.detect_foreground_window_language()

        self.assertTrue(result.success)
        self.assertEqual(result.language_code, "he")
        self.assertEqual(result.lang_id, 0x040D)
        self.assertEqual(result.reason, "ok")

    def test_detect_foreground_window_language_fallback_no_window(self):
        fake_win32gui = mock.Mock()
        fake_win32process = mock.Mock()
        fake_win32api = mock.Mock()

        fake_win32gui.GetForegroundWindow.return_value = 0

        with mock.patch.object(self.language_module.platform, "system", return_value="Windows"), \
             mock.patch.object(self.language_module, "WIN32_MODULES_AVAILABLE", True), \
             mock.patch.object(self.language_module, "win32gui", fake_win32gui), \
             mock.patch.object(self.language_module, "win32process", fake_win32process), \
             mock.patch.object(self.language_module, "win32api", fake_win32api):
            result = self.language_module.detect_foreground_window_language()

        self.assertFalse(result.success)
        self.assertEqual(result.reason, "no_foreground_window")
        self.assertIsNone(result.language_code)

    def test_detect_foreground_window_language_fallback_unmapped(self):
        fake_win32gui = mock.Mock()
        fake_win32process = mock.Mock()
        fake_win32api = mock.Mock()

        fake_win32gui.GetForegroundWindow.return_value = 123
        fake_win32process.GetWindowThreadProcessId.return_value = (321, 999)
        fake_win32api.GetKeyboardLayout.return_value = 0xFFFF

        with mock.patch.object(self.language_module.platform, "system", return_value="Windows"), \
             mock.patch.object(self.language_module, "WIN32_MODULES_AVAILABLE", True), \
             mock.patch.object(self.language_module, "win32gui", fake_win32gui), \
             mock.patch.object(self.language_module, "win32process", fake_win32process), \
             mock.patch.object(self.language_module, "win32api", fake_win32api):
            result = self.language_module.detect_foreground_window_language()

        self.assertFalse(result.success)
        self.assertEqual(result.reason, "unmapped_langid")
        self.assertEqual(result.lang_id, 0xFFFF)


if __name__ == "__main__":
    unittest.main()
