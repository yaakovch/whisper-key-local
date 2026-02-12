from dataclasses import dataclass
from typing import Optional


AUTO_LANGUAGE = "auto"


@dataclass(frozen=True)
class LanguageSelectionDecision:
    language_override: Optional[str]
    source: str
    reason: str


def normalize_configured_language(configured_language: Optional[str]) -> str:
    return str(configured_language or AUTO_LANGUAGE).strip().lower()


def is_english_only_model(model_key: Optional[str]) -> bool:
    if not model_key:
        return False
    return model_key.strip().lower().endswith(".en")


def resolve_language_override(configured_language: Optional[str],
                              sync_with_windows_language: bool,
                              model_key: Optional[str],
                              is_windows: bool,
                              model_english_only_hint: bool = False,
                              detected_language: Optional[str] = None,
                              detection_reason: Optional[str] = None) -> LanguageSelectionDecision:
    normalized_config = normalize_configured_language(configured_language)
    normalized_detected = detected_language.strip().lower() if detected_language else None

    if normalized_config != AUTO_LANGUAGE:
        decision = LanguageSelectionDecision(
            language_override=normalized_config,
            source="manual",
            reason=f"manual_language={normalized_config}"
        )
    elif sync_with_windows_language and is_windows:
        if normalized_detected:
            decision = LanguageSelectionDecision(
                language_override=normalized_detected,
                source="windows_sync",
                reason="windows_layout_detected"
            )
        else:
            decision = LanguageSelectionDecision(
                language_override=None,
                source="windows_sync_fallback",
                reason=detection_reason or "windows_layout_detection_failed"
            )
    else:
        decision = LanguageSelectionDecision(
            language_override=None,
            source="auto",
            reason="whisper_auto_detection"
        )

    if (model_english_only_hint or is_english_only_model(model_key)) and decision.language_override != "en":
        previous_language = decision.language_override or AUTO_LANGUAGE
        return LanguageSelectionDecision(
            language_override="en",
            source="english_model_forced",
            reason=f"model={model_key or 'unknown'} previous={previous_language}"
        )

    return decision
