import asyncio
import os
from playwright.async_api import async_playwright

async def capture():
    print("Initializing Playwright screenshot capture sequence...")
    os.makedirs("screenshots", exist_ok=True)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # Set viewport to standard high resolution desktop screen
        context = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await context.new_page()
        
        # 1. Login Page
        print("Navigating to Login Page...")
        await page.goto("http://localhost/login")
        await page.wait_for_timeout(2000)
        await page.screenshot(path="screenshots/login.png")
        
        # Authenticate
        print("Authenticating credentials...")
        await page.locator('input[placeholder="Enter your username"]').fill("testadmin")
        await page.locator('input[placeholder="Enter your password"]').fill("AdminSecurePass123!")
        await page.locator('button[type="submit"]').click()
        await page.wait_for_timeout(3000)
        
        # 2. Overview Dashboard
        print("Capturing Overview Dashboard...")
        await page.goto("http://localhost/")
        await page.wait_for_timeout(3000)
        await page.screenshot(path="screenshots/dashboard.png")
        
        # 3. Risk Heatmap
        print("Capturing Risk Heatmap...")
        await page.goto("http://localhost/heatmap")
        await page.wait_for_timeout(3000)
        await page.screenshot(path="screenshots/risk_heatmap.png")
        
        # 4. Knowledge Graph
        print("Capturing Knowledge Graph...")
        await page.goto("http://localhost/knowledge")
        await page.wait_for_timeout(3000)
        await page.screenshot(path="screenshots/knowledge_graph.png")
        
        # 5. Run Explorer
        print("Capturing Run Explorer...")
        await page.goto("http://localhost/runs")
        await page.wait_for_timeout(3000)
        await page.screenshot(path="screenshots/run_explorer.png")
        
        await browser.close()
        print("All screenshots successfully captured in d:\\Quality_OS\\screenshots\\ directory!")

if __name__ == "__main__":
    asyncio.run(capture())
