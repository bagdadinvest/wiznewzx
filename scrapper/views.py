import logging
from django.http import JsonResponse
from playwright.sync_api import sync_playwright

# Setup logging for debug statements
logging.basicConfig(level=logging.DEBUG)

def scrape_page_content(url):
    with sync_playwright() as p:
        logging.debug("Launching Playwright browser...")
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        logging.debug(f"Navigating to {url}")

        try:
            page.goto(url, timeout=60000, wait_until="domcontentloaded")

            scraped_content = {
                "h1": None,
                "subheaders": [],
                "paragraphs": []
            }

            # Get the h1 element
            title_element = page.query_selector('h1')
            scraped_content["h1"] = title_element.inner_text().strip() if title_element else "None"
            logging.debug(f"Title found: {scraped_content['h1']}")

            # Get the main content
            main_container = page.query_selector('article, .content, .article-body, .main-content')
            if main_container:
                elements = main_container.query_selector_all('h2, h3, h4, p')
                logging.debug(f"Found {len(elements)} elements in the main container.")
                for element in elements:
                    tag_name = element.evaluate('(element) => element.tagName.toLowerCase()')
                    text_content = element.inner_text().strip()

                    if tag_name in ['h2', 'h3', 'h4']:
                        scraped_content['subheaders'].append({"tag": tag_name, "text": text_content})
                    elif tag_name == 'p':
                        scraped_content['paragraphs'].append(text_content)

                # Sort paragraphs by length
                scraped_content['paragraphs'].sort(key=len, reverse=True)
                logging.debug("Paragraphs sorted by length.")
            else:
                logging.warning("Main content container not found.")
        except Exception as e:
            logging.error(f"Error while scraping: {e}")
        finally:
            browser.close()
            logging.debug("Browser closed.")

        return scraped_content

def scrape_view(request):
    if request.method == "POST":
        url = request.POST.get("url")
        logging.debug(f"Scraping content for URL: {url}")
        content = scrape_page_content(url)
        return JsonResponse(content, safe=False)

    return render(request, "admin/scrape_page.html")
