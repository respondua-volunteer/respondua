from django.shortcuts import render

from django.views import generic
from .models import Post

class PostList(generic.ListView):
    queryset = Post.objects.filter(status=1).order_by('-created_on')
    template_name = 'blogusy.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_blog_page'] = True  
        return context

class PostDetail(generic.DetailView):
    model = Post
    template_name = 'single_blogus.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recent_posts'] = Post.objects.filter(status=1).order_by('-created_on')[:5]
        return context

class RecentPosts(generic.ListView):
    queryset = Post.objects.filter(status=1).order_by('-created_on')[:5]
    template_name = 'recent_posts.html'
    context_object_name = 'recent_posts'


def search_posts(request):
    query = request.GET.get('q')  
    results = Post.objects.filter(title__icontains=query)  
    return render(request, 'search_results.html', {'results': results, 'query': query})
    # return render(request, 'search_results.html', {})
