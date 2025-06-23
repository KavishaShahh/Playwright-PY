import asyncio
from playwright.async_api import async_playwright

async def fetch_news_from_sections():
    sections = ['India', 'World', 'Business', 'Sports', 'Entertainment']

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        # Open Google News homepage
        await page.goto("https://news.google.com", wait_until="domcontentloaded")

        for section in sections:
            try:
                # Click on the section from sidebar
                await page.click(f'a[aria-label="{section}"]')
                await page.wait_for_timeout(5000)  # Wait for news to load

                # Get top 5 headlines from this section
                headlines = await page.locator('article a').all_text_contents()

                print(f"\nTop 5 Headlines from {section} Section:\n")
                i = 0
                limit = 0
                while limit < 5 and i < len(headlines):
                    if len(headlines[i]) > 0:
                        print(f"{limit + 1}. {headlines[i]}")
                        limit += 1
                    i += 1
            except Exception as e:
                print(f"\nCould not fetch headlines for {section}: {e}")

        await browser.close()

# Run the script
asyncio.run(fetch_news_from_sections())