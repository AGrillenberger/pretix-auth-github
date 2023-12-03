from django.conf import settings
from django.urls import reverse
from pretix.base.auth import BaseAuthBackend
from urllib.parse import quote


class GitHubAuthBackend(BaseAuthBackend):
    identifier = "github"

    @property
    def verbose_name(self):
        return settings.CONFIG_FILE.get('pretix_auth_github', 'label', fallback='Github')

    def authentication_url(self, request):
        u = reverse('plugins:pretix_auth_github:start')
        if 'next' in request.GET:
            u += '?next=' + quote(request.GET.get('next'))
        return u

    def get_next_url(self, request):
        if hasattr(request, '_github_next'):
            return request._github_next
