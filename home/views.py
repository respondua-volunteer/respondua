from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.views.decorators.cache import cache_page

from .models import Event
from django.utils import timezone
from blog.models import Post


CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)


@cache_page(CACHE_TTL)
def home(request):
    events = Event.objects.filter(date__gte=timezone.now()).order_by('date')
    recent_posts = Post.objects.all()[:3]
    is_home_page = True  
    return render(request, 'home.html', {'events': events, 'recent_posts':recent_posts, 'is_home_page':is_home_page}, )#{'recent_posts': recent_posts}


@cache_page(CACHE_TTL)
def team(request):
    is_team_page = True  
    return render(request, 'team.html', {'is_team_page':is_team_page})

from django.shortcuts import redirect

def external_privacy_policy(request):
    return redirect("https://app.websitepolicies.com/policies/view/fqvst3db")