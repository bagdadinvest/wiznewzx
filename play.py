import os
from pyvirtualdisplay import Display
from playwright.sync_api import sync_playwright

# Define a temporary directory for storing PDFs
TEMP_PDF_DIR = "pdfs"
os.makedirs(TEMP_PDF_DIR, exist_ok=True)

def save_page_as_pdf(url, title):
    """Export the given webpage as a PDF."""
    # Start the virtual display
    display = Display(visible=False, size=(1920, 1080))
    display.start()

    try:
        # Run Playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)  # Must be headless for PDF
            context = browser.new_context()
            page = context.new_page()

            # Navigate to the URL
            page.goto(url, timeout=60000, wait_until="domcontentloaded")
            page.wait_for_timeout(5000)

            # Set PDF output path
            pdf_path = os.path.join(TEMP_PDF_DIR, f"{title}.pdf")

            # Generate the PDF
            page.pdf(
                path=pdf_path,
                format="A4",
                print_background=True,
            )

            print(f"PDF generated successfully: {pdf_path}")
            return pdf_path

    except Exception as e:
        print(f"Error generating PDF: {e}")
    finally:
        # Ensure cleanup of resources
        display.stop()

# Example Usage
if __name__ == "__main__":
    url = "https://www.msn.com/it-it/notizie/italia/pozzolo-%C3%A8-stato-rinviato-a-giudizio-per-porto-illegale-di-armi/ar-AA1urEat"
    title = "example_page"
    save_page_as_pdf(url, title)
