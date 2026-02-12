# Manual QA Checklist: Windows Language Sync

## Preconditions
1. `whisper.language: auto`
2. `whisper.sync_with_windows_language: true`
3. Console logging enabled
4. App log enabled

## Scenarios

### 1) English layout
1. Switch layout to English.
2. Record and stop.
3. Expect sync log with `en` and successful transcription.

### 2) Hebrew layout
1. Switch layout to Hebrew.
2. Record and stop.
3. Expect sync log with `he` and successful transcription.

### 3) Detection failure fallback
1. Trigger a failure/unmapped condition.
2. Record and stop.
3. Expect fallback-to-auto log and successful transcription.

### 4) Manual override check
1. Set `whisper.language: en`.
2. Keep sync enabled.
3. Switch layout to Hebrew and transcribe.
4. Expect manual language to remain in effect.

### 5) English-only model check
1. Use an english-only model.
2. Keep `language: auto` + sync enabled.
3. Switch layout to non-English and transcribe.
4. Expect log showing english-only forcing `en`.
