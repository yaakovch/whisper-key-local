import platform
from dataclasses import dataclass
from typing import Optional


try:
    import win32api
    import win32gui
    import win32process
    WIN32_MODULES_AVAILABLE = True
except Exception:  # pragma: no cover - exercised with mocks in tests
    win32api = None
    win32gui = None
    win32process = None
    WIN32_MODULES_AVAILABLE = False


# Common full LANGID variants first, then fallback to primary LANGID mapping.
EXACT_LANGID_MAP = {
    0x0409: "en",  # English (United States)
    0x0809: "en",  # English (United Kingdom)
    0x0C09: "en",  # English (Australia)
    0x1009: "en",  # English (Canada)
    0x1409: "en",  # English (New Zealand)
    0x1809: "en",  # English (Ireland)
    0x1C09: "en",  # English (South Africa)
    0x2009: "en",  # English (Jamaica)
    0x2409: "en",  # English (Caribbean)
    0x2809: "en",  # English (Belize)
    0x2C09: "en",  # English (Trinidad and Tobago)
    0x3009: "en",  # English (Zimbabwe)
    0x3409: "en",  # English (Philippines)
    0x040D: "he",  # Hebrew
    0x040A: "es",  # Spanish (Traditional Sort)
    0x080A: "es",  # Spanish (Mexico)
    0x0C0A: "es",  # Spanish (Modern Sort)
    0x100A: "es",  # Spanish (Guatemala)
    0x140A: "es",  # Spanish (Costa Rica)
    0x180A: "es",  # Spanish (Panama)
    0x1C0A: "es",  # Spanish (Dominican Republic)
    0x200A: "es",  # Spanish (Venezuela)
    0x240A: "es",  # Spanish (Colombia)
    0x280A: "es",  # Spanish (Peru)
    0x2C0A: "es",  # Spanish (Argentina)
    0x300A: "es",  # Spanish (Ecuador)
    0x340A: "es",  # Spanish (Chile)
    0x380A: "es",  # Spanish (Uruguay)
    0x3C0A: "es",  # Spanish (Paraguay)
    0x400A: "es",  # Spanish (Bolivia)
    0x440A: "es",  # Spanish (El Salvador)
    0x480A: "es",  # Spanish (Honduras)
    0x4C0A: "es",  # Spanish (Nicaragua)
    0x500A: "es",  # Spanish (Puerto Rico)
    0x040C: "fr",  # French (France)
    0x080C: "fr",  # French (Belgium)
    0x0C0C: "fr",  # French (Canada)
    0x100C: "fr",  # French (Switzerland)
    0x140C: "fr",  # French (Luxembourg)
    0x180C: "fr",  # French (Monaco)
    0x0407: "de",  # German (Germany)
    0x0807: "de",  # German (Switzerland)
    0x0C07: "de",  # German (Austria)
    0x1007: "de",  # German (Luxembourg)
    0x1407: "de",  # German (Liechtenstein)
    0x0416: "pt",  # Portuguese (Brazil)
    0x0816: "pt",  # Portuguese (Portugal)
}


PRIMARY_LANGID_MAP = {
    0x01: "ar",
    0x02: "bg",
    0x03: "ca",
    0x04: "zh",
    0x05: "cs",
    0x06: "da",
    0x07: "de",
    0x08: "el",
    0x09: "en",
    0x0A: "es",
    0x0B: "fi",
    0x0C: "fr",
    0x0D: "he",
    0x0E: "hu",
    0x0F: "is",
    0x10: "it",
    0x11: "ja",
    0x12: "ko",
    0x13: "nl",
    0x14: "no",
    0x15: "pl",
    0x16: "pt",
    0x18: "ro",
    0x19: "ru",
    0x1A: "hr",
    0x1B: "sk",
    0x1C: "sq",
    0x1D: "sv",
    0x1E: "th",
    0x1F: "tr",
    0x20: "ur",
    0x21: "id",
    0x22: "uk",
    0x23: "be",
    0x24: "sl",
    0x25: "et",
    0x26: "lv",
    0x27: "lt",
    0x2A: "vi",
    0x2B: "hy",
    0x2C: "az",
    0x2D: "eu",
    0x2F: "mk",
    0x36: "af",
    0x39: "hi",
    0x3E: "ms",
    0x3F: "kk",
    0x41: "sw",
    0x43: "uz",
    0x45: "bn",
    0x46: "pa",
    0x47: "gu",
    0x49: "ta",
    0x4A: "te",
    0x4B: "kn",
    0x4C: "ml",
    0x4E: "mr",
    0x50: "mn",
    0x52: "cy",
    0x53: "km",
    0x54: "lo",
    0x56: "gl",
    0x5B: "si",
    0x5E: "am",
    0x63: "ps",
    0x64: "tl",
    0x68: "ha",
    0x6A: "yo",
}


@dataclass(frozen=True)
class LanguageDetectionResult:
    success: bool
    language_code: Optional[str] = None
    lang_id: Optional[int] = None
    reason: str = ""
    error: Optional[str] = None

    @property
    def lang_id_hex(self) -> Optional[str]:
        if self.lang_id is None:
            return None
        return f"0x{self.lang_id:04x}"


def map_langid_to_whisper(lang_id: int) -> Optional[str]:
    if lang_id in EXACT_LANGID_MAP:
        return EXACT_LANGID_MAP[lang_id]

    primary_langid = lang_id & 0x03FF
    return PRIMARY_LANGID_MAP.get(primary_langid)


def detect_foreground_window_language() -> LanguageDetectionResult:
    if platform.system() != "Windows":
        return LanguageDetectionResult(success=False, reason="not_windows")

    if not WIN32_MODULES_AVAILABLE:
        return LanguageDetectionResult(success=False, reason="win32_modules_unavailable")

    try:
        foreground_window = win32gui.GetForegroundWindow()
        if not foreground_window:
            return LanguageDetectionResult(success=False, reason="no_foreground_window")

        thread_id, _process_id = win32process.GetWindowThreadProcessId(foreground_window)
        if not thread_id:
            return LanguageDetectionResult(success=False, reason="no_foreground_thread")

        keyboard_layout = win32api.GetKeyboardLayout(thread_id)
        if keyboard_layout is None:
            return LanguageDetectionResult(success=False, reason="no_keyboard_layout")

        lang_id = int(keyboard_layout) & 0xFFFF
        language_code = map_langid_to_whisper(lang_id)

        if language_code is None:
            return LanguageDetectionResult(
                success=False,
                lang_id=lang_id,
                reason="unmapped_langid"
            )

        return LanguageDetectionResult(
            success=True,
            language_code=language_code,
            lang_id=lang_id,
            reason="ok"
        )
    except Exception as exc:
        return LanguageDetectionResult(
            success=False,
            reason="detection_exception",
            error=str(exc)
        )
