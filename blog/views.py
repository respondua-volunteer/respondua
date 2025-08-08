import logging
from django.shortcuts import render
from django.views import generic
from .models import Post

logger = logging.getLogger(__name__)  # создаём логгер для blog

class PostList(generic.ListView):
    queryset = Post.objects.filter(status=1).order_by('-created_on')
    template_name = 'blogusy.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_blog_page'] = True  
        logger.info("Blog list page opened", extra={"total_posts": self.queryset.count()})
        return context


class PostDetail(generic.DetailView):
    model = Post
    template_name = 'single_blogus.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        recent = Post.objects.filter(status=1).order_by('-created_on')[:5]
        context['recent_posts'] = recent
        logger.info("Blog post viewed", extra={"post_title": self.object.title})
        return context


class RecentPosts(generic.ListView):
    queryset = Post.objects.filter(status=1).order_by('-created_on')[:5]
    template_name = 'recent_posts.html'
    context_object_name = 'recent_posts'

    def get_queryset(self):
        logger.debug("Recent posts widget loaded")
        return super().get_queryset()


def search_posts(request):
    query = request.GET.get('q', '').strip()
    results = Post.objects.filter(title__icontains=query) if query else Post.objects.none()

    logger.info(
        "Blog search performed",
        extra={"search_query": query, "results_count": results.count()}
    )

    return render(request, 'search_results.html', {'results': results, 'query': query})
