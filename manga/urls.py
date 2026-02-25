from django.urls import path
from . import views
from . import admin_views

urlpatterns = [
    # Public pages
    path('', views.home, name='home'),
    path('updates/', views.updates, name='updates'),
    path('browse/', views.manga_list, name='manga_list'),
    path('manga/<slug:slug>/', views.manga_detail, name='manga_detail'),
    path('manga/<slug:slug>/chapter/<str:number>/', views.chapter_reader, name='chapter_reader'),
    path('bookmarks/', views.bookmarks_page, name='bookmarks'),

    # API endpoints
    path('api/bookmark/toggle/', views.toggle_bookmark, name='toggle_bookmark'),
    path('api/rate/', views.rate_manga, name='rate_manga'),
    path('api/comment/add/', views.add_comment, name='add_comment'),
    path('api/search/', views.search_ajax, name='search_ajax'),

    # Admin panel
    path('panel/', admin_views.dashboard, name='admin_dashboard'),
    path('panel/manga/', admin_views.manga_list_admin, name='admin_manga_list'),
    path('panel/manga/add/', admin_views.manga_create, name='admin_manga_create'),
    path('panel/manga/<int:manga_id>/edit/', admin_views.manga_edit, name='admin_manga_edit'),
    path('panel/manga/<int:manga_id>/delete/', admin_views.manga_delete, name='admin_manga_delete'),
    path('panel/manga/<int:manga_id>/chapters/', admin_views.chapter_list_admin, name='admin_chapter_list'),
    path('panel/manga/<int:manga_id>/chapters/add/', admin_views.chapter_create, name='admin_chapter_create'),
    path('panel/manga/<int:manga_id>/chapters/<int:chapter_id>/edit/', admin_views.chapter_edit, name='admin_chapter_edit'),
    path('panel/manga/<int:manga_id>/chapters/<int:chapter_id>/delete/', admin_views.chapter_delete, name='admin_chapter_delete'),
    path('panel/chapter-image/<int:image_id>/delete/', admin_views.chapter_image_delete, name='admin_chapter_image_delete'),
    path('panel/users/', admin_views.users_list_admin, name='admin_users'),
    path('panel/users/<int:user_id>/reset-password/', admin_views.reset_password_admin, name='admin_reset_password'),
    path('panel/users/<int:user_id>/toggle-status/', admin_views.toggle_user_status, name='admin_toggle_user_status'),
    path('panel/users/<int:user_id>/toggle-admin/', admin_views.toggle_admin_status, name='admin_toggle_admin_status'),
    path('panel/genres/', admin_views.genre_manage, name='admin_genres'),
]
