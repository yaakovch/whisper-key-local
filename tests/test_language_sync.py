import unittest

from whisper_key.language_sync import (
    is_english_only_model,
    normalize_configured_language,
    resolve_language_override,
)


class LanguageSyncDecisionTests(unittest.TestCase):
    def test_normalize_configured_language_handles_null_as_auto(self):
        self.assertEqual(normalize_configured_language(None), "auto")

    def test_normalize_configured_language_handles_blank_as_auto(self):
        self.assertEqual(normalize_configured_language(""), "auto")

    def test_english_only_model_detection(self):
        self.assertTrue(is_english_only_model("small.en"))
        self.assertTrue(is_english_only_model("SMALL.EN"))
        self.assertFalse(is_english_only_model("small"))

    def test_manual_language_overrides_windows_sync(self):
        decision = resolve_language_override(
            configured_language="he",
            sync_with_windows_language=True,
            model_key="small",
            is_windows=True,
            detected_language="en",
            detection_reason=None
        )
        self.assertEqual(decision.language_override, "he")
        self.assertEqual(decision.source, "manual")

    def test_none_language_with_windows_sync_uses_detected_language(self):
        decision = resolve_language_override(
            configured_language=None,
            sync_with_windows_language=True,
            model_key="small",
            is_windows=True,
            detected_language="he",
            detection_reason=None
        )
        self.assertEqual(decision.language_override, "he")
        self.assertEqual(decision.source, "windows_sync")

    def test_auto_language_without_sync_uses_whisper_auto(self):
        decision = resolve_language_override(
            configured_language="auto",
            sync_with_windows_language=False,
            model_key="small",
            is_windows=True,
            detected_language="he",
            detection_reason=None
        )
        self.assertIsNone(decision.language_override)
        self.assertEqual(decision.source, "auto")

    def test_auto_language_with_windows_sync_uses_detected_language(self):
        decision = resolve_language_override(
            configured_language="auto",
            sync_with_windows_language=True,
            model_key="small",
            is_windows=True,
            detected_language="he",
            detection_reason=None
        )
        self.assertEqual(decision.language_override, "he")
        self.assertEqual(decision.source, "windows_sync")

    def test_windows_sync_falls_back_to_auto_on_detection_failure(self):
        decision = resolve_language_override(
            configured_language="auto",
            sync_with_windows_language=True,
            model_key="small",
            is_windows=True,
            detected_language=None,
            detection_reason="no_foreground_window"
        )
        self.assertIsNone(decision.language_override)
        self.assertEqual(decision.source, "windows_sync_fallback")
        self.assertEqual(decision.reason, "no_foreground_window")

    def test_english_model_forces_english_for_detected_non_english(self):
        decision = resolve_language_override(
            configured_language="auto",
            sync_with_windows_language=True,
            model_key="small.en",
            is_windows=True,
            detected_language="he",
            detection_reason=None
        )
        self.assertEqual(decision.language_override, "en")
        self.assertEqual(decision.source, "english_model_forced")
        self.assertIn("previous=he", decision.reason)

    def test_english_model_forces_english_from_auto_fallback(self):
        decision = resolve_language_override(
            configured_language="auto",
            sync_with_windows_language=True,
            model_key="small.en",
            is_windows=True,
            detected_language=None,
            detection_reason="unmapped_langid"
        )
        self.assertEqual(decision.language_override, "en")
        self.assertEqual(decision.source, "english_model_forced")
        self.assertIn("previous=auto", decision.reason)

    def test_english_model_forces_english_even_with_manual_non_english(self):
        decision = resolve_language_override(
            configured_language="he",
            sync_with_windows_language=True,
            model_key="small.en",
            is_windows=True,
            detected_language="he",
            detection_reason=None
        )
        self.assertEqual(decision.language_override, "en")
        self.assertEqual(decision.source, "english_model_forced")
        self.assertIn("previous=he", decision.reason)

    def test_english_only_hint_forces_english_for_non_en_key(self):
        decision = resolve_language_override(
            configured_language="auto",
            sync_with_windows_language=True,
            model_key="distil-large-v3.5",
            model_english_only_hint=True,
            is_windows=True,
            detected_language="he",
            detection_reason=None
        )
        self.assertEqual(decision.language_override, "en")
        self.assertEqual(decision.source, "english_model_forced")
        self.assertIn("previous=he", decision.reason)


if __name__ == "__main__":
    unittest.main()
