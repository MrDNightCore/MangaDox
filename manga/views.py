from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.core.paginator import Paginator
from django.db.models import Q, F, Avg
from django.utils.html import escape
from django.contrib import messages as django_messages

from .models import Manga, Genre, Chapter, Bookmark, Rating, Comment
from users.models import UserProfile


def get_current_user(request):
    """Get the current logged-in user from session."""
    user_id = request.session.get('user_id')
    if user_id:
        try:
            return UserProfile.objects.get(id=user_id)
        except UserProfile.DoesNotExist:
            return None
    return None


def home(request):
    """Home page with popular and new manga."""
    popular_manga = Manga.objects.order_by('-views')[:12]
    new_manga = Manga.objects.order_by('-created_at')[:12]
    latest_updates = Chapter.objects.select_related('manga').order_by('-created_at')[:20]

    context = {
        'popular_manga': popular_manga,
        'new_manga': new_manga,
        'latest_updates': latest_updates,
    }
    return render(request, 'home.html', context)


def manga_list(request):
    """Browse manga with search, filters, and sorting."""
    queryset = Manga.objects.all()
    genres = Genre.objects.all()

    q = request.GET.get('q', '').strip()
    if q:
        queryset = queryset.filter(
            Q(title__icontains=q) |
            Q(alt_titles__icontains=q) |
            Q(author__icontains=q)
        )

    status = request.GET.get('status', '')
    if status:
        queryset = queryset.filter(status=status)

    manga_type = request.GET.get('type', '')
    if manga_type:
        queryset = queryset.filter(manga_type=manga_type)

    genre_slug = request.GET.get('genre', '')
    if genre_slug:
        genre_slugs = [s.strip() for s in genre_slug.split(',') if s.strip()]
        if genre_slugs:
            queryset = queryset.filter(genres__slug__in=genre_slugs).distinct()

    sort = request.GET.get('sort', 'latest')
    sort_map = {
        'popular': '-views',
        'rating': '-rating',
        'alpha': 'title',
        'alpha_desc': '-title',
        'new': '-created_at',
    }
    queryset = queryset.order_by(sort_map.get(sort, '-updated_at'))

    paginator = Paginator(queryset, 24)
    page = request.GET.get('page', 1)
    manga_page = paginator.get_page(page)

    context = {
        'manga_list': manga_page,
        'genres': genres,
        'query': q,
        'current_status': status,
        'current_type': manga_type,
        'current_sort': sort,
        'current_genre': genre_slug,
        'total_count': paginator.count,
    }
    return render(request, 'manga_list.html', context)


def manga_detail(request, slug):
    """Manga detail page with chapters, comments, and bookmark status."""
    manga = get_object_or_404(Manga, slug=slug)

    Manga.objects.filter(pk=manga.pk).update(views=F('views') + 1)
    manga.refresh_from_db()

    chapters = manga.chapters.order_by('-number')
    comments = manga.comments.select_related('user').order_by('-created_at')[:50]

    user = get_current_user(request)
    is_bookmarked = False
    user_rating = None
    if user:
        is_bookmarked = Bookmark.objects.filter(user=user, manga=manga).exists()
        try:
            user_rating = Rating.objects.get(user=user, manga=manga)
        except Rating.DoesNotExist:
            pass

    context = {
        'manga': manga,
        'chapters': chapters,
        'comments': comments,
        'is_bookmarked': is_bookmarked,
        'user_rating': user_rating,
        'bookmark_count': manga.get_bookmark_count(),
    }
    return render(request, 'manga_detail.html', context)


def chapter_reader(request, slug, number):
    """Chapter reader page — displays all chapter images vertically."""
    manga = get_object_or_404(Manga, slug=slug)

    try:
        chapter_number = float(number)
    except (TypeError, ValueError):
        raise Http404('Invalid chapter number')

    chapter = get_object_or_404(Chapter, manga=manga, number=chapter_number)
    images = chapter.get_images()
    next_chapter = chapter.get_next_chapter()
    prev_chapter = chapter.get_previous_chapter()
    all_chapters = manga.chapters.order_by('number')

    context = {
        'manga': manga,
        'chapter': chapter,
        'images': images,
        'next_chapter': next_chapter,
        'prev_chapter': prev_chapter,
        'all_chapters': all_chapters,
    }
    return render(request, 'chapter_reader.html', context)


def updates(request):
    """Latest manga chapter updates."""
    latest = Chapter.objects.select_related('manga').order_by('-created_at')

    manga_type = request.GET.get('type', '')
    if manga_type:
        latest = latest.filter(manga__manga_type=manga_type)

    paginator = Paginator(latest, 30)
    page = request.GET.get('page', 1)
    chapters_page = paginator.get_page(page)

    popular_manga = Manga.objects.order_by('-views')[:12]

    context = {
        'chapters': chapters_page,
        'popular_manga': popular_manga,
        'current_type': manga_type,
    }
    return render(request, 'updates.html', context)


@require_http_methods(["POST"])
@csrf_protect
def toggle_bookmark(request):
    """Toggle bookmark for a manga (AJAX)."""
    user = get_current_user(request)
    if not user:
        return JsonResponse({'error': 'Login required'}, status=401)

    manga_id = request.POST.get('manga_id')
    try:
        manga = Manga.objects.get(id=manga_id)
    except Manga.DoesNotExist:
        return JsonResponse({'error': 'Manga not found'}, status=404)

    bookmark, created = Bookmark.objects.get_or_create(user=user, manga=manga)
    if not created:
        bookmark.delete()
        return JsonResponse({'bookmarked': False, 'count': manga.get_bookmark_count()})

    return JsonResponse({'bookmarked': True, 'count': manga.get_bookmark_count()})


@require_http_methods(["POST"])
@csrf_protect
def rate_manga(request):
    """Rate a manga (AJAX)."""
    user = get_current_user(request)
    if not user:
        return JsonResponse({'error': 'Login required'}, status=401)

    manga_id = request.POST.get('manga_id')
    score = request.POST.get('score')

    try:
        score = float(score)
        if score < 1 or score > 5:
            return JsonResponse({'error': 'Score must be between 1 and 5'}, status=400)
    except (TypeError, ValueError):
        return JsonResponse({'error': 'Invalid score'}, status=400)

    try:
        manga = Manga.objects.get(id=manga_id)
    except Manga.DoesNotExist:
        return JsonResponse({'error': 'Manga not found'}, status=404)

    Rating.objects.update_or_create(
        user=user, manga=manga,
        defaults={'score': score}
    )

    avg = manga.ratings.aggregate(avg=Avg('score'))['avg'] or 0
    count = manga.ratings.count()
    manga.rating = round(avg, 1)
    manga.rating_count = count
    manga.save(update_fields=['rating', 'rating_count'])

    return JsonResponse({'rating': manga.rating, 'rating_count': manga.rating_count})


@require_http_methods(["POST"])
@csrf_protect
def add_comment(request):
    """Add a comment to a manga (AJAX)."""
    user = get_current_user(request)
    if not user:
        return JsonResponse({'error': 'Login required'}, status=401)

    manga_id = request.POST.get('manga_id')
    text = request.POST.get('text', '').strip()

    if not text:
        return JsonResponse({'error': 'Comment cannot be empty'}, status=400)
    if len(text) > 2000:
        return JsonResponse({'error': 'Comment too long (max 2000 chars)'}, status=400)

    try:
        manga = Manga.objects.get(id=manga_id)
    except Manga.DoesNotExist:
        return JsonResponse({'error': 'Manga not found'}, status=404)

    text = escape(text)
    comment = Comment.objects.create(user=user, manga=manga, text=text)

    return JsonResponse({
        'id': comment.id,
        'user': user.username,
        'text': comment.text,
        'created_at': comment.created_at.strftime('%b %d, %Y %I:%M %p'),
    })


def search_ajax(request):
    """Quick search returning JSON results."""
    q = request.GET.get('q', '').strip()
    if len(q) < 2:
        return JsonResponse({'results': []})

    results = Manga.objects.filter(
        Q(title__icontains=q) | Q(alt_titles__icontains=q)
    )[:8]

    data = []
    for m in results:
        latest = m.get_latest_chapter()
        data.append({
            'title': m.title,
            'slug': m.slug,
            'cover': m.get_cover_display(),
            'manga_type': m.manga_type,
            'latest_chapter': str(latest.number) if latest else 'N/A',
        })

    return JsonResponse({'results': data})


def bookmarks_page(request):
    """User's bookmarks page."""
    user = get_current_user(request)
    if not user:
        django_messages.warning(request, 'Please login to view your bookmarks.')
        return redirect('login_page')

    bookmarks = (
        Bookmark.objects.filter(user=user)
        .select_related('manga')
        .order_by('-created_at')
    )

    context = {'bookmarks': bookmarks}
    return render(request, 'bookmarks.html', context)
