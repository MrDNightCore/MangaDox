from django import forms

from .image_urls import is_direct_image_url
from .models import Manga, Chapter, Genre


class MangaForm(forms.ModelForm):
    genres = forms.ModelMultipleChoiceField(
        queryset=Genre.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    class Meta:
        model = Manga
        fields = [
            'title', 'alt_titles', 'description', 'cover', 'cover_url',
            'author', 'artist', 'status', 'manga_type', 'genres',
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-input', 'placeholder': 'Manga title',
            }),
            'alt_titles': forms.Textarea(attrs={
                'class': 'form-input', 'rows': 3,
                'placeholder': 'Alternative titles, one per line',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-input', 'rows': 5,
                'placeholder': 'Synopsis / description',
            }),
            'cover_url': forms.URLInput(attrs={
                'class': 'form-input',
                'placeholder': 'https://example.com/cover.jpg',
            }),
            'author': forms.TextInput(attrs={
                'class': 'form-input', 'placeholder': 'Author name',
            }),
            'artist': forms.TextInput(attrs={
                'class': 'form-input', 'placeholder': 'Artist name',
            }),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'manga_type': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_cover_url(self):
        """Reject page links so covers never render as a broken image."""
        cover_url = (self.cleaned_data.get('cover_url') or '').strip()
        if cover_url and not is_direct_image_url(cover_url):
            raise forms.ValidationError(
                'This must be a direct link to an image file (ending in .jpg, '
                '.png, .webp, …). Links to a web page — for example a Pinterest '
                'pin — cannot be displayed. Right-click the image and choose '
                '"Copy image address", or upload the cover file instead.'
            )
        return cover_url


class ChapterForm(forms.ModelForm):
    class Meta:
        model = Chapter
        fields = ['number', 'title']
        widgets = {
            'number': forms.NumberInput(attrs={
                'class': 'form-input', 'step': '0.1',
                'placeholder': 'Chapter number',
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Chapter title (optional)',
            }),
        }
