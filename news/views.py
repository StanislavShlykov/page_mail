from datetime import datetime

from django.shortcuts import render, HttpResponse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from .models import Post, Category
from .filters import PostFilter
from django.urls import reverse_lazy
from .forms import PostForm
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.mail import send_mail
from django.shortcuts import redirect
from django.views import View
from django.contrib.auth.models import Group


def content(request):
    return render(request, 'flatpages/main.html')


class NewsList(LoginRequiredMixin, ListView):
    model = Post
    ordering = '-time_in'
    template_name = 'news_list.html'
    context_object_name = 'news_list'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = PostFilter(self.request.GET, queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        return context


class ArticlesList(LoginRequiredMixin, ListView):
    model = Post
    context_object_name = 'news_list'
    queryset = Post.objects.filter(type=True)
    template_name = 'news_list.html'


class NewsDetail(LoginRequiredMixin, DetailView):
    model = Post
    template_name = 'news.html'
    context_object_name = 'news'


class ArticlesDetail(LoginRequiredMixin, DetailView):
    model = Post
    template_name = 'news.html'
    queryset = Post.objects.filter(type=True)
    context_object_name = 'news'


class PostCreate(LoginRequiredMixin, CreateView):
    permission_required = ('news.add_post')
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'
    def post(self, request, *args, **kwargs):
        news = Post(
            post_name = request.POST['post_name'],
            post_text = request.POST['post_text'],
            post_category = Post.category(id = request.POST['category']),
            author = Post.author(id = request.POST['author']),
        )
        news.save()
        for i in news.category.values():
            cat = Category(cat_name = i['cat_name'])
            for j in cat.users.values():
                send_mail(
                    subject= 'новая новость',
                    message= news.post_text,
                    from_email= 'sshlykov3@yandex.ru',
                    recipient_list=[j['email'],],
                    fail_silently= True
                )
    # def form_valid(self, form):
    #     post = form.save()
    #     for i in post.category.values():
    #         cat = Category(cat_name=i['cat_name'])
    #         cat_name = i['cat_name']
    #         for j in cat.users.values():
    #             send_mail(
    #                 subject=f'Новая статья по теме {cat_name}',
    #                 message=post.post_text,
    #                 from_email='sslykov3@yandex.ru',
    #                 recipient_list=[f'''{j['email']}'''],
    #                 fail_silently=True
    #             )
    #     return super().form_valid(form)
    #
    # # def send_mail(self, form):
    # #     post = form.save()
    # #     for i in post.category.values():
    # #         cat = Category(cat_name = i['cat_name'])
    # #         cat_name = i['cat_name']
    # #         for j in cat.users.values():
    # #             send_mail(
    # #                 subject= f'Новая статья по теме {cat_name}',
    # #                 message= post.post_text,
    # #                 from_email= 'sslykov3@yandex.ru',
    # #                 recipient_list=[f'''{j['email']}'''],
    # #                 fail_silently = True
    #     )


class NewsCreate(PermissionRequiredMixin, CreateView):
    permission_required = ('news.add_post')
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'

    def form_valid(self, form):
        post = form.save(commit=False)
        post.type = True
        return super().form_valid(form)

class PostUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = ('news.change_post')
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'


class PostDelete(PermissionRequiredMixin, DeleteView):
    permission_required = ('news.delete_post',)
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('post_list')


class NewsSearch(NewsList):
    template_name = 'news_search.html'


def sign_me(request):
    user= request.user
    category = Category.objects.get(cat_name = request.GET['category'])
    category.users.add(user)
    return HttpResponse('вы подписались!')



    # if not user in category.users:

