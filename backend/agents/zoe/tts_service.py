"""
Text-to-Speech Service for ThinkLife Backend

Handles high-quality speech generation using OpenAI TTS API
"""

import logging
import base64
import os
from typing import Optional

import httpx
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class TTSService:
    """Text-to-Speech service using OpenAI TTS API"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.base_url = "https://api.openai.com/v1/audio/speech"
        self.voice = "nova"  # High-quality female voice
        self.model = "tts-1-hd"  # High-definition model
        
        if not self.api_key:
            logger.warning("OPENAI_API_KEY not found. TTS functionality will be disabled.")
    
    async def generate_speech(self, text: str) -> Optional[str]:
        """
        Generate speech audio from text
        
        Args:
            text: Text to convert to speech
            
        Returns:
            Base64 encoded audio data or None if failed
        """
        if not self.api_key:
            logger.error("TTS generation failed: No OpenAI API key configured")
            return None
            
        if not text or not text.strip():
            logger.error("TTS generation failed: Empty text provided")
            return None
            
        if len(text) > 4096:
            logger.error(f"TTS generation failed: Text too long ({len(text)} characters)")
            return None
        
        try:
            # Clean text for better speech
            clean_text = self._clean_text(text)
            
            logger.info(f"Generating TTS for text: {clean_text[:50]}{'...' if len(clean_text) > 50 else ''}")
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.base_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "input": clean_text,
                        "voice": self.voice,
                        "response_format": "mp3",
                        "speed": 1.0
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    # Convert audio bytes to base64
                    audio_bytes = response.content
                    audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
                    
                    logger.info(f"TTS generated successfully: {len(audio_bytes)} bytes")
                    return audio_base64
                else:
                    logger.error(f"OpenAI TTS API error: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"TTS generation error: {str(e)}")
            return None
    
    def _clean_text(self, text: str) -> str:
        """Clean text for better speech synthesis"""
        # Remove emojis and special characters
        import re
        
        # Remove common emojis (using Unicode code points)
        text = re.sub(r'[\U0001F31E\U0001F33B\U0001F338\U0001F60A\U0001F614\U0001F917\U0001F914\U0001F49D\U0001F389\u2728\U0001F31F\U0001F4AB\U0001F308\u2764\U0001F499\U0001F49A\U0001F49B\U0001F49C\U0001F9E1\U0001F90D\U0001F5A4]', '', text)
        
        # Remove other emoji patterns
        text = re.sub(r'[\U0001F600-\U0001F64F]', '', text)  # emoticons
        text = re.sub(r'[\U0001F300-\U0001F5FF]', '', text)  # symbols & pictographs
        text = re.sub(r'[\U0001F680-\U0001F6FF]', '', text)  # transport & map symbols
        text = re.sub(r'[\U0001F1E0-\U0001F1FF]', '', text)  # flags
        
        # Clean up extra whitespace
        text = ' '.join(text.split())
        
        return text.strip()
    
    def is_available(self) -> bool:
        """Check if TTS service is available"""
        return self.api_key is not None


# Global TTS service instance
tts_service = TTSService() 