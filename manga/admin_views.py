from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.core.paginator import Paginator
from django.db.models import Q, Count

from .models import Manga, Genre, Chapter, ChapterImage, Bookmark, Comment
from .forms import MangaForm, ChapterForm
from users.models import UserProfile


def admin_required(view_func):
    """Decorator requiring admin access."""
    def wrapper(request, *args, **kwargs):
        # First, allow Django's auth users only if they're superuser
        try:
            if hasattr(request, 'user') and request.user.is_authenticated:
                # Allow direct Django superusers
                if getattr(request.user, 'is_superuser', False):
                    # Try to attach a matching UserProfile if available (by email or username)
                    profile = None
                    try:
                        if getattr(request.user, 'email', None):
                            profile = UserProfile.objects.filter(email=request.user.email).first()
                        if not profile and getattr(request.user, 'username', None):
                            profile = UserProfile.objects.filter(username=request.user.username).first()
                    except Exception:
                        profile = None
                    request.admin_user = profile
                    return view_func(request, *args, **kwargs)
                # If not a superuser, check if there's a linked UserProfile marked as is_admin
                else:
                    profile = None
                    try:
                        if getattr(request.user, 'email', None):
                            profile = UserProfile.objects.filter(email=request.user.email).first()
                        if not profile and getattr(request.user, 'username', None):
                            profile = UserProfile.objects.filter(username=request.user.username).first()
                    except Exception:
                        profile = None
                    if profile and getattr(profile, 'is_admin', False):
                        request.admin_user = profile
                        return view_func(request, *args, **kwargs)
        except Exception:
            # If anything goes wrong checking request.user, fall back to session-based check below
            pass

        # Fallback: legacy/session-based admin system used by the site
        user_id = request.session.get('user_id')
        if not user_id:
            messages.warning(request, 'Please login first.')
            return redirect('login_page')
        try:
            user = UserProfile.objects.get(id=user_id)
            if not user.is_admin:
                messages.error(request, 'Admin access required.')
                return redirect('home')
        except UserProfile.DoesNotExist:
            messages.error(request, 'User not found.')
            return redirect('login_page')
        request.admin_user = user
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    wrapper.__doc__ = view_func.__doc__
    return wrapper


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------
@admin_required
def dashboard(request):
    total_manga = Manga.objects.count()
    total_chapters = Chapter.objects.count()
    total_users = UserProfile.objects.count()
    total_bookmarks = Bookmark.objects.count()
    total_comments = Comment.objects.count()
    total_genres = Genre.objects.count()

    recent_manga = Manga.objects.order_by('-created_at')[:5]
    recent_chapters = Chapter.objects.select_related('manga').order_by('-created_at')[:10]
    recent_users = UserProfile.objects.order_by('-created_at')[:5]

    context = {
        'total_manga': total_manga,
        'total_chapters': total_chapters,
        'total_users': total_users,
        'total_bookmarks': total_bookmarks,
        'total_comments': total_comments,
        'total_genres': total_genres,
        'recent_manga': recent_manga,
        'recent_chapters': recent_chapters,
        'recent_users': recent_users,
    }
    return render(request, 'admin/dashboard.html', context)


# ---------------------------------------------------------------------------
# Manga CRUD
# ---------------------------------------------------------------------------
@admin_required
def manga_list_admin(request):
    queryset = (
        Manga.objects.annotate(chapter_count=Count('chapters'))
        .order_by('-updated_at')
    )
    q = request.GET.get('q', '').strip()
    if q:
        queryset = queryset.filter(title__icontains=q)

    paginator = Paginator(queryset, 20)
    page = request.GET.get('page', 1)
    manga_page = paginator.get_page(page)

    context = {'manga_list': manga_page, 'query': q}
    return render(request, 'admin/manga_list.html', context)


@admin_required
@csrf_protect
def manga_create(request):
    if request.method == 'POST':
        form = MangaForm(request.POST, request.FILES)
        if form.is_valid():
            manga = form.save()
            messages.success(request, f'"{manga.title}" created successfully.')
            return redirect('admin_manga_list')
    else:
        form = MangaForm()

    context = {'form': form, 'genres': Genre.objects.all(), 'is_edit': False}
    return render(request, 'admin/manga_form.html', context)


@admin_required
@csrf_protect
def manga_edit(request, manga_id):
    manga = get_object_or_404(Manga, id=manga_id)
    if request.method == 'POST':
        form = MangaForm(request.POST, request.FILES, instance=manga)
        if form.is_valid():
            manga = form.save()
            messages.success(request, f'"{manga.title}" updated successfully.')
            return redirect('admin_manga_list')
    else:
        form = MangaForm(instance=manga)

    context = {
        'form': form, 'manga': manga,
        'genres': Genre.objects.all(), 'is_edit': True,
    }
    return render(request, 'admin/manga_form.html', context)


@admin_required
@csrf_protect
@require_http_methods(["POST"])
def manga_delete(request, manga_id):
    manga = get_object_or_404(Manga, id=manga_id)
    title = manga.title
    manga.delete()
    messages.success(request, f'"{title}" deleted successfully.')
    return redirect('admin_manga_list')


# ---------------------------------------------------------------------------
# Chapter CRUD
# ---------------------------------------------------------------------------
@admin_required
def chapter_list_admin(request, manga_id):
    manga = get_object_or_404(Manga, id=manga_id)
    chapters = manga.chapters.annotate(image_count=Count('images')).order_by('-number')
    context = {'manga': manga, 'chapters': chapters}
    return render(request, 'admin/chapter_list.html', context)


@admin_required
@csrf_protect
def chapter_create(request, manga_id):
    manga = get_object_or_404(Manga, id=manga_id)
    if request.method == 'POST':
        form = ChapterForm(request.POST)
        if form.is_valid():
            chapter = form.save(commit=False)
            chapter.manga = manga
            chapter.save()

            images = request.FILES.getlist('images')
            for i, img in enumerate(images):
                ChapterImage.objects.create(chapter=chapter, image=img, order=i)

            manga.save()  # bump updated_at
            messages.success(request, f'Chapter {chapter.number} added successfully.')
            return redirect('admin_chapter_list', manga_id=manga.id)
    else:
        latest = manga.chapters.order_by('-number').first()
        initial_number = (latest.number + 1) if latest else 1
        form = ChapterForm(initial={'number': initial_number})

    context = {'form': form, 'manga': manga, 'is_edit': False}
    return render(request, 'admin/chapter_form.html', context)


@admin_required
@csrf_protect
def chapter_edit(request, manga_id, chapter_id):
    manga = get_object_or_404(Manga, id=manga_id)
    chapter = get_object_or_404(Chapter, id=chapter_id, manga=manga)

    if request.method == 'POST':
        form = ChapterForm(request.POST, instance=chapter)
        if form.is_valid():
            chapter = form.save()

            images = request.FILES.getlist('images')
            if images:
                max_order_obj = chapter.images.order_by('-order').first()
                start_order = (max_order_obj.order + 1) if max_order_obj else 0
                for i, img in enumerate(images):
                    ChapterImage.objects.create(
                        chapter=chapter, image=img, order=start_order + i
                    )

            messages.success(request, f'Chapter {chapter.number} updated.')
            return redirect('admin_chapter_list', manga_id=manga.id)
    else:
        form = ChapterForm(instance=chapter)

    existing_images = chapter.images.order_by('order')
    context = {
        'form': form, 'manga': manga, 'chapter': chapter,
        'existing_images': existing_images, 'is_edit': True,
    }
    return render(request, 'admin/chapter_form.html', context)


@admin_required
@csrf_protect
@require_http_methods(["POST"])
def chapter_delete(request, manga_id, chapter_id):
    manga = get_object_or_404(Manga, id=manga_id)
    chapter = get_object_or_404(Chapter, id=chapter_id, manga=manga)
    number = chapter.number
    chapter.delete()
    messages.success(request, f'Chapter {number} deleted.')
    return redirect('admin_chapter_list', manga_id=manga.id)


@admin_required
@csrf_protect
@require_http_methods(["POST"])
def chapter_image_delete(request, image_id):
    image = get_object_or_404(ChapterImage, id=image_id)
    image.delete()
    return JsonResponse({'success': True})


# ---------------------------------------------------------------------------
# User management
# ---------------------------------------------------------------------------
@admin_required
def users_list_admin(request):
    queryset = UserProfile.objects.all().order_by('-created_at')
    q = request.GET.get('q', '').strip()
    if q:
        queryset = queryset.filter(
            Q(username__icontains=q) | Q(email__icontains=q)
        )

    paginator = Paginator(queryset, 20)
    page = request.GET.get('page', 1)
    users_page = paginator.get_page(page)

    context = {'users': users_page, 'query': q}
    return render(request, 'admin/users_list.html', context)


@admin_required
@csrf_protect
def reset_password_admin(request, user_id):
    target_user = get_object_or_404(UserProfile, id=user_id)
    if request.method == 'POST':
        new_password = request.POST.get('new_password', '')
        confirm_password = request.POST.get('confirm_password', '')

        if not new_password:
            messages.error(request, 'Password cannot be empty.')
        elif new_password != confirm_password:
            messages.error(request, 'Passwords do not match.')
        elif len(new_password) < 8:
            messages.error(request, 'Password must be at least 8 characters.')
        else:
            target_user.set_password(new_password)
            target_user.is_locked = False
            target_user.failed_login_attempts = 0
            target_user.locked_until = None
            target_user.save()
            messages.success(
                request, f'Password for "{target_user.username}" has been reset.'
            )
            return redirect('admin_users')

    context = {'target_user': target_user}
    return render(request, 'admin/reset_password.html', context)


@admin_required
@csrf_protect
@require_http_methods(["POST"])
def toggle_user_status(request, user_id):
    target_user = get_object_or_404(UserProfile, id=user_id)
    target_user.is_active = not target_user.is_active
    if target_user.is_active:
        target_user.is_locked = False
        target_user.locked_until = None
        target_user.failed_login_attempts = 0
    target_user.save()
    status = 'activated' if target_user.is_active else 'deactivated'
    messages.success(request, f'User "{target_user.username}" {status}.')
    return redirect('admin_users')


@admin_required
@csrf_protect
@require_http_methods(["POST"])
def toggle_admin_status(request, user_id):
    target_user = get_object_or_404(UserProfile, id=user_id)
    if target_user.id == request.admin_user.id:
        messages.error(request, 'You cannot change your own admin status.')
        return redirect('admin_users')
    target_user.is_admin = not target_user.is_admin
    target_user.save()
    action = 'granted admin to' if target_user.is_admin else 'removed admin from'
    messages.success(request, f'{action.capitalize()} "{target_user.username}".')
    return redirect('admin_users')


# ---------------------------------------------------------------------------
# Genre management
# ---------------------------------------------------------------------------
@admin_required
@csrf_protect
def genre_manage(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add':
            name = request.POST.get('name', '').strip()
            if name:
                from django.utils.text import slugify
                slug = slugify(name)
                if not Genre.objects.filter(slug=slug).exists():
                    Genre.objects.create(name=name, slug=slug)
                    messages.success(request, f'Genre "{name}" added.')
                else:
                    messages.error(request, f'Genre "{name}" already exists.')
        elif action == 'delete':
            genre_id = request.POST.get('genre_id')
            try:
                Genre.objects.get(id=genre_id).delete()
                messages.success(request, 'Genre deleted.')
            except Genre.DoesNotExist:
                messages.error(request, 'Genre not found.')

    genres = Genre.objects.annotate(manga_count=Count('manga_list')).order_by('name')
    context = {'genres': genres}
    return render(request, 'admin/genres.html', context)
