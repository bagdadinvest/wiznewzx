from playwright.sync_api import sync_playwright

def scrape_article_content(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=60000)  # Load the article page

        # Content structure
        content_structure = {
            "h1": None,
            "h2": [],
            "h3": [],
            "h4": [],
            "paragraphs": []
        }

        try:
            # Scrape the <h1> title
            title_element = page.query_selector('h1')
            content_structure["h1"] = title_element.inner_text().strip() if title_element else "None"

            # Locate main content area
            main_container = page.query_selector('article, .content, .article-body, .main-content')
            if main_container:
                elements = main_container.query_selector_all('h2, h3, h4, p')

                # Categorize elements
                for element in elements:
                    tag_name = element.evaluate('(element) => element.tagName.toLowerCase()')
                    text_content = element.inner_text().strip()

                    if tag_name == 'h2':
                        content_structure['h2'].append(text_content)
                    elif tag_name == 'h3':
                        content_structure['h3'].append(text_content)
                    elif tag_name == 'h4':
                        content_structure['h4'].append(text_content)
                    elif tag_name == 'p':
                        content_structure['paragraphs'].append(text_content)
            else:
                print("Main content container not found.")

        except Exception as e:
            print(f"Error while scraping: {e}")

        # Print structured content
        print(f"h1: {content_structure['h1']}")
        print(f"h2: {content_structure['h2'] if content_structure['h2'] else 'None'}")
        print(f"h3: {content_structure['h3'] if content_structure['h3'] else 'None'}")
        print(f"h4: {content_structure['h4'] if content_structure['h4'] else 'None'}")
        print("Paragraphs:")
        for paragraph in content_structure['paragraphs']:
            print(f"<p>{paragraph}</p>")

        browser.close()
        return content_structure

# Test the function with the provided URL
url = "https://www.bfmtv.com/international/moyen-orient/yemen-les-etats-unis-ont-frappe-des-installations-des-rebelles-houthis_AD-202411100111.html"
scrape_article_content(url)
