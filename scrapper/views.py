from django.http import JsonResponse
from wagtail.models import Page
from website.models import ProposalPage, ProposalIndexPage
from custom_media.models import CustomDocument
from wagtail.images import get_image_model
from django.urls import reverse
from playwright.sync_api import sync_playwright
from django.views.decorators.csrf import csrf_exempt
from django.core.files.temp import NamedTemporaryFile
from django.core.files import File
import os
import logging
import json
import hashlib
import requests

ImageModel = get_image_model()

# Configure logging
logging.basicConfig(level=logging.DEBUG)

TEMP_PDF_DIR = "temp_pdfs"
os.makedirs(TEMP_PDF_DIR, exist_ok=True)

def download_image(url):
    """Download image utility with improved handling."""
    try:
        response = requests.get(url, stream=True, timeout=10)
        if response.status_code == 200:
            content_type = response.headers.get('Content-Type')
            if not content_type or not content_type.startswith('image/'):
                print(f"Invalid content type for image: {content_type}")
                return None

            filename = os.path.basename(url.split("?")[0]) or "downloaded_image.jpg"
            temp_file = NamedTemporaryFile(delete=False, suffix=".jpg")
            for chunk in response.iter_content(1024):
                temp_file.write(chunk)
            temp_file.seek(0)

            image = ImageModel(title=filename)
            image.file.save(filename, File(temp_file), save=True)
            print(f"Image downloaded and saved successfully: {filename}")
            return image
        else:
            print(f"Failed to download image: {url}, Status code: {response.status_code}")
            return None
    except requests.RequestException as req_ex:
        print(f"Request failed for {url}: {req_ex}")
        return None
    except Exception as e:
        print(f"Failed downloading {url}: {e}")
        return None
    finally:
        if 'temp_file' in locals():
            temp_file.close()

def save_page_as_pdf(url, title):
    """PDF exporting with title as filename."""
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context()
            page = context.new_page()
            page.goto(url, timeout=60000, wait_until="domcontentloaded")
            page.wait_for_timeout(5000)

            pdf_path = os.path.join(TEMP_PDF_DIR, f"{title}.pdf")
            page.pdf(path=pdf_path)
            print(f"PDF generated successfully: {pdf_path}")
            return pdf_path
        except Exception as e:
            print(f"Could not generate PDF for {url}. Reason: {e}")
        finally:
            browser.close()

@csrf_exempt
def scrape_and_create_proposal(request):
    if request.method == "POST":
        try:
            print("Parsing request body...")
            data = json.loads(request.body)
            print(f"Request data received: {data}")

            url = data.get("url")
            title = data.get("title")
            source = data.get("source")
            description = data.get("description")
            image_url = data.get("image_url")

            missing_fields = [field for field in ["url", "title", "source", "description"] if not data.get(field)]
            if missing_fields:
                print(f"Missing fields: {missing_fields}")
                return JsonResponse({"error": f"Missing fields: {', '.join(missing_fields)}"}, status=400)

            parent_page = ProposalIndexPage.objects.live().first()
            if not parent_page:
                print("No ProposalIndexPage found, creating one.")
                root = Page.objects.get(slug='home')
                parent_page = ProposalIndexPage(title="Proposals Index")
                root.add_child(instance=parent_page)
                parent_page.save_revision().publish()
                print("ProposalIndexPage created.")

            cover_image = None
            if image_url:
                print(f"Downloading image from {image_url}...")
                cover_image = download_image(image_url)
                if cover_image:
                    print(f"Image downloaded and saved with ID {cover_image.id}.")
                else:
                    print("Image download failed or returned None.")

            print("Creating ProposalPage...")
            proposal_page = ProposalPage(
                title=title,
                caption=description,
                author=request.user,
                source=source,
                cover_image=cover_image
            )
            parent_page.add_child(instance=proposal_page)
            proposal_page.save_revision()
            print(f"ProposalPage '{title}' created with ID {proposal_page.id}.")

            pdf_path = save_page_as_pdf(url, proposal_page.title)
            if pdf_path:
                pdf_filename = f"{proposal_page.title}.pdf"
                with open(pdf_path, "rb") as pdf_file:
                    CustomDocument(title=proposal_page.title).file.save(pdf_filename, File(pdf_file))
                print(f"PDF for ProposalPage '{proposal_page.title}' saved successfully.")

            redirect_url = reverse('wagtailadmin_pages:edit', args=[proposal_page.id])
            return JsonResponse({"redirect_url": redirect_url}, status=200)

        except json.JSONDecodeError:
            print("Invalid JSON received.")
            return JsonResponse({"error": "Invalid JSON format"}, status=400)

        except Exception as ex:
            print(f"Unhandled exception: {ex}")
            return JsonResponse({'error': f'Unhandled issue: {str(ex)}'}, status=500)

    print("Invalid request method.")
    return JsonResponse({"error": "Invalid request method."}, status=405)
