import asyncio
from playwright.async_api import async_playwright
import time

class GoogleNewsScraper:
    def __init__(self):
        self.base_url = "https://news.google.com"
        self.sections = ['World', 'Business','Technology', 'Sports', 'Entertainment']
        
    async def scrape_section(self, page, section):
        """Scrape headlines for a specific section"""
        try:
            # Navigate to section
            if section == 'World':
                section_url = f"{self.base_url}/topics/CAAqKggKIiRDQkFTRlFvSUwyMHZNRGx1YlY4U0JXVnVMVWRDR2dKSlRpZ0FQAQ?hl=en-IN&gl=IN&ceid=IN%3Aen"
            elif section == 'Business':
                section_url = f"{self.base_url}/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx6TVdZU0FtVnVHZ0pKVGlnQVAB"
            elif section == 'Technology':
                section_url = f"{self.base_url}/topics/CAAqKggKIiRDQkFTRlFvSUwyMHZNRGRqTVhZU0JXVnVMVWRDR2dKSlRpZ0FQAQ?hl=en-IN&gl=IN&ceid=IN%3Aen"
            elif section == 'Sports':
                section_url = f"{self.base_url}/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRFp1ZEdvU0FtVnVHZ0pKVGlnQVAB"
            elif section == 'Entertainment':
                section_url = f"{self.base_url}/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNREpxYW5RU0FtVnVHZ0pKVGlnQVAB"
            else:
                return []
            
            await page.goto(section_url)
            
            # Wait for content to load
            await page.wait_for_load_state('networkidle')
            await page.wait_for_timeout(2000)  # Additional wait for dynamic content
            
            # Try multiple selectors to find headlines
            headlines = []
            selectors = [
                'article h3',
                'article h4',
                '[role="heading"]',
                'h3 a',
                'h4 a',
                '.JtKRv',  # Google News specific class
                '.ipQwMb',  # Another Google News class
                'a[jsname]'  # Links with jsname attribute
            ]
            
            for selector in selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    if elements:
                        for element in elements:
                            text = await element.inner_text()
                            if text and len(text.strip()) > 10:
                                headlines.append(text.strip())
                        if headlines:  # If we found headlines with this selector, break
                            break
                except Exception as e:
                    continue
            
            # Remove duplicates while preserving order
            seen = set()
            unique_headlines = []
            for headline in headlines:
                if headline not in seen and len(headline) > 15:  # Filter short headlines
                    seen.add(headline)
                    unique_headlines.append(headline)
            
            # Add section URL as the source for all headlines in this section
            return {
                "headlines": unique_headlines[:10],  # Return top 10 headlines
                "source": section_url  # Add the section URL as source
            }
            
        except Exception as e:
            print(f"Error scraping {section}: {str(e)}")
            return {"headlines": [], "source": ""}
    
    async def scrape_all_sections(self):
        """Scrape headlines from all sections"""
        async with async_playwright() as p:
            # Launch browser
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            )
            page = await context.new_page()
            
            results = {}
            
            for section in self.sections:
                print(f"Scraping {section} section...")
                section_data = await self.scrape_section(page, section)
                results[section] = section_data
                
                # Small delay between requests
                await page.wait_for_timeout(1000)
            
            await browser.close()
            return results
    
    def print_headlines(self, results):
        """Print headlines organized by section"""
        print("\n" + "="*60)
        print("GOOGLE NEWS HEADLINES BY SECTION")
        print("="*60)
        
        for section, data in results.items():
            headlines = data["headlines"]
            source = data["source"]
            
            print(f"\n{section.upper()} NEWS:")
            print(f"Source: {source}")
            print("-" * 40)
            
            if headlines:
                for i, headline in enumerate(headlines, 1):
                    print(f"{i:2d}. {headline}")
            else:
                print("No headlines found for this section")
            
            print()

async def main():
    """Main function to run the scraper"""
    scraper = GoogleNewsScraper()
    
    print("Starting Google News scraping...")
    print("This may take a few moments...")
    
    try:
        results = await scraper.scrape_all_sections()
        scraper.print_headlines(results)
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
     
if __name__ == "__main__":
    # Run the scraper
    asyncio.run(main())