from django.core.management.base import BaseCommand
from django.utils import timezone

from photobooth.models import PhotoboothSession


class Command(BaseCommand):
    help = "Create a new photobooth session for an event"

    def add_arguments(self, parser):
        parser.add_argument(
            "name", type=str, help='Event name (e.g., "John & Jane Wedding")'
        )
        parser.add_argument(
            "--activate", action="store_true", help="Set as active session"
        )
        parser.add_argument("--qr-url", type=str, help="Base URL for QR codes")

    def handle(self, *args, **options):
        name = options["name"]
        activate = options["activate"]
        qr_url = options["qr_url"] or "http://localhost:8001"

        # Deactivate other sessions if this one should be active
        if activate:
            PhotoboothSession.objects.filter(is_active=True).update(is_active=False)
            self.stdout.write(
                self.style.WARNING("Deactivated existing active sessions")
            )

        # Create new session
        session = PhotoboothSession.objects.create(
            name=name, date=timezone.now(), is_active=activate, qr_base_url=qr_url
        )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created session: "{session.name}"')
        )
        self.stdout.write(f"Session ID: {session.id}")

        if activate:
            self.stdout.write(self.style.SUCCESS("Session is now ACTIVE"))

        self.stdout.write(f"Photobooth URL: {qr_url}/photobooth/")
        self.stdout.write(f"Gallery URL: {qr_url}/photobooth/gallery/{session.id}/")
