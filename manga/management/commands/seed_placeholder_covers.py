"""Management command to seed manga with placeholder cover images for testing."""
from django.core.management.base import BaseCommand
from manga.models import Manga


class Command(BaseCommand):
    help = "Update all manga with placeholder cover URLs for testing (when media files are unavailable)"

    def handle(self, *args, **options):
        # Placeholder image URL (from placeholder service)
        placeholder_url = "https://via.placeholder.com/400x600?text=No+Cover"

        manga_list = Manga.objects.all()
        updated_count = 0

        for manga in manga_list:
            # Only update if cover_url is empty
            if not manga.cover_url:
                manga.cover_url = placeholder_url
                manga.save()
                updated_count += 1
                self.stdout.write(f"  ✓ {manga.title} → placeholder")

        self.stdout.write(
            self.style.SUCCESS(f"\n✓ Updated {updated_count} manga with placeholder cover URLs")
        )
