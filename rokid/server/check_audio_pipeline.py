"""Opt-in live-model checks. Use synthetic audio and a separate smoke-test database."""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
sys.path.insert(0,str(PROJECT))

from dotenv import load_dotenv
from server.audio_models import GeminiExtractor, WhisperTranscriber
from server.audio_preferences import PreferenceService, decode_wav
from server.preference_store import PreferenceStore


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage",choices=("whisper","gemini","full"),required=True)
    parser.add_argument("--audio",type=Path)
    parser.add_argument("--guest",default="POC Test Guest")
    parser.add_argument("--db",type=Path,default=PROJECT/".artifacts"/"audio-preferences"/"smoke.sqlite3")
    args=parser.parse_args()
    load_dotenv(PROJECT/"server"/".env",override=False)
    transcript="Our guest prefers black coffee with no milk and no sugar. The guest also prefers a room with a view."
    if args.stage in ("whisper","full") and args.audio is None: parser.error("--audio is required")
    if args.stage=="whisper":
        model=WhisperTranscriber(); model.load(); started=time.perf_counter()
        text=model.transcribe(decode_wav(args.audio.read_bytes()))
        print(json.dumps({"stage":"whisper","model":model.model_name,"transcript":text,"processing_ms":round((time.perf_counter()-started)*1000)},ensure_ascii=False))
    else:
        extractor=GeminiExtractor()
        if not extractor.configured: parser.error("Configure GEMINI_API_KEY in server/.env first")
        try:
            if args.stage=="gemini":
                preferences=extractor.extract(transcript,args.guest)
                assert {p["key"] for p in preferences} >= {"coffee","room_view"}, "Expected test preferences missing"
                print(json.dumps({"stage":"gemini","model":extractor.model_name,"preferences":preferences},ensure_ascii=False))
            else:
                import uuid
                service=PreferenceService(PreferenceStore(args.db),extractor=extractor)
                token=service.bindings.issue(args.guest)["token"]
                result=service.process(args.audio.read_bytes(),token,str(uuid.uuid4()))
                assert result["saved_count"] >= 2, "Expected test preferences missing"
                assert len(service.store.guests()) >= 1
                print(json.dumps({"stage":"full","database":str(args.db),**result},ensure_ascii=False))
        except Exception as error:
            # SDK exception messages can include request metadata. Report only type and numeric status.
            print(json.dumps({"stage":args.stage,"error_type":type(error).__name__,"provider_code":getattr(error,"code",None)}),file=sys.stderr)
            return 1
        finally: extractor.close()
    return 0


if __name__=="__main__": raise SystemExit(main())
