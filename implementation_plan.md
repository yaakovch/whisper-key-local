# Implementation Plan: Windows Keyboard Layout Language Sync

Derived from `SPEC.md`.

## Milestone 0: Git Context
1. Work in `feature/windows-language-sync`.
2. Keep `master` synced with `upstream/master`.

## Milestone 1: Config
1. Add `whisper.sync_with_windows_language` default in config.
2. Validate boolean in config validator.
3. Update README config table.

## Milestone 2: Windows Detector
1. Add `src/whisper_key/platform/windows/language.py`.
2. Implement Win32 foreground-window keyboard layout detection.
3. Add broad LANGID mapping with English/Hebrew priority.
4. Return structured result for fallback/logging.

## Milestone 3: Transcription Integration
1. Add language decision logic helper module.
2. In `state_manager`, resolve override at recording end.
3. In `whisper_engine`, support `language_override`.
4. Enforce english-only model behavior (`en` forced).

## Milestone 4: Logging
1. Log sync success (`en`/`he` etc.).
2. Log fallback reasons.
3. Log english-only model forcing behavior.

## Milestone 5: Automated Tests
1. Unit tests for rule engine and english-only behavior.
2. Mocked integration tests for Windows detector success/failure/unmapped.

## Milestone 6: Manual QA
1. Verify English layout detection.
2. Verify Hebrew layout detection.
3. Verify unknown/failure fallback.
4. Verify manual language override remains authoritative.
5. Verify english-only model force-to-`en`.

## Definition of Done
1. Feature works on Windows 10/11 with `language=auto`.
2. Manual mode unchanged.
3. Fallback safe and logged.
4. Tests passing.
