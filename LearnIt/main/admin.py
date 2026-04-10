from django.contrib import admin
from .models import Profile, Community, Post, Comment

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'points', 'created_at')
    search_fields = ('user__username', 'user__email')


@admin.register(Community)
class CommunityAdmin(admin.ModelAdmin):
    list_display = ('name', 'admin', 'is_public', 'member_count', 'created_at')
    list_filter = ('is_public',)
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}

    def member_count(self, obj):
        return obj.members.count()
    member_count.short_description = 'Members'


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'community', 'author', 'is_solved', 'reward_points', 'created_at')
    list_filter = ('is_solved', 'community')
    search_fields = ('title', 'description')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'post', 'is_correct', 'created_at')
    list_filter = ('is_correct',)