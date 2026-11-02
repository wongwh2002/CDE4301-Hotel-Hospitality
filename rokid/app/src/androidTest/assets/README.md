`synthetic-speech-16k-mono.pcm` is headerless signed little-endian 16-bit mono PCM
at 16 kHz. It was generated offline with Windows System.Speech (no microphone
recording, no playback) for the native WebRTC VAD smoke test.

Spoken text: "Hello, welcome to the restaurant. Would you like some black coffee?
We are happy to help you today."

The test verifies speech/silence wiring; it does not measure real guest speech,
background-noise accuracy, speaker attribution, or missed-utterance rate.
