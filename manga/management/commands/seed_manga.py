"""
Management command to seed the database with sample manga data.
Usage: python manage.py seed_manga
"""
import random
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from manga.models import Genre, Manga, Chapter
from users.models import UserProfile


GENRES = [
    'Action', 'Adventure', 'Comedy', 'Drama', 'Fantasy',
    'Horror', 'Isekai', 'Martial Arts', 'Romance', 'Sci-Fi',
    'Seinen', 'Shounen', 'Slice of Life', 'Supernatural', 'Thriller',
    'Mystery', 'School Life', 'Historical', 'Mecha', 'Sports',
]

MANGA_DATA = [
    {
        'title': 'Crimson Blade Chronicles',
        'desc': 'A young swordsman discovers an ancient crimson blade that grants immense power but slowly consumes the wielder\'s soul. To save his village from destruction, he must master the blade before it masters him.',
        'type': 'Manhwa', 'status': 'Ongoing',
        'genres': ['Action', 'Fantasy', 'Adventure'],
        'cover': 'https://picsum.photos/seed/crimson/300/420',
    },
    {
        'title': 'Midnight Academy',
        'desc': 'At a prestigious academy hidden between dimensions, students learn to harness supernatural abilities. When a forbidden experiment goes wrong, a group of misfits must prevent reality from unraveling.',
        'type': 'Manga', 'status': 'Ongoing',
        'genres': ['Fantasy', 'School Life', 'Supernatural'],
        'cover': 'https://picsum.photos/seed/academy/300/420',
    },
    {
        'title': 'Dragon Emperor Reborn',
        'desc': 'The most powerful dragon emperor is reincarnated as a human child in a world where dragons are hunted to extinction. He must rebuild his strength and unite the remaining dragons.',
        'type': 'Manhua', 'status': 'Ongoing',
        'genres': ['Action', 'Fantasy', 'Martial Arts', 'Isekai'],
        'cover': 'https://picsum.photos/seed/dragon/300/420',
    },
    {
        'title': 'Silent Whispers',
        'desc': 'A detective with the ability to hear the thoughts of the dead investigates a string of murders in a quiet coastal town. Each victim leads closer to a conspiracy that could shake the nation.',
        'type': 'Manga', 'status': 'Completed',
        'genres': ['Mystery', 'Thriller', 'Drama'],
        'cover': 'https://picsum.photos/seed/whispers/300/420',
    },
    {
        'title': 'Stellar Vanguard',
        'desc': 'In the year 3000, humanity has colonized the stars. When an alien threat emerges from beyond known space, a ragtag crew of misfits becomes humanity\'s last hope.',
        'type': 'Manhwa', 'status': 'Ongoing',
        'genres': ['Sci-Fi', 'Action', 'Adventure'],
        'cover': 'https://picsum.photos/seed/stellar/300/420',
    },
    {
        'title': 'Love & Lattes',
        'desc': 'A struggling barista and a cold-hearted CEO keep bumping into each other at the same cafe. What starts as mutual annoyance slowly turns into something neither expected.',
        'type': 'Manhwa', 'status': 'Ongoing',
        'genres': ['Romance', 'Comedy', 'Slice of Life'],
        'cover': 'https://picsum.photos/seed/latte/300/420',
    },
    {
        'title': 'Ironclad Warrior',
        'desc': 'Cast out from his clan for lacking talent, a young martial artist discovers an ancient iron body technique in a forgotten cave. His journey to the top of the martial world begins.',
        'type': 'Manhua', 'status': 'Ongoing',
        'genres': ['Martial Arts', 'Action', 'Fantasy'],
        'cover': 'https://picsum.photos/seed/ironclad/300/420',
    },
    {
        'title': 'Phantom Thief Luna',
        'desc': 'By day she is an ordinary high school student. By night she is Luna, a phantom thief who steals cursed artifacts to protect the world from their dark influence.',
        'type': 'Manga', 'status': 'Completed',
        'genres': ['Action', 'Supernatural', 'School Life', 'Comedy'],
        'cover': 'https://picsum.photos/seed/phantom/300/420',
    },
    {
        'title': 'Abyss Walker',
        'desc': 'Dungeons appeared across the world, and with them came monsters. Hunters delve into the abyss for fortune and glory. One E-rank hunter discovers he can absorb monster abilities.',
        'type': 'Manhwa', 'status': 'Ongoing',
        'genres': ['Action', 'Fantasy', 'Adventure', 'Seinen'],
        'cover': 'https://picsum.photos/seed/abyss/300/420',
    },
    {
        'title': 'Chef\'s Grand Tour',
        'desc': 'A world-class chef loses his sense of taste after an accident. He embarks on a journey across cultures and cuisines to rediscover what food truly means.',
        'type': 'Manga', 'status': 'Ongoing',
        'genres': ['Slice of Life', 'Drama', 'Comedy'],
        'cover': 'https://picsum.photos/seed/chef/300/420',
    },
    {
        'title': 'Shadow Monarch\'s Return',
        'desc': 'The Shadow Monarch, sealed for a thousand years, awakens in the body of the weakest student at a magic academy. With his ancient knowledge, he begins his climb back to power.',
        'type': 'Manhwa', 'status': 'Ongoing',
        'genres': ['Fantasy', 'Action', 'Isekai', 'Shounen'],
        'cover': 'https://picsum.photos/seed/shadow/300/420',
    },
    {
        'title': 'Eternal Garden',
        'desc': 'In a world where flowers grant magical abilities, a young gardener tends to the legendary Eternal Garden. But dark forces seek to corrupt its power for themselves.',
        'type': 'Manga', 'status': 'Hiatus',
        'genres': ['Fantasy', 'Romance', 'Supernatural'],
        'cover': 'https://picsum.photos/seed/garden/300/420',
    },
    {
        'title': 'Cyber Ronin 2099',
        'desc': 'In a neon-drenched cyberpunk city, a ronin hacker fights corporate corruption with a plasma katana and neural implants. Justice has a new face in the digital age.',
        'type': 'Manga', 'status': 'Ongoing',
        'genres': ['Sci-Fi', 'Action', 'Thriller', 'Seinen'],
        'cover': 'https://picsum.photos/seed/cyberronin/300/420',
    },
    {
        'title': 'Spirit Beast Tamer',
        'desc': 'In a world where humans bond with spirit beasts, a young orphan discovers he can tame legendary beasts that others consider untamable. His destiny is to unite all realms.',
        'type': 'Manhua', 'status': 'Ongoing',
        'genres': ['Fantasy', 'Adventure', 'Action', 'Shounen'],
        'cover': 'https://picsum.photos/seed/spiritbeast/300/420',
    },
    {
        'title': 'Heartstrings',
        'desc': 'Two musicians from completely different backgrounds are forced to work together for a national competition. Their clashing personalities hide a growing mutual respect and affection.',
        'type': 'Manhwa', 'status': 'Completed',
        'genres': ['Romance', 'Drama', 'Slice of Life'],
        'cover': 'https://picsum.photos/seed/heartstrings/300/420',
    },
]


class Command(BaseCommand):
    help = 'Seeds the database with sample manga, genres, chapters, and an admin user.'

    def handle(self, *args, **options):
        self.stdout.write('Seeding genres...')
        genre_map = {}
        for name in GENRES:
            genre, _ = Genre.objects.get_or_create(name=name, defaults={'slug': slugify(name)})
            genre_map[name] = genre

        self.stdout.write('Seeding manga...')
        for data in MANGA_DATA:
            slug = slugify(data['title'])
            if Manga.objects.filter(slug=slug).exists():
                self.stdout.write(f'  Skipping "{data["title"]}" (already exists)')
                continue

            manga = Manga.objects.create(
                title=data['title'],
                slug=slug,
                description=data['desc'],
                cover_url=data['cover'],
                author=random.choice(['Kim Soo-jin', 'Tanaka Yuki', 'Li Wei', 'Park Min-ho', 'Sato Kenji']),
                artist=random.choice(['Studio Phoenix', 'Moonlight Art', 'Dragon Brush', 'Digital Dreams']),
                status=data['status'],
                manga_type=data['type'],
                views=random.randint(1000, 500000),
                rating=round(random.uniform(3.0, 5.0), 1),
                rating_count=random.randint(10, 500),
            )
            for gname in data['genres']:
                if gname in genre_map:
                    manga.genres.add(genre_map[gname])

            num_chapters = random.randint(5, 30)
            for i in range(1, num_chapters + 1):
                Chapter.objects.get_or_create(
                    manga=manga, number=i,
                    defaults={'title': f'Episode {i}' if random.random() > 0.5 else ''}
                )

            self.stdout.write(f'  Created "{data["title"]}" with {num_chapters} chapters')

        # Create admin user if none exists
        if not UserProfile.objects.filter(is_admin=True).exists():
            admin, created = UserProfile.objects.get_or_create(
                username='admin',
                defaults={
                    'email': 'admin@mangadox.com',
                    'is_admin': True,
                    'is_active': True,
                }
            )
            if created:
                admin.set_password('Admin@1234!')
                admin.save()
                self.stdout.write(self.style.SUCCESS(
                    'Admin user created: username=admin, password=Admin@1234!'
                ))
            else:
                admin.is_admin = True
                admin.save()
                self.stdout.write('Existing "admin" user promoted to admin.')

        self.stdout.write(self.style.SUCCESS('Seeding complete!'))
