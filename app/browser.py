"""
Browser service with Playwright + stealth mode
"""
import asyncio
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class BrowserService:
    """Manages browser instances with stealth mode"""
    
    def __init__(self):
        self.playwright = None
        self.browser: Optional[Browser] = None
        self._initialized = False
    
    async def initialize(self):
        """Initialize playwright and browser"""
        if self._initialized:
            return
        
        logger.info("Initializing Playwright...")
        self.playwright = await async_playwright().start()
        
        # Launch with stealth settings
        self.browser = await self.playwright.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-web-security',
                '--disable-features=IsolateOrigins,site-per-process',
            ]
        )
        
        self._initialized = True
        logger.info("Browser initialized with stealth mode")
    
    async def get_context(self) -> BrowserContext:
        """Get a new browser context"""
        if not self.browser:
            await self.initialize()
        
        context = await self.browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="ru-RU",
            timezone_id="Europe/Moscow",
            extra_http_headers={
                "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8",
            }
        )
        
        # Apply stealth patches
        await self._apply_stealth(context)
        
        return context
    
    async def _apply_stealth(self, context: BrowserContext):
        """Apply stealth patches to avoid detection"""
        # Remove webdriver flag
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
                configurable: true
            });
        """)
        
        # Mock permissions
        await context.add_init_script("""
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
        """)
        
        # Mock plugins
        await context.add_init_script("""
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
                configurable: true
            });
        """)
        
        # Mock languages
        await context.add_init_script("""
            Object.defineProperty(navigator, 'languages', {
                get: () => ['ru-RU', 'ru', 'en-US', 'en'],
                configurable: true
            });
        """)
    
    async def get_page(self) -> Page:
        """Get a new page from a fresh context"""
        context = await self.get_context()
        page = await context.new_page()
        return page
    
    async def close(self):
        """Close browser and cleanup"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        self._initialized = False
        logger.info("Browser closed")


# Singleton instance
_browser_service: Optional[BrowserService] = None


async def get_browser() -> BrowserService:
    """Get or create browser service singleton"""
    global _browser_service
    if _browser_service is None:
        _browser_service = BrowserService()
        await _browser_service.initialize()
    return _browser_service
