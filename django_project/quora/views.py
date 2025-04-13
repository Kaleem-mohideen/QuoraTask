from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)
from .models import Post, Answer
from .forms import AnswerForm

from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse


# @login_required
# def like_answer(request, answer_id):
#     answer = get_object_or_404(Answer, id=answer_id)
#     answer.likes.add(request.user)
#     return redirect('post-detail', pk=answer.question.id)

@require_POST
@login_required
def like_answer(request, answer_id):
    answer = get_object_or_404(Answer, id=answer_id)
    liked = False

    if request.user in answer.likes.all():
        answer.likes.remove(request.user)
    else:
        answer.likes.add(request.user)
        liked = True

    return JsonResponse({
        'liked': liked,
        'like_count': answer.likes.count()
    })

@require_POST
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    liked = False

    if request.user in post.likes.all():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)
        liked = True

    return JsonResponse({
        'liked': liked,
        'like_count': post.likes.count()
    })

posts = [
    {
        'author': 'Mir Kaleem',
        'title': 'Quora Post 1',
        'content': 'First post content',
        'date_posted': 'April 12, 2025'
    },
    {
        'author': 'John',
        'title': 'Quora Post 2',
        'content': 'Second post content',
        'date_posted': 'April 13, 2025'
    }
]
def home(request):
    context = {
        'posts': posts #Post.objects.all()
    }
    return render(request, 'quora/home.html', context)


class PostListView(ListView):
    model = Post
    template_name = 'quora/home.html'  # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    ordering = ['-date_posted']
    paginate_by = 5


class UserPostListView(ListView):
    model = Post
    template_name = 'quora/user_posts.html'  # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    paginate_by = 5

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Post.objects.filter(author=user).order_by('-date_posted')


class PostDetailView(DetailView):
    model = Post
    template_name = 'quora/post_detail.html'  # adjust if needed

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['answer_form'] = AnswerForm()
        context['answers'] = self.object.answers.all().order_by('-date_posted')
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = AnswerForm(request.POST)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.author = request.user
            answer.question = self.object
            answer.save()
            return redirect('post-detail', pk=self.object.pk)
        context = self.get_context_data(object=self.object)
        context['answer_form'] = form
        return self.render_to_response(context)

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['title', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = '/'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


def about(request):
    return render(request, 'quora/about.html', {'title': 'About'})
