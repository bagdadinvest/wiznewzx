import os
import logging
from playwright.sync_api import sync_playwright

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Directory to save PDFs
PDF_DIR = "pdfs"
os.makedirs(PDF_DIR, exist_ok=True)

def dismiss_popups(page):
    """Handle common pop-ups like modals or cookie banners."""
    try:
        popups = [
            {"selector": "div.cookie-banner button.accept", "action": "click"},
            {"selector": "div.modal button.close", "action": "click"},
            {"selector": "button.subscribe-close", "action": "click"}
        ]

        for popup in popups:
            element = page.query_selector(popup["selector"])
            if element:
                element.click()
                logging.debug(f"Popup dismissed: {popup['selector']}")
    except Exception as e:
        logging.warning(f"Error dismissing popups: {e}")

def save_page_as_pdf(url, pdf_name="page.pdf"):
    """Visit the URL, handle pop-ups, and save the webpage as a PDF."""
    with sync_playwright() as p:
        logging.debug("Launching browser...")
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        try:
            logging.debug(f"Navigating to {url}")
            page.goto(url, timeout=60000, wait_until="domcontentloaded")
            logging.debug("Page loaded successfully.")

            # Handle pop-ups and modals
            dismiss_popups(page)

            # Inject CSS to hide persistent banners
            page.add_style_tag(content="""
                .subscribe-modal, .popup, .login-prompt {
                    display: none !important;
                }
            """)

            # Save the page as PDF
            pdf_path = os.path.join(PDF_DIR, pdf_name)
            page.pdf(path=pdf_path, format="A4", print_background=True)
            logging.info(f"PDF saved at {pdf_path}")

        except Exception as e:
            logging.error(f"Error during PDF generation: {e}")

        finally:
            browser.close()
            logging.debug("Browser closed.")

        return pdf_path

# Test Function
def test_pdf_generation():
    test_url = "https://dailyhodl.com/2024/11/14/polygon-rival-primed-to-explode-by-over-200-in-weeks-according-to-crypto-analyst-michael-van-de-poppe/"  # Replace with your target URL
    pdf_path = save_page_as_pdf(test_url, "test_page_with_popups.pdf")
    print(f"Generated PDF at: {pdf_path}")

if __name__ == "__main__":
    test_pdf_generation()
