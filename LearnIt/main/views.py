from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Profile, Community, Post, Comment
from django.db.models import Count

# ====================== AUTH VIEWS ======================

def home(request):
    if request.user.is_authenticated:
        return redirect('explore_communities')
    return render(request, 'home.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('explore_communities')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('explore_communities')
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('home')


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('explore_communities')

    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        intro = request.POST.get('intro', '')

        # Validation
        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return render(request, 'signup.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken!")
            return render(request, 'signup.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered!")
            return render(request, 'signup.html')

        # Create User
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name
            )

            # Create Profile
            profile = Profile.objects.create(
                user=user,
                points=300,
                intro=intro
            )

            # Handle Avatar upload
            if 'avatar' in request.FILES:
                profile.avatar = request.FILES['avatar']
            
            # Handle Character Image upload
            if 'character_image' in request.FILES:
                profile.character_image = request.FILES['character_image']
            
            profile.save()

            # Auto login after signup
            login(request, user)
            messages.success(request, "Account created! You received 300 points 🎉")
            return redirect('explore_communities')

        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
            return render(request, 'signup.html')

    return render(request, 'signup.html')

@login_required
def explore_communities(request):
    query = request.GET.get('q', '')
    if query:
        communities = Community.objects.filter(name__icontains=query)
    else:
        communities = Community.objects.annotate(members_count=Count('members')).order_by('-members_count')[:20]
    
    return render(request, 'explore.html', {'communities': communities, 'query': query})

@login_required
def upload_redirect(request):
    messages.info(request, "Select a community first, then post your problem.")
    return redirect('explore_communities')

@login_required
def create_community(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        is_private = request.POST.get('is_private') == 'on'
        is_public = not is_private
        join_code = request.POST.get('join_code', '').strip()
        
        if not name or not description:
            messages.error(request, "Community name and description are required.")
            return render(request, 'create_community.html')
        
        if is_private and not join_code:
            messages.error(request, "Join code is required for private communities.")
            return render(request, 'create_community.html')
        
        community = Community.objects.create(
            name=name,
            description=description,
            is_public=is_public,
            join_code=join_code if is_private else None,
            admin=request.user
        )
        community.members.add(request.user)  # Creator joins automatically
        messages.success(request, f'Community "{name}" created!')
        return redirect('community_detail', slug=community.slug)
    
    return render(request, 'create_community.html')

@login_required
def community_detail(request, slug):
    community = get_object_or_404(Community, slug=slug)
    is_member = community.members.filter(id=request.user.id).exists()
    
    if not community.is_public and not is_member and community.admin != request.user:
        if request.method == 'POST':
            code = request.POST.get('join_code', '').strip()
            if code and code == community.join_code:
                community.members.add(request.user)
                messages.success(request, f"Joined {community.name}!")
                return redirect('community_detail', slug=slug)
            else:
                messages.error(request, "Invalid join code.")
        return render(request, 'join_private.html', {'community': community})
    
    posts = community.posts.all().order_by('-created_at')
    return render(request, 'community.html', {
        'community': community,
        'posts': posts,
        'is_member': is_member
    })

@login_required
def join_community(request, slug):
    community = get_object_or_404(Community, slug=slug)
    if community.is_public:
        community.members.add(request.user)
        messages.success(request, f"Joined {community.name}")
    else:
        # Private - you can add join code logic here later
        messages.info(request, "Private community - join code required (feature coming)")
    return redirect('community_detail', slug=slug)

@login_required
def upload_post(request, slug):
    community = get_object_or_404(Community, slug=slug)
    if request.user.profile.points < 10:
        messages.error(request, "You need at least 10 points to post.")
        return redirect('community_detail', slug=slug)

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        
        if not title or not description:
            messages.error(request, "Title and description are required.")
            return render(request, 'upload.html', {'community': community})
        
        post = Post.objects.create(
            community=community,
            author=request.user,
            title=title,
            description=description,
            code=request.POST.get('code', ''),
            error_message=request.POST.get('error_message', ''),
            reward_points=int(request.POST.get('reward_points', 10)),
        )
        request.user.profile.points -= 10
        request.user.profile.save()
        messages.success(request, "Problem posted!")
        return redirect('post_detail', post_id=post.id)
    
    return render(request, 'upload.html', {'community': community})

@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.method != 'POST':
        return redirect('post_detail', post_id=post.id)

    if request.user == post.author:
        messages.error(request, "You cannot comment on your own problem.")
        return redirect('post_detail', post_id=post.id)

    if post.is_solved:
        messages.warning(request, "This problem has already been solved.")
        return redirect('post_detail', post_id=post.id)

    body = request.POST.get('body', '').strip()
    code = request.POST.get('code', '').strip()
    file = request.FILES.get('file')

    if not body:
        messages.error(request, "Solution description is required.")
        return redirect('post_detail', post_id=post.id)

    comment = Comment.objects.create(
        post=post,
        author=request.user,
        body=body,
        code=code,
    )

    if file:
        comment.file = file
        comment.save()

    messages.success(request, "Solution submitted successfully.")
    return redirect('post_detail', post_id=post.id)

@login_required
def mark_comment_correct(request, post_id, comment_id):
    post = get_object_or_404(Post, id=post_id)
    comment = get_object_or_404(Comment, id=comment_id, post=post)

    if request.method != 'POST':
        return redirect('post_detail', post_id=post.id)

    if request.user != post.author:
        messages.error(request, "Only the post author can mark a solution as correct.")
        return redirect('post_detail', post_id=post.id)

    if post.is_solved:
        messages.warning(request, "This problem is already solved.")
        return redirect('post_detail', post_id=post.id)

    try:
        award_points = int(request.POST.get('points', post.reward_points))
    except (TypeError, ValueError):
        award_points = post.reward_points

    if award_points < 10:
        award_points = 10

    if request.user.profile.points < award_points:
        messages.error(request, "You do not have enough points to award this solution.")
        return redirect('post_detail', post_id=post.id)

    request.user.profile.points -= award_points
    request.user.profile.save()

    comment.author.profile.points += award_points
    comment.author.profile.save()

    comment.is_correct = True
    comment.save()
    post.is_solved = True
    post.correct_comment = comment
    post.reward_points = award_points
    post.save()

    messages.success(request, f"Solution marked correct and {award_points} points awarded.")
    return redirect('post_detail', post_id=post.id)

@login_required
def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    return render(request, 'post_detail.html', {'post': post})

@login_required
def profile(request):
    return redirect('user_profile', username=request.user.username)

@login_required
def user_profile(request, username):
    user = get_object_or_404(User, username=username)
    profile = user.profile
    communities = user.joined_communities.all()
    posts = user.posts.all()
    
    is_own_profile = (user == request.user)
    
    return render(request, 'profile.html', {
        'profile': profile,
        'communities': communities,
        'posts': posts,
        'is_own_profile': is_own_profile
    })

@login_required
def edit_profile(request):
    profile = request.user.profile
    
    if request.method == 'POST':
        # Update bio/intro
        if 'intro' in request.POST:
            profile.intro = request.POST.get('intro', '')
        
        # Handle avatar upload
        if 'avatar' in request.FILES:
            profile.avatar = request.FILES['avatar']
        
        # Handle character image upload
        if 'character_image' in request.FILES:
            profile.character_image = request.FILES['character_image']
        
        profile.save()
        messages.success(request, "Profile updated successfully!")
        return redirect('user_profile', username=request.user.username)
    
    return render(request, 'edit_profile.html', {'profile': profile})