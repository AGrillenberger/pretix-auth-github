from django.utils.translation import gettext_lazy

try:
    from pretix.base.plugins import PluginConfig
except ImportError:
    raise RuntimeError("Please use pretix 2.7 or above to run this plugin!")

from . import __version__


class PluginApp(PluginConfig):
    default = True
    name = 'pretix_auth_github'
    verbose_name = 'GitHub Authentication'

    class PretixPluginMeta:
        name = gettext_lazy('GitHub Authentication')
        description = gettext_lazy('Supports pretix backend auth using GitHub')
        visible = False
        version = __version__
        category = 'INTEGRATION'
        compatibility = "pretix>=4.7.0.dev1"

    def ready(self):
        from . import signals  # NOQA


