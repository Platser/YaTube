from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Group, Follow, Post, User
from .utils import get_posts_page


def index(request):
    """
    Главная страница проложеия post.
    Показывает 10 последних записей сообщества.
    """
    page_obj = get_posts_page(
        request,
        Post.objects.all()
    )
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    """
    Страница группы.
    Показывает 10 последних записей группы.
    """
    group = get_object_or_404(Group, slug=slug)
    page_obj = get_posts_page(
        request,
        group.posts.all(),
    )
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    user = get_object_or_404(get_user_model(), username=username)
    page_obj = get_posts_page(
        request,
        user.posts.all(),
    )
    following = False
    if (request.user.is_authenticated
            and Follow.objects.filter(user=request.user, author=user)):
        following = True
    context = {
        'author': user,
        'page_obj': page_obj,
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(
        request.POST or None,
    )
    comments = post.comments.all()
    context = {
        'post': post,
        'form': form,
        'comments': comments,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None
    )
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect("posts:profile", username=request.user.username)
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect("posts:post_detail", post_id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect("posts:post_detail", post_id=post_id)
    return render(
        request,
        'posts/create_post.html',
        {'form': form, 'is_edit': True},
    )


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    """
    Отображает список постов авторов на которые подписан пользователь
    """
    following = list(
        f.author for f in list(Follow.objects.filter(user=request.user))
    )
    # following = list(
    #     f.author for f in list(request.user.following.all())
    # )
    page_obj = get_posts_page(
        request,
        Post.objects.filter(author__in=following)
    )
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    """
    Обработка запроса подписки на автора
    """
    author = get_object_or_404(User, username=username)
    Follow.objects.create(user=request.user, author=author)
    return redirect(request.META.get('HTTP_REFERER'))


@login_required
def profile_unfollow(request, username):
    """
    Обработка запроса отписки от автора
    """
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user, author=author).delete()
    return redirect(request.META.get('HTTP_REFERER'))
