from django.shortcuts import render, get_object_or_404, redirect
import pdb
from django.utils import timezone, http
from .models import Post, Comment
from .forms import PostForm, CommentForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
# Create your views here.

def post_list(request):
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
    return render(request, 'blog/post_list.html', {'posts':posts, 'next':request.path})

def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.published_date == None and post.author != request.user:
        return redirect('blog:post_list')
    return render(request, 'blog/post_detail.html', {'post':post, 'next':request.path})

@login_required
def post_new(request):
    if request.method =="POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            if request.POST['sap']=='1':
                post.publish()
            return redirect('blog:post_detail', pk=post.pk)
    else:
        form = PostForm()
        return render(request, 'blog/post_edit.html', {'form': form})

@login_required
def post_edit(request, pk):

    post = get_object_or_404(Post, pk=pk)
    if request.user != post.author:
        return redirect('blog:post_detail', pk=post.pk)

    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = None
            if request.POST['sap']=='1':
                post.publish()
            post.save()
            return redirect('blog:post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/post_edit.html', {'form': form})

@login_required
def post_draft_list(request):
    posts = Post.objects.filter(author=request.user).filter(published_date__isnull=True).order_by('created_date')
    return render(request, 'blog/post_draft_list.html', {'posts':posts})

@login_required
def post_publish(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.user != post.author:
        return redirect('blog:post_detail', pk=post.pk)
    post.publish()
    return redirect('blog:post_detail', pk=pk)

@login_required
def post_remove(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.user != post.author:
        return redirect('blog:post_detail', pk=post.pk)
    post.delete()
    return redirect('blog:post_list')

@login_required
def add_comment_to_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.author_name = str(request.user)
            comment.save()
            return redirect('blog:post_detail', pk=post.pk)
    else:
        form = CommentForm()
    return render(request, 'blog/add_comment_to_post.html', {'form': form, 'next':request.path})

@login_required
def comment_approve(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if request.user != comment.post.author:
        return redirect('blog:post_detail', pk=comment.post.pk)
    comment.approve()
    return redirect('blog:post_detail', pk=comment.post.pk)

@login_required
def comment_remove(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if request.user != comment.post.author and request.user != comment.author:
        return redirect('blog:post_detail', pk=comment.post.pk)
    comment.delete()
    return redirect('blog:post_detail', pk=comment.post.pk)

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        next = request.POST['next']
        next = next if http.is_safe_url(next, request.get_host()) else '/'
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password')
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect(next, '/')
    else:
        form = UserCreationForm()
        next = request.GET['next']
        next = next if http.is_safe_url(next, request.get_host()) else '/'
    return render(request, 'registration/signup.html', {'form':form, 'next':next})
