"""Helpers for validating and resolving cover / page image URLs.

Live covers were breaking for two reasons handled here:

1. `cover_url` values pointing at *web pages* instead of image files
   (e.g. `https://in.pinterest.com/pin/1109715164490885466/`). The browser
   receives HTML, cannot decode it as an image and renders a broken image.
2. `https://via.placeholder.com/...` — the placeholder service used by the
   old seeding command no longer resolves, so every seeded cover 404'd.
"""
from urllib.parse import urlparse

from django.templatetags.static import static

# Static path of the bundled "no cover" artwork (staticfiles/images/).
DEFAULT_COVER_STATIC_PATH = 'images/default_cover.svg'

# Hosts that only ever serve HTML pages, never a direct image file.
PAGE_ONLY_HOSTS = (
    'pinterest.com',
    'pin.it',
    'imgur.com',          # direct images live on i.imgur.com
    'flickr.com',
    'deviantart.com',
    'x.com',
    'twitter.com',
    'facebook.com',
    'instagram.com',
    'reddit.com',
    'mangadex.org',
    'google.com',
)

# Image hosts/services that are dead or block hotlinking, so they always
# render as a broken image in the browser.
UNREACHABLE_IMAGE_HOSTS = (
    'via.placeholder.com',
    'placeholder.com',
)

# Extensions a browser can decode as an image.
IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.gif', '.webp', '.avif', '.bmp', '.svg')

# Non-image document extensions occasionally pasted by mistake.
NON_IMAGE_EXTENSIONS = ('.html', '.htm', '.php', '.asp', '.aspx', '.pdf')


def default_cover_url():
    """URL of the bundled fallback cover, hashed when using manifest storage."""
    try:
        return static(DEFAULT_COVER_STATIC_PATH)
    except Exception:
        # Manifest lookup can fail if `collectstatic` has not run yet.
        return '/static/' + DEFAULT_COVER_STATIC_PATH


def _host_matches(host, candidates):
    return any(host == c or host.endswith('.' + c) for c in candidates)


def is_direct_image_url(url):
    """True when `url` can reasonably be rendered inside an `<img>` tag."""
    if not url:
        return False

    parsed = urlparse(url.strip())
    if parsed.scheme not in ('http', 'https') or not parsed.netloc:
        return False

    host = parsed.netloc.lower().split('@')[-1].split(':')[0]
    if _host_matches(host, UNREACHABLE_IMAGE_HOSTS):
        return False

    path = parsed.path.lower()
    # An explicit image extension is the strongest signal and wins over the
    # host check, so image CDNs of page-only hosts (i.pinimg.com, i.imgur.com)
    # keep working.
    if path.endswith(IMAGE_EXTENSIONS):
        return True
    if path.endswith(NON_IMAGE_EXTENSIONS):
        return False
    if _host_matches(host, PAGE_ONLY_HOSTS):
        return False
    # Many CDNs serve extension-less image URLs — allow those through.
    return bool(path.strip('/')) or bool(parsed.query)


def resolve_cover_url(cover_url):
    """Return a usable cover URL, or an empty string when unusable."""
    cover_url = (cover_url or '').strip()
    return cover_url if is_direct_image_url(cover_url) else ''
