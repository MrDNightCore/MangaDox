from django.contrib import admin
from .models import Manga, Genre, Chapter, ChapterImage, Bookmark, Rating, Comment


class ChapterImageInline(admin.TabularInline):
    model = ChapterImage
    extra = 1


class ChapterInline(admin.TabularInline):
    model = Chapter
    extra = 0
    show_change_link = True


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Manga)
class MangaAdmin(admin.ModelAdmin):
    list_display = ('title', 'manga_type', 'status', 'views', 'rating', 'created_at')
    list_filter = ('status', 'manga_type', 'genres')
    search_fields = ('title', 'alt_titles', 'author')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('genres',)
    inlines = [ChapterInline]


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ('manga', 'number', 'title', 'created_at')
    list_filter = ('manga',)
    inlines = [ChapterImageInline]


@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ('user', 'manga', 'created_at')


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('user', 'manga', 'score', 'created_at')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'manga', 'created_at')
    list_filter = ('manga',)
