from django.db import models
from django.utils.text import slugify


class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Manga(models.Model):
    STATUS_CHOICES = [
        ('Ongoing', 'Ongoing'),
        ('Completed', 'Completed'),
        ('Hiatus', 'Hiatus'),
    ]
    TYPE_CHOICES = [
        ('Manga', 'Manga'),
        ('Manhwa', 'Manhwa'),
        ('Manhua', 'Manhua'),
    ]

    title = models.CharField(max_length=500)
    slug = models.SlugField(max_length=500, unique=True, blank=True)
    alt_titles = models.TextField(blank=True, help_text='Alternative titles, one per line')
    description = models.TextField(blank=True)
    cover = models.ImageField(upload_to='manga_covers/', blank=True, null=True)
    cover_url = models.URLField(max_length=500, blank=True, help_text='External cover image URL')
    author = models.CharField(max_length=300, blank=True, default='Unknown')
    artist = models.CharField(max_length=300, blank=True, default='Unknown')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Ongoing')
    manga_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='Manga')
    genres = models.ManyToManyField(Genre, blank=True, related_name='manga_list')
    views = models.PositiveIntegerField(default=0)
    rating = models.FloatField(default=0.0)
    rating_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            original_slug = self.slug
            counter = 1
            while Manga.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f'{original_slug}-{counter}'
                counter += 1
        super().save(*args, **kwargs)

    def get_cover_display(self):
        if self.cover and hasattr(self.cover, 'url'):
            return self.cover.url
        if self.cover_url:
            return self.cover_url
        return '/static/images/default_cover.svg'

    def get_chapter_count(self):
        return self.chapters.count()

    def get_latest_chapter(self):
        return self.chapters.order_by('-number').first()

    def get_bookmark_count(self):
        return self.bookmarked_by.count()

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-updated_at']


class Chapter(models.Model):
    manga = models.ForeignKey(Manga, on_delete=models.CASCADE, related_name='chapters')
    number = models.FloatField()
    title = models.CharField(max_length=300, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_images(self):
        return self.images.order_by('order')

    def get_next_chapter(self):
        return Chapter.objects.filter(
            manga=self.manga, number__gt=self.number
        ).order_by('number').first()

    def get_previous_chapter(self):
        return Chapter.objects.filter(
            manga=self.manga, number__lt=self.number
        ).order_by('-number').first()

    def __str__(self):
        title_part = f' - {self.title}' if self.title else ''
        return f'{self.manga.title} Ch.{self.number}{title_part}'

    class Meta:
        ordering = ['-number']
        unique_together = ['manga', 'number']


class ChapterImage(models.Model):
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='chapter_images/')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'{self.chapter} - Image {self.order}'


class Bookmark(models.Model):
    user = models.ForeignKey(
        'users.UserProfile', on_delete=models.CASCADE, related_name='bookmarks'
    )
    manga = models.ForeignKey(
        Manga, on_delete=models.CASCADE, related_name='bookmarked_by'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'manga']

    def __str__(self):
        return f'{self.user.username} → {self.manga.title}'


class Rating(models.Model):
    user = models.ForeignKey(
        'users.UserProfile', on_delete=models.CASCADE, related_name='manga_ratings'
    )
    manga = models.ForeignKey(
        Manga, on_delete=models.CASCADE, related_name='ratings'
    )
    score = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'manga']

    def __str__(self):
        return f'{self.user.username} rated {self.manga.title}: {self.score}'


class Comment(models.Model):
    user = models.ForeignKey(
        'users.UserProfile', on_delete=models.CASCADE, related_name='manga_comments'
    )
    manga = models.ForeignKey(
        Manga, on_delete=models.CASCADE, related_name='comments'
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} on {self.manga.title}'
