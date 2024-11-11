from django.core.management.base import BaseCommand
from translations.azure import AzureTranslator
from django.conf import settings
import polib

class Command(BaseCommand):
    help = 'Automatically translate .po files using Azure Translator'

    def add_arguments(self, parser):
        parser.add_argument(
            'po_filepath',
            type=str,
            help='Path to the .po file to be translated',
        )

    def handle(self, *args, **options):
        po_filepath = options['po_filepath']

        # Initialize AzureTranslator using settings
        translator = AzureTranslator(settings.WAGTAILLOCALIZE_MACHINE_TRANSLATOR['OPTIONS'])

        # Load and translate the .po file
        po = polib.pofile(po_filepath)
        for entry in po.untranslated_entries():
            translated_text = translator.translate(entry.msgid)
            entry.msgstr = translated_text
            self.stdout.write(self.style.SUCCESS(f'Translated: {entry.msgid} -> {translated_text}'))

        # Save updated .po file
        po.save(po_filepath)
        self.stdout.write(self.style.SUCCESS('Translation completed and saved.'))
