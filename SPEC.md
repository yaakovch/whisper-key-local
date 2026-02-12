# SPEC: Windows Keyboard Layout Language Sync

## 1. Summary
Add Windows keyboard-layout-based language sync to Whisper Key so transcription language follows the active Windows input language when appropriate.

## 2. Goals
- Support Windows 10 and Windows 11.
- Detect active Windows language at the end of recording (right before transcription).
- Apply detected language only when:
  - `whisper.language == auto`
  - `whisper.sync_with_windows_language == true`
- Keep manual language fully authoritative when `whisper.language != auto`.
- Log decisions and fallbacks to both console and app log (`app.log`).
- Include broad common language coverage with explicit priority for English and Hebrew.

## 3. Non-Goals
- No tray UI language indicator in this iteration.
- No model auto-switching between multilingual and `.en` model families.
- No macOS language detection in this iteration.

## 4. Functional Requirements
1. Add config key:
   - `whisper.sync_with_windows_language: true`
2. Decision order:
   - Manual language (`!= auto`) always wins.
   - `auto` + sync off -> Whisper auto.
   - `auto` + sync on (Windows) -> detect foreground window layout and map to language.
   - Unknown/failure -> fallback to Whisper auto.
   - English-only models force `en` and log this behavior.
3. Detection timing:
   - At recording end, before transcription.
4. Platform behavior:
   - Windows: active.
   - Non-Windows: silently ignore.

## 5. Technical Design
- New module: `src/whisper_key/platform/windows/language.py`
  - Foreground window + thread keyboard layout detection.
  - LANGID -> Whisper language mapping.
  - Structured detection result for logging/fallback.
- Pipeline updates:
  - `src/whisper_key/state_manager.py`
  - `src/whisper_key/whisper_engine.py` (`language_override` support)
- Config updates:
  - `src/whisper_key/config.defaults.yaml`
  - validation in config manager.

## 6. Logging
- Log success, unknown mapping fallback, detection failure fallback, and english-only override.

## 7. Testing (Level C)
- Unit tests:
  - Rule engine behavior.
  - Mapping and fallback behavior.
- Mocked integration tests:
  - Win32 detection success/failure/unmapped.
- Manual QA checklist across Windows apps and layout switching.

## 8. Success Criteria
- Language switching works when `language=auto` and sync is enabled.
- Manual language mode unchanged.
- Fallback is safe and visible.
- English-only model behavior deterministic and logged.

## 9. Deliverables
- `SPEC.md`
- `implementation_plan.md`
- Code changes for Windows language sync
- Automated tests
- Manual QA checklist
