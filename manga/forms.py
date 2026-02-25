from django import forms
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
                'class': 'form-input', 'placeholder': 'https://...',
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
