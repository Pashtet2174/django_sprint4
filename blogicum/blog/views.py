from core.constans import NUMBER_OF_POSTS
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import CommentForm, PostForm
from .models import Category, Comment, Post

User = get_user_model()


def index(request):
    template = "blog/index.html"

    post_list = Post.objects.published()

    paginator = Paginator(post_list, NUMBER_OF_POSTS)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {"page_obj": page_obj}
    return render(request, template, context)


def post_detail(request, pk):
    template = "blog/detail.html"

    post = get_object_or_404(
        Post.objects.select_related("author", "category", "location"), pk=pk
    )

    # Проверка доступа к посту
    can_view = True

    # Пост не опубликован
    if not post.is_published:
        can_view = (request.user == post.author)

    # Пост с будущей датой публикации
    elif post.pub_date > timezone.now():
        can_view = (request.user == post.author)

    # Категория не опубликована (ВАЖНО: добавить эту проверку)
    elif not post.category.is_published:
        can_view = (request.user == post.author)

    if not can_view:
        from django.http import Http404
        raise Http404("Пост не найден")

    comments = post.comments.all().select_related("author")

    if request.method == "POST" and request.user.is_authenticated:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            messages.success(request, "Комментарий успешно добавлен!")
            return redirect("blog:post_detail", pk=post.pk)
    else:
        comment_form = CommentForm()

    context = {
        "post": post,
        "comments": comments,
        "form": comment_form,
    }

    return render(request, template, context)


def category_posts(request, cs):
    template = "blog/category.html"
    category = get_object_or_404(Category, is_published=True, slug=cs)

    post_list = category.posts.published()

    paginator = Paginator(post_list, NUMBER_OF_POSTS)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "category": category,
        "page_obj": page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    template = "blog/profile.html"
    user = get_object_or_404(User, username=username)

    if request.user == user:
        post_list = user.posts.all().order_by("-pub_date")
    else:
        post_list = user.posts.published()

    paginator = Paginator(post_list, NUMBER_OF_POSTS)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "profile": user,
        "page_obj": page_obj,
    }
    return render(request, template, context)


@login_required
def edit_profile(request):
    template = "blog/edit_profile.html"
    if request.method == "POST":
        from django.contrib.auth.forms import UserChangeForm

        form = UserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Профиль успешно обновлен!")
            return redirect("blog:profile", username=request.user.username)
    else:
        from django.contrib.auth.forms import UserChangeForm

        form = UserChangeForm(instance=request.user)
    context = {"form": form}
    return render(request, template, context)


@login_required
def create_post(request):
    template = "blog/create.html"

    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, "Пост успешно создан!")
            return redirect("blog:profile", username=request.user.username)
    else:
        form = PostForm()

    context = {"form": form}
    return render(request, template, context)


@login_required
def edit_post(request, pk):
    template = "blog/create.html"
    post = get_object_or_404(Post, pk=pk)

    if post.author != request.user:
        messages.error(request, "Вы не можете редактировать этот пост")
        return redirect("blog:post_detail", pk=post.pk)  # Перенаправление вместо 404

    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, "Пост успешно обновлен!")
            return redirect("blog:post_detail", pk=post.pk)
    else:
        form = PostForm(instance=post)

    context = {"form": form}
    return render(request, template, context)


@login_required
def delete_post(request, pk):
    template = "blog/create.html"
    post = get_object_or_404(Post, pk=pk)

    if post.author != request.user:
        messages.error(request, "Вы не можете удалить этот пост")
        return redirect("blog:post_detail", pk=post.pk)  # Перенаправление вместо 404

    if request.method == "POST":
        post.delete()
        messages.success(request, "Пост успешно удален!")
        return redirect("blog:profile", username=request.user.username)

    form = PostForm(instance=post)
    context = {
        "form": form,
        "post": post,
    }
    return render(request, template, context)


@login_required
def add_comment(request, pk):
    """Добавление комментария к посту."""
    post = get_object_or_404(Post, pk=pk)

    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            messages.success(request, "Комментарий успешно добавлен!")
    else:
        form = CommentForm()

    return redirect("blog:post_detail", pk=post.pk)


@login_required
def edit_comment(request, post_pk, comment_pk):
    """Редактирование комментария."""
    post = get_object_or_404(Post, pk=post_pk)
    comment = get_object_or_404(Comment, pk=comment_pk)

    if comment.author != request.user:
        messages.error(request, "Вы не можете редактировать этот комментарий")
        return redirect("blog:post_detail", pk=post.pk)  # Перенаправление вместо 404

    if request.method == "POST":
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            messages.success(request, "Комментарий успешно обновлен!")
            return redirect("blog:post_detail", pk=post.pk)
    else:
        form = CommentForm(instance=comment)

    context = {
        "form": form,
        "post": post,
        "comment": comment,
        "editing_comment": True,
    }
    return render(request, "blog/edit_comment.html", context)


@login_required
def delete_comment(request, post_pk, comment_pk):
    post = get_object_or_404(Post, pk=post_pk)
    comment = get_object_or_404(Comment, pk=comment_pk)

    if comment.author != request.user:
        messages.error(request, "Вы не можете удалить этот комментарий")
        return redirect("blog:post_detail", pk=post.pk)  # Перенаправление вместо 404

    if request.method == "POST":
        comment.delete()
        messages.success(request, "Комментарий успешно удален!")
        return redirect("blog:post_detail", pk=post.pk)

    context = {
        "post": post,
        "comment": comment,
        "deleting_comment": True,
    }
    return render(request, "blog/delete_comment.html", context)
