import os
import csv
import datetime
from lxml import html
from django.core.management.base import BaseCommand
from scraping.models import Website

class Command(BaseCommand):
    help = 'Extract content from HTML files using XPath selectors'

    def add_arguments(self, parser):
        parser.add_argument(
            '--website-ids',
            nargs='*',
            type=int,
            help='List of website IDs to process. If not provided, all websites will be processed.'
        )

    def handle(self, *args, **options):
        """Handle the command."""
        self.stdout.write(self.style.SUCCESS('Starting extraction process...'))

        # Extract arguments
        website_ids = options.get('website-ids')

        if website_ids:
            self.stdout.write(f"Website IDs provided: {website_ids}")  # Debug statement
            websites = Website.objects.filter(id__in=website_ids)
        else:
            self.stdout.write("No website IDs provided. Processing all websites.")  # Debug statement
            websites = Website.objects.all()

        self.stdout.write(f"Websites retrieved: {[website.name for website in websites]}")  # Debug statement

        if not websites:
            self.stdout.write(self.style.ERROR("No websites found."))
            return

        for website in websites:
            self.stdout.write(self.style.SUCCESS(f"Processing '{website.name}'"))

            # Define file paths
            today_str = datetime.date.today().strftime('%Y-%m-%d')
            base_directory = os.path.join('media', website.name, today_str)
            html_file_path = os.path.join(base_directory, 'fullpage.html')
            xpaths_file_path = os.path.join(base_directory, 'xpaths.csv')
            output_file_path = os.path.join(base_directory, 'extracted_content.txt')

            # Check if the HTML file exists
            if not os.path.exists(html_file_path):
                self.stdout.write(self.style.ERROR(f"HTML file not found: '{html_file_path}' for website '{website.name}'"))
                continue

            # Check if the XPaths CSV file exists
            if not os.path.exists(xpaths_file_path):
                self.stdout.write(self.style.ERROR(f"XPaths CSV file not found: '{xpaths_file_path}' for website '{website.name}'"))
                continue

            # Read XPaths from CSV
            xpaths = self.read_xpaths_from_csv(xpaths_file_path)
            
            # Print the XPaths found, including when empty
            if xpaths:
                self.stdout.write(f"XPaths found in '{xpaths_file_path}': {xpaths}")
            else:
                self.stdout.write(f"No XPaths found in '{xpaths_file_path}'")

            # Load HTML content
            html_content = self.load_html_content(html_file_path)
            
            if html_content:
                # Extract content using XPath selectors
                extracted_content = self.extract_text_by_xpath(html_content, xpaths)
                
                # Save extracted content to a file in tabular format
                self.save_text_to_file(extracted_content, output_file_path)
                self.stdout.write(f"Extracted content saved to '{output_file_path}'")

    def read_xpaths_from_csv(self, file_path):
        """Read XPath selectors from a CSV file."""
        xpaths = []
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                # Debug: Check if the header is correct
                header = reader.fieldnames
                self.stdout.write(f"CSV Header: {header}")
                
                for row in reader:
                    xpath = row.get('XPath Segment')  # Updated header name
                    if xpath:
                        xpaths.append(xpath.strip())
            self.stdout.write(f"XPaths read: {xpaths}")
        except IOError as e:
            self.stdout.write(self.style.ERROR(f"Error reading XPath file '{file_path}': {e}"))
        return xpaths

    def load_html_content(self, file_path):
        """Load HTML content from a file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except IOError as e:
            self.stdout.write(self.style.ERROR(f"Error reading HTML file '{file_path}': {e}"))
            return None

    def extract_text_by_xpath(self, html_content, xpaths):
        """Extract text from HTML content based on a list of XPath selectors."""
        try:
            tree = html.fromstring(html_content)
            extracted_data = []
            for xpath in xpaths:
                try:
                    elements = tree.xpath(xpath)
                    content = '\n'.join(html.tostring(element, method='text', encoding='unicode').strip() for element in elements)
                    extracted_data.append((xpath, content))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"XPath error for '{xpath}': {e}"))
            return extracted_data
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error processing HTML content: {e}"))
            return []

    def save_text_to_file(self, data, file_path):
        """Save extracted text content to a file in tabular format."""
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                for xpath, content in data:
                    file.write(f"{xpath},{content}\n")
        except IOError as e:
            self.stdout.write(self.style.ERROR(f"Error saving file '{file_path}': {e}"))
