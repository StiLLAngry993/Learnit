from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    points = models.IntegerField(default=300)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    character_image = models.ImageField(upload_to='characters/', blank=True, null=True)
    intro = models.TextField(blank=True, default="No intro yet.")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class Community(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    is_public = models.BooleanField(default=True)
    join_code = models.CharField(max_length=20, blank=True, null=True)
    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin_communities')
    members = models.ManyToManyField(User, related_name='joined_communities', blank=True)
    rating = models.FloatField(default=0.0)
    total_ratings = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Post(models.Model):
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='posts')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    title = models.CharField(max_length=200)
    description = models.TextField()
    code = models.TextField(blank=True)
    error_message = models.TextField(blank=True)
    file = models.FileField(upload_to='posts/', blank=True, null=True)
    reward_points = models.IntegerField(default=10)
    is_solved = models.BooleanField(default=False)
    correct_comment = models.ForeignKey('Comment', on_delete=models.SET_NULL, blank=True, null=True, related_name='correct_for')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField()
    code = models.TextField(blank=True)
    file = models.FileField(upload_to='solutions/', blank=True, null=True)
    is_correct = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author.username}"