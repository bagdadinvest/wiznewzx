from django.http import JsonResponse
from wagtail.blocks import RichTextBlock
from wagtail.models import Page
from website.models import ArticlePage, ArticleIndexPage  # Import your models
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

            # Get h1
            h1_element = page.query_selector('h1')
            scraped_content["h1"] = h1_element.inner_text().strip() if h1_element else scraped_content["h1"]

            # Get main content
            main_container = page.query_selector('article, .content, .article-body, .main-content')
            if main_container:
                paragraphs = main_container.query_selector_all('p')
                body_content = "\n\n".join([p.inner_text().strip() for p in paragraphs])
                scraped_content["body"] = body_content
            else:
                logging.warning("Main content container not found.")
        except Exception as e:
            logging.error(f"Error while scraping: {e}")
            scraped_content["error"] = str(e)
        finally:
            browser.close()

        return scraped_content

def scrape_view(request):
    """Handles scraping and creation of ArticlePage."""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            url = data.get("url")
            logging.debug(f"Scraping content for URL: {url}")
            scraped_content = scrape_page_content(url)

            if 'error' in scraped_content:
                return JsonResponse(scraped_content, status=400)

            # Ensure ArticleIndexPage exists
            parent_page = ArticleIndexPage.objects.live().first()
            if not parent_page:
                logging.info("Creating a new ArticleIndexPage...")
                home_page = Page.objects.get(slug='home')  # Adjust this slug if needed
                parent_page = ArticleIndexPage(
                    title="Articles",
                    slug="articles"
                )
                home_page.add_child(instance=parent_page)
                parent_page.save_revision().publish()

            # Create new ArticlePage
            article_page = ArticlePage(
                title=scraped_content["h1"],
                body=[("paragraph", scraped_content["body"])]  # Using StreamField block
            )
            parent_page.add_child(instance=article_page)
            article_page.save_revision().publish()

            return JsonResponse({"message": "ArticlePage created successfully.", "page_id": article_page.id})
        except Exception as e:
            logging.error(f"Error: {e}")
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method."}, status=405)
