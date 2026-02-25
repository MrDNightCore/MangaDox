from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
	"""
	Admin interface for UserProfile with security features.
	
	Security features:
	- Display account lock status
	- Show failed login attempts
	- Display last login
	- Prevent direct password editing
	"""
	list_display = ("id", "username", "email", "is_active", "is_locked", "failed_login_attempts", "last_login", "created_at")
	list_filter = ("is_active", "is_locked", "created_at")
	search_fields = ("username", "email")
	readonly_fields = ("password", "created_at", "updated_at", "last_login", "failed_login_attempts")
	
	fieldsets = (
		("User Information", {
			"fields": ("username", "email", "is_active")
		}),
		("Password", {
			"fields": ("password",),
			"classes": ("collapse",),
			"description": "Password is hashed and cannot be edited directly. Use password reset instead."
		}),
		("Account Status", {
			"fields": ("is_locked", "locked_until", "failed_login_attempts"),
		}),
		("Activity", {
			"fields": ("created_at", "updated_at", "last_login"),
		}),
	)
	
	actions = ["unlock_accounts", "deactivate_users", "activate_users"]
	
	def unlock_accounts(self, request, queryset):
		"""Admin action to unlock locked accounts."""
		count = 0
		for user in queryset:
			if user.is_locked:
				user.is_locked = False
				user.locked_until = None
				user.failed_login_attempts = 0
				user.save()
				count += 1
		self.message_user(request, f"{count} account(s) unlocked.")
	unlock_accounts.short_description = "Unlock selected accounts"
	
	def deactivate_users(self, request, queryset):
		"""Admin action to deactivate users."""
		count = queryset.update(is_active=False)
		self.message_user(request, f"{count} user(s) deactivated.")
	deactivate_users.short_description = "Deactivate selected users"
	
	def activate_users(self, request, queryset):
		"""Admin action to activate users."""
		count = queryset.update(is_active=True)
		self.message_user(request, f"{count} user(s) activated.")
	activate_users.short_description = "Activate selected users"
