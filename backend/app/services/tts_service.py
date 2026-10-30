import os
import asyncio
import logging
from typing import Dict, Any, Optional
from backend.app.config import settings

logger = logging.getLogger("TTSService")

class TTSService:
    """
    AI Voice & Audio Engine supporting multi-character dialogue,
    custom pitch/rate controls, and automatic synchronized subtitle generation.
    """
    DEFAULT_VOICES = {
        "narrator": "en-US-ChristopherNeural",
        "male_protagonist": "en-US-GuyNeural",
        "female_protagonist": "en-US-JennyNeural",
        "mysterious_voice": "en-GB-RyanNeural",
        "deep_suspense": "en-US-EricNeural"
    }

    def __init__(self):
        self.provider = settings.TTS_PROVIDER

    async def synthesize_speech(
        self,
        text: str,
        output_audio_path: str,
        output_subtitles_path: Optional[str] = None,
        voice: str = "en-US-ChristopherNeural",
        rate: str = "+0%",
        pitch: str = "+0Hz"
    ) -> Dict[str, Any]:
        """Synthesizes high-fidelity speech and creates synchronized subtitle track."""
        os.makedirs(os.path.dirname(output_audio_path), exist_ok=True)
        if output_subtitles_path:
            os.makedirs(os.path.dirname(output_subtitles_path), exist_ok=True)

        try:
            import edge_tts

            communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
            submaker = edge_tts.SubMaker()
            
            with open(output_audio_path, "wb") as audio_file:
                async for chunk in communicate.stream():
                    if chunk["type"] == "audio":
                        audio_file.write(chunk["data"])
                    elif chunk["type"] == "WordBoundary":
                        submaker.feed(chunk)

            if output_subtitles_path:
                srt_content = submaker.get_srt()
                with open(output_subtitles_path, "w", encoding="utf-8") as sub_file:
                    sub_file.write(srt_content)
                logger.info(f"Generated synchronized subtitles at {output_subtitles_path}")

            logger.info(f"Synthesized voiceover audio using {voice} at {output_audio_path}")
            return {
                "status": "success",
                "audio_path": output_audio_path,
                "subtitles_path": output_subtitles_path,
                "voice": voice,
                "provider": "edge-tts"
            }
        except Exception as e:
            logger.warning(f"edge-tts synthesis fallback: {e}. Generating silent/placeholder audio.")
            # Create a placeholder audio file
            with open(output_audio_path, "wb") as f:
                f.write(b"\xFF\xFB\x90\x00" * 200) # minimal mp3 frame header stub
            
            if output_subtitles_path:
                with open(output_subtitles_path, "w", encoding="utf-8") as f:
                    f.write("1\n00:00:00,000 --> 00:00:05,000\n" + text[:60] + "\n\n")
                    
            return {
                "status": "fallback",
                "audio_path": output_audio_path,
                "subtitles_path": output_subtitles_path,
                "voice": voice,
                "provider": "stub"
            }

tts_service = TTSService()
