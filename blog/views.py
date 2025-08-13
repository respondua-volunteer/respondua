import logging
from django.shortcuts import render
from django.views import generic
from .models import Post
from typing import List
from django.conf import settings
from django.db import connection
from django.db.models import F, Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import translation
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

PG_CONFIG = {"uk": "ukrainian", "en": "english"}

def _active_lang() -> str:
    lang = (translation.get_language() or settings.LANGUAGE_CODE or "uk")[:2]
    return "uk" if lang not in ("uk", "en") else lang

def search_posts(request):
    q = (request.GET.get("q") or "").strip()[:100]
    page = request.GET.get("page") or 1
    lang = _active_lang()
    title_field = f"title_{lang}"
    content_field = f"content_{lang}"

    # убрал .only(...) чтобы не конфликтовать и свободно читать author.name
    base = (
        Post.objects.filter(status=1)
        .select_related("author")
        .prefetch_related("tags")
    )

    results = base.none()
    similar: List[Post] = []
    used_backend = connection.vendor

    if q and len(q) >= 2:
        if used_backend == "postgresql":
            from django.contrib.postgres.search import (
                SearchVector, SearchQuery, SearchRank, SearchHeadline
            )
            config = PG_CONFIG.get(lang, "simple")

            # Ищем и по имени автора (вес поменьше)
            vector = (
                SearchVector(F(title_field),   weight="A", config=config) +
                SearchVector(F(content_field), weight="B", config=config) +
                SearchVector(F("author__name"), weight="C", config=config)
            )

            query = SearchQuery(q, config=config, search_type="plain")

            qs = (
                base.annotate(search_vector=vector)
                    .filter(search_vector=query)
                    .annotate(rank=SearchRank(F("search_vector"), query))
                    .order_by("-rank", "-created_on")
                    .distinct()
            )

            # Подсветка (если доступна)
            try:
                qs = qs.annotate(
                    hl_title=SearchHeadline(F(title_field), query,
                                            start_sel="<mark>", stop_sel="</mark>", config=config),
                    hl_excerpt=SearchHeadline(F(content_field), query,
                                              start_sel="<mark>", stop_sel="</mark>", config=config),
                )
            except Exception:
                pass

            results = qs

        else:
            # SQLite/MySQL: простая фильтрация + автор
            results = (
                base.filter(
                    Q(**{f"{title_field}__icontains": q}) |
                    Q(**{f"{content_field}__icontains": q}) |
                    Q(author__name__icontains=q)
                )
                .order_by("-created_on")
                .distinct()
            )

        # Если пусто — попробуем «похожие» по автору или названию
        if not results.exists():
            try:
                if used_backend == "postgresql":
                    from django.contrib.postgres.search import TrigramSimilarity
                    similar = (
                        base.annotate(sim=TrigramSimilarity(F("author__name"), q))
                            .filter(sim__gte=0.2)
                            .order_by("-sim", "-created_on")[:5]
                    )
                    if not similar:
                        similar = (
                            base.annotate(sim=TrigramSimilarity(F(title_field), q))
                                .filter(sim__gte=0.2)
                                .order_by("-sim", "-created_on")[:5]
                        )
                else:
                    similar = base.filter(author__name__icontains=q)[:5]
                    if not similar:
                        similar = base.filter(**{f"{title_field}__icontains": q})[:5]
            except Exception:
                similar = base.filter(author__name__icontains=q)[:5] or \
                          base.filter(**{f"{title_field}__icontains": q})[:5]
    else:
        similar = []

    paginator = Paginator(results, 10)
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    logger.info(
        "Blog search performed",
        extra={"query": q, "lang": lang, "db": used_backend,
               "count": paginator.count, "page": page_obj.number}
    )

    return render(
        request,
        "search_results.html",
        {"query": q, "results": page_obj, "similar": similar, "lang": lang},
    )