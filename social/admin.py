from django.contrib import admin

from .models import Post, Comment, Profile


class ProfileAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False


admin.site.register(Profile, ProfileAdmin)
admin.site.register(Post)
admin.site.register(Comment)
