from wagtail.blocks import StreamValue
from django.http import JsonResponse
from wagtail.models import Page
from website.models import CustomArticlePage, ArticleIndexPage
import json
import logging
from playwright.sync_api import sync_playwright

logging.basicConfig(level=logging.DEBUG)

def scrape_page_content(url):
    """Scrapes page content and returns a dictionary with 'h1' and 'body'."""
    with sync_playwright() as p:
        logging.debug("Launching Playwright browser...")
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        logging.debug(f"Navigating to {url}")

        scraped_content = {"h1": "Untitled Article", "body": "No content available."}

        try:
            page.goto(url, timeout=60000, wait_until="domcontentloaded")
            logging.debug("Page loaded successfully.")

            # Get h1
            h1_element = page.query_selector('h1')
            if h1_element:
                scraped_content["h1"] = h1_element.inner_text().strip()
                logging.debug(f"Found h1: {scraped_content['h1']}")
            else:
                logging.warning("No h1 element found on the page.")

            # Get main content
            main_container = page.query_selector('article, .content, .article-body, .main-content')
            if main_container:
                paragraphs = main_container.query_selector_all('p')
                body_content = "\n\n".join([p.inner_text().strip() for p in paragraphs])
                scraped_content["body"] = body_content
                logging.debug(f"Scraped body content: {scraped_content['body'][:500]}...")  # Truncated for logging
            else:
                logging.warning("Main content container not found.")
        except Exception as e:
            logging.error(f"Error while scraping: {e}")
            scraped_content["error"] = str(e)
        finally:
            browser.close()
            logging.debug("Browser closed.")

        return scraped_content

def scrape_view(request):
    """Handles scraping and creation of CustomArticlePage."""
    logging.debug("Received a request to scrape and create an article.")

    if request.method == "POST":
        try:
            data = json.loads(request.body)
            logging.debug(f"Request data: {data}")

            url = data.get("url")
            if not url:
                logging.error("No URL provided in request.")
                return JsonResponse({"error": "URL is required"}, status=400)

            logging.debug(f"Scraping content for URL: {url}")
            scraped_content = scrape_page_content(url)

            if 'error' in scraped_content:
                logging.error(f"Scraping error: {scraped_content['error']}")
                return JsonResponse(scraped_content, status=400)

            # Ensure ArticleIndexPage exists
            parent_page = ArticleIndexPage.objects.live().first()
            if not parent_page:
                logging.info("No ArticleIndexPage found, creating one.")
                home_page = Page.objects.get(slug='home')
                parent_page = ArticleIndexPage(
                    title="Articles",
                    slug="articles"
                )
                home_page.add_child(instance=parent_page)
                parent_page.save_revision().publish()
                logging.debug("ArticleIndexPage created and published.")

            # Create new CustomArticlePage
            logging.debug(f"Creating CustomArticlePage with title: {scraped_content['h1']}")
            article_page = CustomArticlePage(
                title=scraped_content["h1"],
                additional_content=scraped_content["body"]
            )
            parent_page.add_child(instance=article_page)
            article_page.save_revision().publish()
            logging.debug(f"CustomArticlePage created successfully with ID: {article_page.id}")

            return JsonResponse({"message": "CustomArticlePage created successfully.", "page_id": article_page.id})
        except Exception as e:
            logging.error(f"Error during article creation: {e}")
            return JsonResponse({"error": str(e)}, status=500)

    logging.warning("Invalid request method received.")
    return JsonResponse({"error": "Invalid request method."}, status=405)
