`synthetic-speech-16k-mono.pcm` is headerless signed little-endian 16-bit mono PCM
at 16 kHz. It was generated offline with Windows System.Speech (no microphone
recording, no playback) for the native WebRTC VAD smoke test.

Spoken text: "Hello, welcome to the restaurant. Would you like some black coffee?
We are happy to help you today."

The test verifies speech/silence wiring; it does not measure real guest speech,
background-noise accuracy, speaker attribution, or missed-utterance rate.

`synthetic-preference-16k-mono.pcm` uses the same format and offline Windows
System.Speech generation. It contains: "Our guest prefers black coffee with no
milk and no sugar. The guest also prefers a room with a view."
It is used by the opt-in server-backed preference pipeline test. It contains no
recorded microphone audio and must be used with an isolated test database.
