"""Clean up unusable manga `cover_url` values.

Render's filesystem is ephemeral, so uploaded covers disappear between
deploys. This command used to paper over that by pointing every cover at
`https://via.placeholder.com/...`, but that service no longer resolves — which
is what made every cover render as a broken image in production.

Instead of inventing an external URL, unusable values are cleared so that
`Manga.get_cover_display()` falls back to the bundled `default_cover.svg`
which is served from static files and always loads.
"""
from django.core.management.base import BaseCommand

from manga.image_urls import is_direct_image_url
from manga.models import Manga


class Command(BaseCommand):
    help = (
        "Clear manga cover URLs that a browser cannot render as an image "
        "(page links, dead placeholder services) so the default cover is used."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Report the unusable cover URLs without modifying them.',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        cleared = 0

        for manga in Manga.objects.exclude(cover_url='').only('id', 'title', 'cover_url'):
            if is_direct_image_url(manga.cover_url):
                continue

            self.stdout.write(f'  - {manga.title}: unusable cover URL {manga.cover_url}')
            cleared += 1
            if not dry_run:
                Manga.objects.filter(pk=manga.pk).update(cover_url='')

        if dry_run:
            self.stdout.write(self.style.WARNING(f'\nDry run: {cleared} cover URL(s) would be cleared.'))
        else:
            self.stdout.write(self.style.SUCCESS(f'\nCleared {cleared} unusable cover URL(s).'))
