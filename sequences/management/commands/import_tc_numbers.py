import openpyxl
from django.core.management.base import BaseCommand
from sequences.models import DocumentNumberSequence

class Command(BaseCommand):
    help = 'Import TC numbers from Excel file'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to Excel file')

    def handle(self, *args, **options):
        file_path = options['file_path']
        wb = openpyxl.load_workbook(file_path)
        sheet = wb.active
        prefix = 'AFPL/2026-27/'  # adjust as needed
        seq, created = DocumentNumberSequence.objects.get_or_create(prefix=prefix)
        numbers = []
        for row in sheet.iter_rows(min_row=2, values_only=True):  # assuming header row
            val = row[0]  # first column
            if val and str(val).isdigit():
                numbers.append(int(val))
        seq.used_numbers = numbers
        seq.last_number = max(numbers) if numbers else 0
        seq.save()
        self.stdout.write(self.style.SUCCESS(f'Imported {len(numbers)} numbers'))