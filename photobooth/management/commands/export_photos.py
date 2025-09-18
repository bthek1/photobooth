import os
import shutil

from django.core.management.base import BaseCommand

from photobooth.models import Photo


class Command(BaseCommand):
    help = "Export photos from a photobooth session"

    def add_arguments(self, parser):
        parser.add_argument("session_id", type=str, help="Session UUID to export")
        parser.add_argument(
            "--output-dir",
            type=str,
            help="Output directory (default: exported_photos_<session_id>)",
        )
        parser.add_argument(
            "--include-metadata",
            action="store_true",
            help="Include metadata in filenames",
        )

    def handle(self, *args, **options):
        session_id = options["session_id"]
        output_dir = options["output_dir"] or f"exported_photos_{session_id}"
        include_metadata = options["include_metadata"]

        # Get photos for session
        photos = Photo.objects.filter(session_id=session_id, is_processed=True)

        if not photos.exists():
            self.stdout.write(
                self.style.ERROR(f"No photos found for session {session_id}")
            )
            return

        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        self.stdout.write(f"Exporting to: {output_dir}")

        # Export photos
        exported_count = 0
        for i, photo in enumerate(photos, 1):
            if photo.image and os.path.exists(photo.image.path):
                # Generate filename
                if include_metadata:
                    guest_name = (
                        photo.guest_name.replace(" ", "_")
                        if photo.guest_name
                        else "guest"
                    )
                    filename = f"photo_{i:04d}_{photo.taken_at.strftime('%Y%m%d_%H%M%S')}_{guest_name}.jpg"
                else:
                    filename = (
                        f"photo_{i:04d}_{photo.taken_at.strftime('%Y%m%d_%H%M%S')}.jpg"
                    )

                # Copy file
                src = photo.image.path
                dst = os.path.join(output_dir, filename)
                shutil.copy2(src, dst)
                exported_count += 1

                self.stdout.write(f"Exported: {filename}")

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully exported {exported_count} photos to {output_dir}/"
            )
        )
