import logging
from django.http import Http404
from django.shortcuts import render
from django.utils.translation import get_language
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

    def get_object(self, queryset=None):
        queryset = queryset or self.get_queryset()
        language = (get_language() or "uk").split("-")[0]
        slug = self.kwargs.get(self.slug_url_kwarg)
        slug_field = f"{self.slug_field}_{language}"

        localized_queryset = queryset.filter(status=1)
        if hasattr(Post, slug_field):
            localized_queryset = localized_queryset.filter(**{slug_field: slug})
        else:
            localized_queryset = localized_queryset.filter(**{self.slug_field: slug})

        obj = localized_queryset.order_by("-updated_on", "-pk").first()
        if obj is None:
            raise Http404("No Post matches the given query.")

        if localized_queryset.count() > 1:
            logger.warning(
                "Multiple posts matched localized slug",
                extra={"slug": slug, "language": language, "matches": localized_queryset.count()},
            )

        return obj

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
