"""
Browse routes for browser agent
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import base64

router = APIRouter(prefix="/api/v1", tags=["browse"])


class BrowseRequest(BaseModel):
    url: str
    action: str = "content"  # content | screenshot | html | click | type
    selector: Optional[str] = None
    text: Optional[str] = None
    wait_for: Optional[str] = None


class BrowseResponse(BaseModel):
    url: str
    status: str
    content: Optional[str] = None
    screenshot: Optional[str] = None
    title: Optional[str] = None


@router.post("/browse", response_model=BrowseResponse)
async def browse(request: BrowseRequest):
    """
    Browse URL and perform action
    
    Actions:
    - content: Get page content (text)
    - screenshot: Get base64 screenshot
    - html: Get raw HTML
    - click: Click element by selector
    - type: Type text into element
    """
    from .browser import get_browser
    
    try:
        browser = await get_browser()
        page = await browser.get_page()
        
        try:
            # Navigate to URL
            await page.goto(request.url, wait_until="domcontentloaded", timeout=30000)
            
            result = BrowseResponse(url=request.url, status="success")
            
            if request.action == "content":
                result.content = await page.text_content("body")
                result.title = await page.title()
            
            elif request.action == "screenshot":
                result.screenshot = base64.b64encode(
                    await page.screenshot(full_page=False)
                ).decode()
            
            elif request.action == "html":
                result.content = await page.content()
            
            elif request.action == "click" and request.selector:
                await page.click(request.selector, timeout=10000)
                result.status = "clicked"
            
            elif request.action == "type" and request.selector and request.text:
                await page.fill(request.selector, request.text)
                result.status = "typed"
            
            else:
                raise HTTPException(400, f"Invalid action or missing selector")
            
            return result
        
        finally:
            await page.context.close()
    
    except Exception as e:
        raise HTTPException(500, str(e))


@router.post("/click")
async def click(url: str, selector: str):
    """Click element on page"""
    from .browser import get_browser
    
    try:
        browser = await get_browser()
        page = await browser.get_page()
        
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await page.click(selector, timeout=10000)
            return {"status": "success", "url": url, "clicked": selector}
        finally:
            await page.context.close()
    
    except Exception as e:
        raise HTTPException(500, str(e))


@router.post("/type")
async def type_text(url: str, selector: str, text: str):
    """Type text into element"""
    from .browser import get_browser
    
    try:
        browser = await get_browser()
        page = await browser.get_page()
        
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await page.fill(selector, text)
            return {"status": "success", "url": url, "selector": selector, "text": text}
        finally:
            await page.context.close()
    
    except Exception as e:
        raise HTTPException(500, str(e))
