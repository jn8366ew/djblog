# for chaining postlist and bookmarklist
from itertools import chain

# Core django import
from django.views.generic import CreateView, UpdateView, DeleteView, FormView
from django.views.generic.dates import ArchiveIndexView, YearArchiveView, MonthArchiveView, \
                                       DayArchiveView, TodayArchiveView
from django.views.generic import ListView, DetailView, TemplateView
from django.conf import settings
from django.views.generic import FormView
from django.db.models import Q
from django.shortcuts import render

# For authorization function
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

# Project App import
from mysite.views import OwnerOnlyMixin
from .forms import PostSearchForm
from .models import Post
from bookmark.models import Bookmark



# ListView
class PostLV(ListView):
    model = Post
    template_name = 'blog/post_all.html'
    # 이 컨텍스트 객체는 템플릿에서 사용된다
    context_object_name = 'posts'
    paginate_by = 5


# DetailView
class PostDV(DetailView):
    model = Post

    # methods For DISQUS
    # Return 안써써 meta str 오류 뜸
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # use f string. https://realpython.com/python-f-strings/ 의 simple syntax 참조
        context['disqus_short'] = f"{settings.DISQUS_SHORTNAME}"
        context['disqus_id'] = f"post-{self.object.id}-{self.object.slug}"
        context['disqus_url'] = f"{settings.DISQUS_MY_DOMAIN}{self.object.get_absolute_url()}"
        context['disqus_title'] = f"{self.object.slug}"
        return context

# FormView
class SearchFormView(FormView):
    form_class = PostSearchForm
    template_name = 'blog/post_search.html'

    def form_valid(self, form):
        searchWord = form.cleaned_data['search_word']
        post_list = Post.objects.filter(Q(title__icontains=searchWord) | Q(description__icontains=searchWord) | \
                                        Q(content__icontains=searchWord)).distinct()


        # bookmark도 검색
        bookmark_list = Bookmark.objects.filter(Q(title__icontains=searchWord)).distinct()

        """문제점: URL은 title 검색 결과는 나옴. 클릭시 그 url로 안가짐. 추후 보완 """
        # test = list(chain(post_list, bookmark_list))


        context = {}
        context['form'] = form
        context['search_term'] = searchWord
        context['object_list'] = post_list

        return render(self.request, self.template_name, context) # No Redirection

# ArchiveView
class PostAV(ArchiveIndexView):
    model = Post
    date_field = 'modify_dt'

class PostYAV(YearArchiveView):
    model = Post
    date_field = 'modify_dt'
    make_object_list = True

class PostMAV(MonthArchiveView):
    model = Post
    date_field = 'modify_dt'

class PostDAV(DayArchiveView):
    model = Post
    date_field = 'modify_dt'

class PostTAV(TodayArchiveView):
    model = Post
    date_field = 'modify_dt'

# Class style TagView
class TagCloudTV(TemplateView):
    template_name = 'taggit/taggit_cloud.html'

class TaggedObjectLV(ListView):
    template_name = 'taggit/taggit_post_list.html'
    model = Post

    def get_queryset(self):
        return Post.objects.filter(tags__name=self.kwargs.get('tag'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tagname'] = self.kwargs['tag']
        return context

# class-based views

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'slug', 'description', 'content', 'tags']
    initial = {'slug': 'auto-filling-do-not-input'}
    # another way to deal with 'slug' field
    # field = ['title', 'description', 'content', 'tags']
    success_url = reverse_lazy('blog:index')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

class PostChangeLV(LoginRequiredMixin, ListView):
    template_name = 'blog/post_change_list.html'

    def get_queryset(self):
        return Post.objects.filter(owner=self.request.user)

class PostUpdateView(OwnerOnlyMixin, UpdateView):
    model = Post
    fields = ['title', 'slug', 'description', 'content', 'tags']
    success_url = reverse_lazy('blog:index')

class PostDeleteView(OwnerOnlyMixin, DeleteView):
    model = Post
    success_url = reverse_lazy('blog:index')