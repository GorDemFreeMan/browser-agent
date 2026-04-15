"""
Browser Agent Microservice
FastAPI + Playwright + Vision
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from typing import Optional
import base64
import asyncio

from .browser import BrowserService
from .routes import browse, screenshot, analyze

app = FastAPI(
    title="Browser Agent",
    description="Web automation microservice for OpenClaw",
    version="1.0.0"
)

# CORS for OpenClaw
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize browser service
browser_service = BrowserService()

# Include routes
app.include_router(browse.router)
app.include_router(screenshot.router)
app.include_router(analyze.router)


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "ok", "service": "browser-agent"}


@app.on_event("startup")
async def startup():
    """Initialize browser on startup"""
    await browser_service.initialize()


@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown"""
    await browser_service.close()


# Request models
class BrowseRequest(BaseModel):
    url: str
    action: str = "content"  # content | screenshot | html
    selector: Optional[str] = None
    text: Optional[str] = None
    wait_for: Optional[str] = None


class LoginRequest(BaseModel):
    url: str
    username_selector: str
    password_selector: str
    submit_selector: str
    username: str
    password: str


class AnalyzeRequest(BaseModel):
    image_data: str  # base64 encoded image
    prompt: str = "Describe what you see in this image"


# Legacy routes for backward compatibility
@app.post("/browse")
async def browse_url(request: BrowseRequest):
    """Browse URL and perform action"""
    try:
        async with browser_service.get_page() as page:
            await page.goto(request.url, wait_until="domcontentloaded", timeout=30000)
            
            if request.action == "content":
                content = await page.content()
                return {"url": request.url, "content": content[:5000]}
            
            elif request.action == "screenshot":
                screenshot = await page.screenshot()
                return {
                    "url": request.url,
                    "screenshot": base64.b64encode(screenshot).decode()
                }
            
            elif request.action == "html":
                return {"url": request.url, "html": await page.content()}
            
            else:
                raise HTTPException(400, f"Unknown action: {request.action}")
    
    except Exception as e:
        raise HTTPException(500, str(e))


@app.post("/screenshot")
async def take_screenshot(url: str, full_page: bool = False):
    """Take screenshot of URL"""
    try:
        async with browser_service.get_page() as page:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            screenshot = await page.screenshot(full_page=full_page)
            return {
                "url": url,
                "screenshot": base64.b64encode(screenshot).decode()
            }
    except Exception as e:
        raise HTTPException(500, str(e))


@app.post("/login")
async def login(request: LoginRequest):
    """Login to website"""
    try:
        async with browser_service.get_page() as page:
            await page.goto(request.url, wait_until="domcontentloaded", timeout=30000)
            
            # Fill username
            await page.fill(request.username_selector, request.username)
            
            # Fill password
            await page.fill(request.password_selector, request.password)
            
            # Click submit
            await page.click(request.submit_selector)
            
            # Wait for navigation or response
            await page.wait_for_load_state("networkidle", timeout=10000)
            
            return {
                "status": "success",
                "url": page.url,
                "title": await page.title()
            }
    except Exception as e:
        raise HTTPException(500, str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
