# 🎬 MangaDox — CRUD Operations Video Presentation Guide

**Duration:** 4–5 minutes (target ~4:30)
**Project:** MangaDox — A Manga Reading Platform built with Django + SQLite3
**Deployed:** https://mangadox.onrender.com
**GitHub:** MrDNightCore/MangaDox

---

## 📋 Talking Points Outline

| Segment | Duration | What to Show |
|---------|----------|-------------|
| 1. Intro & Project Overview | ~0:30 | Title slide / Homepage |
| 2. CREATE — Add a Manga | ~1:00 | Admin panel → Add Manga form |
| 3. READ — Browse & View Manga | ~0:45 | Public browse page → Manga detail |
| 4. UPDATE — Edit Manga Details | ~0:45 | Admin panel → Edit form |
| 5. DELETE — Remove a Manga | ~0:30 | Admin panel → Delete confirmation |
| 6. Bonus CRUD (Comments/Bookmarks) | ~0:30 | User interactions on manga detail |
| 7. Wrap-Up & Tech Stack | ~0:30 | Summary slide |

---

## 🎙️ Script / Narration Guide

---

### SEGMENT 1 — Introduction (~0:30)

**Action:** Show the homepage at `/`

**Say:**
> "Hi, I'm [Your Name], and today I'll be demonstrating the CRUD operations in my project — MangaDox, a manga reading platform built with Python Django and SQLite3. CRUD stands for Create, Read, Update, and Delete. Let me walk you through each operation."

**Screen:** Navigate to the home page showing popular manga and latest updates.VX

---

### SEGMENT 2 — CREATE Operation (~1:00)

**Action:** Navigate to Admin Panel → Add Manga

**Steps to show on screen:**
1. Go to `/panel/` (Admin Dashboard) — show the stats briefly
2. Click **Manga** list → click **Add Manga** (`/panel/manga/add/`)
3. Fill in the form fields:
   - **Title:** "Solo Leveling"
   - **Description:** A short synopsis
   - **Author / Artist:** "Chugong / Dubu"
   - **Status:** Ongoing
   - **Type:** Manhwa
   - **Genres:** Check Action, Fantasy
   - **Cover URL:** Paste an image link
4. Click **Save** — show the success message

**Say:**
> "For the CREATE operation, I'll use the admin panel. Here's our dashboard showing site statistics. Let me add a new manga. I fill in the title, description, author, select the status and type, pick genres, and provide a cover image. Once I hit save — the manga is now created and appears in our list."

**Key Code Reference:**
- View: `manga/admin_views.py` → `manga_create()` (line 122–134)
- Form: `manga/forms.py` → `MangaForm`
- Model: `manga/models.py` → `Manga` model (line 21–80)

---

### SEGMENT 3 — READ Operation (~0:45)

**Action:** Navigate to public pages to show data retrieval

**Steps to show on screen:**
1. Go to **Browse** page (`/browse/`) — show the manga grid with pagination
2. Use the **search bar** — type a title and show results
3. Click on a manga → show the **Manga Detail** page (`/manga/<slug>/`)
   - Title, cover, description, genres, chapters, comments, ratings
4. (Optional) Open a **Chapter Reader** (`/manga/<slug>/chapter/1/`) — show images

**Say:**
> "For the READ operation — users can browse all manga with search, filter by genre, status, or type, and sort results. Clicking on a manga shows its detail page with the full description, chapter list, and community features like ratings and comments. Users can also read chapters through our built-in reader."

**Key Code Reference:**
- View: `manga/views.py` → `manga_list()` (line 39–90), `manga_detail()` (line 93–121)
- URL: `/browse/`, `/manga/<slug>/`

---

### SEGMENT 4 — UPDATE Operation (~0:45)

**Action:** Navigate to Admin Panel → Edit the manga you just created

**Steps to show on screen:**
1. Go to `/panel/manga/` — find the manga in the list
2. Click the **Edit** button → opens `/panel/manga/<id>/edit/`
3. Change something visible:
   - Update the **Status** from "Ongoing" → "Completed"
   - Edit the **Description** — add more text
4. Click **Save** — show the success message
5. Go to the **public manga detail page** to show the updated data live

**Say:**
> "For the UPDATE operation, I go back to the admin panel, find the manga, and click edit. I'll change the status from Ongoing to Completed and update the description. After saving, you can see the changes reflected immediately on the public page."

**Key Code Reference:**
- View: `manga/admin_views.py` → `manga_edit()` (line 137–154)
- Uses same `MangaForm` with `instance=manga` for pre-populated fields

---

### SEGMENT 5 — DELETE Operation (~0:30)

**Action:** Delete a manga from Admin Panel

**Steps to show on screen:**
1. Go to `/panel/manga/`
2. Click the **Delete** button on the manga
3. Confirm the deletion
4. Show the success message and the manga gone from the list
5. (Optional) Go to `/browse/` to verify it's removed from public pages

**Say:**
> "Finally, the DELETE operation. From the admin panel, I click delete on the manga entry, confirm it, and the manga along with all its chapters and images is permanently removed from the database. It no longer appears in the browse page."

**Key Code Reference:**
- View: `manga/admin_views.py` → `manga_delete()` (line 157–165)
- Uses `CASCADE` deletion — chapters and images are auto-deleted

---

### SEGMENT 6 — Bonus CRUD: User Interactions (~0:30)

**Action:** Show user-side CRUD (comments, bookmarks, ratings)

**Steps to show on screen (pick 1-2):**
- **Bookmark** a manga (toggle on/off) → CREATE/DELETE via AJAX
- **Rate** a manga (1-5 stars) → CREATE/UPDATE via AJAX
- **Comment** on a manga → CREATE via AJAX

**Say:**
> "Beyond the admin panel, users also perform CRUD operations. They can bookmark manga, rate them, and leave comments — all handled through AJAX requests for a smooth experience."

**Key Code Reference:**
- `manga/views.py` → `toggle_bookmark()`, `rate_manga()`, `add_comment()`

---

### SEGMENT 7 — Wrap-Up (~0:30)

**Action:** Show a summary (or just speak over the homepage)

**Say:**
> "To summarize — MangaDox implements full CRUD operations: Creating manga through the admin panel, Reading them on public browse and detail pages, Updating manga details through edit forms, and Deleting entries from the admin panel. The project is built with Django, uses SQLite3 for the database, vanilla CSS for styling, and is deployed on Render. Thank you for watching!"

---

## 🛠️ Tech Stack Summary (for title/end slide)

| Component | Technology |
|-----------|-----------|
| Backend | Python 3.14 + Django |
| Database | SQLite3 |
| Frontend | Django Templates + Vanilla CSS |
| Icons | Font Awesome |
| Deployment | Render (https://mangadox.onrender.com) |
| Auth | Custom session-based with rate limiting |

---

## 📂 Key Files to Mention / Show in Code (if needed)

| File | Purpose |
|------|---------|
| `manga/models.py` | Manga, Chapter, Bookmark, Rating, Comment models |
| `manga/admin_views.py` | All admin CRUD views (create, edit, delete) |
| `manga/views.py` | Public read views + AJAX endpoints |
| `manga/forms.py` | Django ModelForms for Manga and Chapter |
| `manga/urls.py` | All URL routing (public + admin panel) |
| `users/models.py` | UserProfile model with security features |
| `users/views.py` | Login, Register, Logout views |

---

## ⏱️ Timing Tips

- **Practice once** with a timer — aim for 4:00 on your first dry run
- **Don't show code** unless specifically required — focus on the live demo
- **Pre-seed data** — have some manga already in the database so browse/read pages look good
- **Stay logged in** as admin before recording to save time
- **Use keyboard shortcuts** to navigate faster (Ctrl+L for address bar)
- If you go under 4 min, expand Segment 6 (show all 3: bookmark, rate, comment)
- If you go over 5 min, skip Segment 6 entirely

---

## 🎯 Quick URL Reference

| Page | URL |
|------|-----|
| Homepage | `/` |
| Browse Manga | `/browse/` |
| Manga Detail | `/manga/<slug>/` |
| Chapter Reader | `/manga/<slug>/chapter/<number>/` |
| Admin Dashboard | `/panel/` |
| Admin Manga List | `/panel/manga/` |
| Add Manga | `/panel/manga/add/` |
| Edit Manga | `/panel/manga/<id>/edit/` |
| Admin Users | `/panel/users/` |
| Admin Genres | `/panel/genres/` |

---

**Good luck with the presentation! 🎤**
