import os
from django.core.management.base import BaseCommand
from django.conf import settings
from documents.models import Document

class Command(BaseCommand):
    help = "Removes old duplicate and orphaned generated files from media directory to free server storage."

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Report files that would be deleted without actually deleting them.',
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        media_root = str(settings.MEDIA_ROOT)
        gen_dir = os.path.join(media_root, 'generated')

        if not os.path.exists(gen_dir):
            self.stdout.write(self.style.WARNING(f"Directory not found: {gen_dir}"))
            return

        # Collect all active file paths recorded in Document model
        active_files = set()
        for doc in Document.objects.all():
            if doc.generated_pdf and doc.generated_pdf.name:
                active_files.add(os.path.abspath(os.path.join(media_root, doc.generated_pdf.name)))
            if doc.generated_docx and doc.generated_docx.name:
                active_files.add(os.path.abspath(os.path.join(media_root, doc.generated_docx.name)))
            if doc.qr_code and doc.qr_code.name:
                active_files.add(os.path.abspath(os.path.join(media_root, doc.qr_code.name)))

        deleted_count = 0
        reclaimed_bytes = 0

        for root, dirs, files in os.walk(gen_dir):
            for filename in files:
                full_path = os.path.abspath(os.path.join(root, filename))
                if full_path not in active_files:
                    try:
                        file_size = os.path.getsize(full_path)
                        if not dry_run:
                            os.remove(full_path)
                        deleted_count += 1
                        reclaimed_bytes += file_size
                    except Exception as e:
                        self.stderr.write(f"Could not remove {full_path}: {e}")

        mb_saved = round(reclaimed_bytes / (1024 * 1024), 2)
        action_word = "Would delete" if dry_run else "Successfully deleted"
        self.stdout.write(
            self.style.SUCCESS(
                f"{action_word} {deleted_count} orphaned/old files. Reclaimed {mb_saved} MB of disk storage!"
            )
        )
