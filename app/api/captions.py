from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.core.security import verify_token
import google.generativeai as genai
from app.core.config import settings
import json

router = APIRouter()

# Configure Gemini
genai.configure(api_key=settings.GEMINI_API_KEY)

class CaptionRequest(BaseModel):
    imageBase64: str
    imageType: str = "image/jpeg"

class CaptionResponse(BaseModel):
    captions: list[str]
    count: int
    fallback: bool = False
    message: str = ""

@router.post("/generate", response_model=CaptionResponse)
async def generate_captions(
    request: CaptionRequest,
    current_user: dict = Depends(verify_token)
):
    try:
        if not request.imageBase64:
            raise HTTPException(status_code=400, detail="Image data is required")
        
        print("🎨 Generating captions using Google Gemini...")
        
        prompt = """Analyze this image carefully and generate 5 diverse, engaging captions suitable for a university social networking post (like LinkedIn or Instagram for students/alumni).

Requirements for each caption:
1. Professional yet friendly tone (suitable for students and alumni)
2. Varied styles: mix of professional, casual, inspirational, humorous, and thoughtful
3. Between 10-25 words each
4. Include relevant emojis where appropriate
5. Capture different aspects or interpretations of what's shown in the image
6. Make them creative and engaging - not generic

Consider the context, mood, setting, activities, people, objects, and overall message of the image.

IMPORTANT: Return ONLY a valid JSON array of exactly 5 caption strings. No additional text, explanations, or markdown formatting.

Format example:
["Professional caption about the achievement shown 🎓", "Casual friendly caption about the moment 😊", "Inspirational caption about growth 🌟", "Light humorous take on the situation 😄", "Thoughtful reflective caption 💭"]"""
        
        # Create model
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Prepare image
        import base64
        image_data = base64.b64decode(request.imageBase64)
        
        # Generate content
        response = model.generate_content([
            prompt,
            {"mime_type": request.imageType, "data": request.imageBase64}
        ])
        
        text = response.text
        print(f"Raw Gemini response: {text}")
        
        # Parse response
        try:
            # Clean the response
            cleaned_text = text.replace("```json", "").replace("```", "").strip()
            captions = json.loads(cleaned_text)
        except json.JSONDecodeError:
            # Try to extract captions manually
            import re
            matches = re.findall(r'"([^"]{10,150})"', text)
            if matches and len(matches) >= 3:
                captions = matches[:5]
            else:
                raise ValueError("Could not parse caption suggestions")
        
        # Validate
        if not isinstance(captions, list) or len(captions) == 0:
            raise ValueError("Invalid caption format")
        
        # Ensure exactly 5 captions
        generic_captions = [
            "Making memories that matter 📸",
            "Another chapter in the journey 🚀",
            "Grateful for moments like these 🙏",
            "Creating my own path forward 💫",
            "Here's to new experiences! 🎉"
        ]
        
        while len(captions) < 5:
            captions.append(generic_captions[len(captions) % len(generic_captions)])
        
        captions = captions[:5]
        
        print(f"✅ Generated {len(captions)} captions")
        
        return {
            "captions": captions,
            "count": len(captions),
            "fallback": False,
            "message": "Captions generated successfully"
        }
        
    except Exception as e:
        print(f"❌ Error generating captions: {e}")
        
        # Fallback captions
        fallback_captions = [
            "Capturing this special moment 📸✨",
            "Making memories that last forever 🌟",
            "Here's to new adventures and experiences! 🚀",
            "Living my best life, one day at a time 💫",
            "Grateful for moments like these 🙏💛"
        ]
        
        return {
            "captions": fallback_captions,
            "count": len(fallback_captions),
            "fallback": True,
            "message": "Using fallback captions. Please check your API key."
        }