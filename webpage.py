import asyncio
from playwright.async_api import async_playwright

class GoogleNewsScraper:
    def __init__(self):
        self.base_url = "https://news.google.com"
        self.sections = ['World', 'Business', 'Technology', 'Sports', 'Entertainment']

    async def scrape_section(self, page, section):
        try:
            urls = {
                'World': f"{self.base_url}/topics/CAAqKggKIiRDQkFTRlFvSUwyMHZNRGx1YlY4U0JXVnVMVWRDR2dKSlRpZ0FQAQ?hl=en-IN&gl=IN&ceid=IN:en",
                'Business': f"{self.base_url}/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx6TVdZU0FtVnVHZ0pKVGlnQVAB",
                'Technology': f"{self.base_url}/topics/CAAqKggKIiRDQkFTRlFvSUwyMHZNRGRqTVhZU0JXVnVMVWRDR2dKSlRpZ0FQAQ?hl=en-IN&gl=IN&ceid=IN:en",
                'Sports': f"{self.base_url}/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRFp1ZEdvU0FtVnVHZ0pKVGlnQVAB",
                'Entertainment': f"{self.base_url}/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNREpxYW5RU0FtVnVHZ0pKVGlnQVAB"
            }

            await page.goto(urls[section])
            await page.wait_for_load_state('networkidle')
            await page.wait_for_timeout(2000)

            headlines = []
            selectors = [
                'article h3',
                'article h4',
                '[role="heading"]',
                'h3 a',
                'h4 a',
                '.JtKRv',
                '.ipQwMb',
                'a[jsname]'
            ]

            for selector in selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    if elements:
                        for element in elements:
                            text = await element.inner_text()
                            if text and len(text.strip()) > 10:
                                headlines.append(text.strip())
                        if headlines:
                            break
                except:
                    continue

            seen = set()
            unique_headlines = []
            for headline in headlines:
                if headline not in seen and len(headline) > 15:
                    seen.add(headline)
                    unique_headlines.append(headline)

            return unique_headlines[:10]

        except Exception as e:
            print(f"Error scraping {section}: {str(e)}")
            return []

    async def scrape_all_sections(self):
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()

            results = {}
            for section in self.sections:
                print(f"Scraping {section}...")
                headlines = await self.scrape_section(page, section)
                results[section] = headlines
                await page.wait_for_timeout(1000)

            await browser.close()
            return results

    def save_to_html(self, results):
        html = """
        <html>
        <head>
            <title>Google News Headlines</title>
            <style>
                body { font-family: Arial; background: #f4f4f4; padding: 20px; }
                .section { background: white; padding: 20px; margin-bottom: 30px; border-radius: 10px; }
                h1 { text-align: center; }
            </style>
        </head>
        <body>
            <h1>📰 Google News Headlines</h1>
        """

        for section, headlines in results.items():
            html += f"<div class='section'><h2>{section}</h2>"
            if headlines:
                for i, headline in enumerate(headlines, 1):
                    html += f"<p>{i}. {headline}</p>"
            else:
                html += "<p>No headlines found.</p>"
            html += "</div>"

        html += "</body></html>"

        with open("news.html", "w", encoding="utf-8") as f:
            f.write(html)

        print("News saved to news.html. Open it in your browser!")

async def main():
    scraper = GoogleNewsScraper()
    print("🔄 Scraping Google News... Please wait...")
    try:
        results = await scraper.scrape_all_sections()
        scraper.save_to_html(results)
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())