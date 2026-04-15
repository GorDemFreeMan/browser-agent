"""
Analyze routes - Vision integration with Qwen
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import base64
import json
import subprocess

router = APIRouter(prefix="/api/v1", tags=["analyze"])


class AnalyzeRequest(BaseModel):
    image_data: str  # base64 encoded image
    prompt: str = "Describe what you see in this image. Include any text visible."
    model: str = "qwen2.5vl:3b"


class AnalyzeResponse(BaseModel):
    analysis: str
    model: str
    prompt: str


async def analyze_with_qwen(image_b64: str, prompt: str, model: str = "qwen2.5vl:3b") -> str:
    """Analyze image using local Qwen model via Ollama"""
    
    # Prepare the curl request
    cmd = [
        "curl", "-s", "http://127.0.0.1:11434/api/generate",
        "-d", json.dumps({
            "model": model,
            "prompt": prompt,
            "images": [image_b64],
            "stream": False
        })
    ]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            response_data = json.loads(result.stdout)
            return response_data.get("response", "No response from model")
        else:
            raise Exception(f"Curl failed: {result.stderr}")
    
    except subprocess.TimeoutExpired:
        raise Exception("Vision analysis timed out")
    except Exception as e:
        raise Exception(f"Vision analysis failed: {str(e)}")


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_image(request: AnalyzeRequest):
    """
    Analyze image using Vision model (Qwen2.5-VL)
    
    The image should be base64 encoded.
    Optionally, you can also analyze a URL directly by passing url parameter.
    """
    # Validate base64
    try:
        image_bytes = base64.b64decode(request.image_data)
    except Exception as e:
        raise HTTPException(400, f"Invalid base64 image: {str(e)}")
    
    # Re-encode to ensure proper format
    image_b64 = base64.b64encode(image_bytes).decode()
    
    try:
        analysis = await analyze_with_qwen(
            image_b64=image_b64,
            prompt=request.prompt,
            model=request.model
        )
        
        return AnalyzeResponse(
            analysis=analysis,
            model=request.model,
            prompt=request.prompt
        )
    
    except Exception as e:
        raise HTTPException(500, str(e))


@router.post("/analyze-url")
async def analyze_url(url: str, prompt: str = "Describe what you see on this webpage."):
    """
    Analyze URL content by first taking screenshot then analyzing
    
    This is a convenience endpoint that combines /screenshot and /analyze
    """
    from app.browser import get_browser
    
    try:
        # First take screenshot
        browser_service = await get_browser()
        page = await browser_service.get_page()
        
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(1000)
            
            screenshot_bytes = await page.screenshot(full_page=True)
            image_b64 = base64.b64encode(screenshot_bytes).decode()
        
        finally:
            await page.context.close()
        
        # Then analyze
        analysis = await analyze_with_qwen(
            image_b64=image_b64,
            prompt=prompt
        )
        
        return {
            "url": url,
            "analysis": analysis
        }
    
    except Exception as e:
        raise HTTPException(500, str(e))
