import json
import logging
from typing import Dict, Any, List, Optional
from backend.app.config import settings

logger = logging.getLogger("GeminiLLM")

class GeminiLLMService:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model_name = settings.GEMINI_MODEL
        self._client = None
        if self.api_key:
            try:
                from google import genai
                self._client = genai.Client(api_key=self.api_key)
            except Exception as e:
                logger.warning(f"Google GenAI SDK initialization fallback: {e}")

    async def generate_json(self, prompt: str, system_instruction: str = "") -> Dict[str, Any]:
        """Calls Gemini with structured JSON output enforcement, or returns intelligent fallback in sandbox mode."""
        if self._client:
            try:
                full_prompt = f"{system_instruction}\n\nTask:\n{prompt}\n\nReturn strictly valid JSON only. Do not wrap in markdown or backticks."
                response = self._client.models.generate_content(
                    model=self.model_name,
                    contents=full_prompt
                )
                text = response.text.strip()
                if text.startswith("```json"):
                    text = text[7:]
                if text.startswith("```"):
                    text = text[3:]
                if text.endswith("```"):
                    text = text[:-3]
                return json.loads(text.strip())
            except Exception as e:
                logger.error(f"Gemini API generation error: {e}. Falling back to heuristic model.")

        # Heuristic intelligent mock generation for sandbox and offline testing
        return self._generate_fallback(prompt)

    def _generate_fallback(self, prompt: str) -> Dict[str, Any]:
        prompt_lower = prompt.lower()
        if "trend" in prompt_lower:
            return {
                "trends": [
                    {
                        "topic": "The 100-Year Glitch in Quantum Reality",
                        "niche": "sci-fi",
                        "source_platform": "instagram",
                        "hook_3s": "In 1924, a clock in Zurich ticked backwards once. Today, it stopped completely.",
                        "storytelling_technique": "Cold open question + Inverted chronological mystery",
                        "estimated_duration_sec": 45,
                        "editing_style": "Rapid micro-cuts, neon glitch transitions, high-contrast grading",
                        "audio_trend": "Low frequency cinematic sub-bass with ticking sound effect",
                        "engagement_indicators": "Saves 3x higher than likes, active comment theorizing",
                        "reasons_successful": "Immediate curiosity gap and existential stakes.",
                        "growth_rate": 88.5,
                        "engagement_score": 92.0,
                        "relevance_score": 94.0,
                        "competition_score": 38.0,
                        "reusability_score": 96.0,
                        "virality_score": 91.5
                    },
                    {
                        "topic": "Unsolved Deep Ocean Radio Bursts",
                        "niche": "suspense",
                        "source_platform": "youtube",
                        "hook_3s": "Submarines keep detecting an SOS from 30,000 feet below sea level. But there are no ships down there.",
                        "storytelling_technique": "Found-footage classified document format",
                        "estimated_duration_sec": 50,
                        "editing_style": "CRT monitor overlay, sonar pulse visualizer, dark ocean palettes",
                        "audio_trend": "Eerie hydrophone recordings and muffled sonar ping",
                        "engagement_indicators": "High completion rate (82%), shared across Discord/Reddit",
                        "reasons_successful": "Deep sea thalassophobia combined with unexplained audio.",
                        "growth_rate": 84.0,
                        "engagement_score": 89.0,
                        "relevance_score": 90.0,
                        "competition_score": 42.0,
                        "reusability_score": 93.0,
                        "virality_score": 87.5
                    }
                ]
            }
        elif "script" in prompt_lower or "episode" in prompt_lower:
            return {
                "series_name": "Project Chronos: The Stolen Timelines",
                "episode_number": 1,
                "title": "The Backward Tick",
                "synopsis": "Dr. Aris Vance discovers that an antique brass clock in the Geneva vault contains atomic gears made of an alloy that does not exist in our periodic table.",
                "hook_3s": "If your watch ticks backwards today, do not look in the mirror.",
                "cliffhanger": "Aris shines the UV light on the gear: stamped onto the microscopic metal is tomorrow's date.",
                "full_script": "If your watch ticks backwards today, do not look in the mirror. Dr. Aris Vance thought the alarm at the Geneva subterranean archive was a glitch. When he reached Vault 9, the air pressure had plummeted to freezing. Sitting on the pedestal was an unmarked chronometer ticking counter-clockwise. Every tick erased one line of text from the paper in his hands. He grabbed the emergency radio, but the voice that answered was his own. And then he shined his UV light onto the central gear...",
                "scenes": [
                    {
                        "scene_number": 1,
                        "scene_description": "Extreme close-up of a vintage brass mechanical pocket watch in vertical framing. The second hand suddenly jerks counter-clockwise with a metallic click.",
                        "camera_angle": "Macro lens, 45-degree angled top-down shot with shallow depth of field",
                        "character_name": "Dr. Aris Vance",
                        "character_actions": "Gloved fingers trembling as he holds the antique watch",
                        "dialogue": "If your watch ticks backwards today, do not look in the mirror.",
                        "environment": "Cold, sterile underground concrete research vault",
                        "lighting": "Dramatic blue-cyan volumetric rim lighting with amber reflections on brass",
                        "visual_style": "Hyper-realistic cinematic 8K, 9:16 vertical composition, anamorphic bokeh",
                        "sound_effects": "Heavy mechanical reverse tick, air decompressing hiss",
                        "duration_seconds": 6.0,
                        "veo_prompt": "Cinematic vertical 9:16 macro shot of a brass vintage chronometer whose second hand ticks backwards with mechanical precision. Trembling gloved hand holds it under moody cyan laboratory lighting, photorealistic 8k, shallow depth of field."
                    },
                    {
                        "scene_number": 2,
                        "scene_description": "Dr. Vance looks up into the shadowy corridor of Vault 9. Frost patterns rapidly spread across the stainless steel vault door.",
                        "camera_angle": "Low-angle medium shot pushing slowly towards the character",
                        "character_name": "Dr. Aris Vance",
                        "character_actions": "Exhales a cloud of frozen breath, eyes wide in disbelief",
                        "dialogue": "Dr. Aris Vance thought the alarm was a routine glitch. Until the air turned to ice.",
                        "environment": "Dim subterranean hallway lined with secure server racks and heavy vault doors",
                        "lighting": "Flashing amber emergency beacon light casting long dancing shadows",
                        "visual_style": "High-suspense cinematic thriller, atmospheric fog and condensation",
                        "sound_effects": "Low sub-bass drone, metallic ice cracking sounds",
                        "duration_seconds": 7.0,
                        "veo_prompt": "Cinematic vertical 9:16 low angle shot of a scientist in high-tech jacket exhaling visible breath in a freezing high-security vault corridor. Frost rapidly crystallizes on steel walls, amber warning lights flashing, suspenseful atmospheric realism."
                    },
                    {
                        "scene_number": 3,
                        "scene_description": "Vance shines a purple ultraviolet flashlight onto the inner gears of the watch. Glowing engraved numbers illuminate.",
                        "camera_angle": "Dutch angle over-the-shoulder macro view",
                        "character_name": "Dr. Aris Vance",
                        "character_actions": "Clicking on UV pen light and leaning in close",
                        "dialogue": "He turned on the UV scanner. Stamped onto the microscopic titanium gear... was tomorrow's date.",
                        "environment": "Pitch black vault, illuminated only by intense violet UV beam",
                        "lighting": "Fluorescent UV neon glow contrasting with deep black shadows",
                        "visual_style": "Sci-fi mystery aesthetic, sharp optical clarity",
                        "sound_effects": "High pitch electrical whine, dramatic sudden cliffhanger chord",
                        "duration_seconds": 7.0,
                        "veo_prompt": "Vertical 9:16 cinematic close-up of a purple ultraviolet light illuminating glowing numbers engraved on an intricate titanium gear inside an open mechanical device. Futuristic suspense, 8k resolution, razor sharp focus."
                    }
                ],
                "caption": "Would you keep holding the watch? ⏳ The Geneva anomaly has officially begun. Episode 1 of Chronos.",
                "hashtags": "#SciFiShorts #MysterySeries #TimeTravel #Suspense #AIStories #ReelsViral"
            }
        return {"result": "success", "data": "Generated structured concept"}

gemini_service = GeminiLLMService()
