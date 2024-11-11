import json
from django.http import JsonResponse
from django.shortcuts import render
from playwright.sync_api import sync_playwright

def scrape_page_content(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=60000)

        scraped_content = {
            "h1": None,
            "subheaders": [],
            "paragraphs": []
        }

        try:
            # Get the h1 element
            title_element = page.query_selector('h1')
            scraped_content["h1"] = title_element.inner_text().strip() if title_element else "None"

            # Get the main container
            main_container = page.query_selector('article, .content, .article-body, .main-content')
            if main_container:
                elements = main_container.query_selector_all('h2, h3, h4, p')
                for element in elements:
                    tag_name = element.evaluate('(element) => element.tagName.toLowerCase()')
                    text_content = element.inner_text().strip()

                    if tag_name in ['h2', 'h3', 'h4']:
                        scraped_content['subheaders'].append({"tag": tag_name, "text": text_content})
                    elif tag_name == 'p':
                        scraped_content['paragraphs'].append(text_content)

                # Sort paragraphs by length, largest first
                scraped_content['paragraphs'].sort(key=len, reverse=True)
        except Exception as e:
            print(f"Error while scraping: {e}")

        browser.close()
        return scraped_content

def scrape_view(request):
    if request.method == "POST":
        url = request.POST.get("url")
        content = scrape_page_content(url)
        return JsonResponse(content, safe=False)

    return render(request, "scrape_page.html")
