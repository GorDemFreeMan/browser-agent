"""
Screenshot routes for browser agent
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import base64

router = APIRouter(prefix="/api/v1", tags=["screenshot"])


class ScreenshotRequest(BaseModel):
    url: str
    full_page: bool = False


class ScreenshotResponse(BaseModel):
    url: str
    screenshot: str  # base64
    width: int
    height: int


@router.post("/screenshot", response_model=ScreenshotResponse)
async def take_screenshot(request: ScreenshotRequest):
    """Take screenshot of URL"""
    from .browser import get_browser
    
    try:
        browser = await get_browser()
        page = await browser.get_page()
        
        try:
            await page.goto(request.url, wait_until="domcontentloaded", timeout=30000)
            
            # Wait a bit for any lazy content
            await page.wait_for_timeout(1000)
            
            screenshot_bytes = await page.screenshot(full_page=request.full_page)
            
            # Get viewport size
            viewport = page.viewport_size
            width = viewport["width"] if viewport else 1920
            height = viewport["height"] if viewport else 1080
            
            return ScreenshotResponse(
                url=request.url,
                screenshot=base64.b64encode(screenshot_bytes).decode(),
                width=width,
                height=height
            )
        
        finally:
            await page.context.close()
    
    except Exception as e:
        raise HTTPException(500, str(e))
