Pretix GitHub Authentication
===================

This plugin is based on [https://github.com/pretix-unofficial/pretix-auth-okta](https://github.com/pretix-unofficial/pretix-auth-okta) and allows to authenticate against GitHub in the pretix backend.

***Attention***: The plugin is a quick-and-dirty adaptation of the plugin above, so it may not be reliable!

To install the plugin, use: ``pip install git+https://github.com/agrillenberger/pretix-auth-github.git@main#egg=pretix-auth-github``

Configuration
-------------

1. Create GitHub OAuth application. Redirect URL is ``https://your-server/_github/return``.
2. Add ``auth_backends=pretix_auth_okta.auth.GitHubAuthBackend,pretix.base.auth.NativeAuthBackend`` to ``[pretix]`` section of ``pretix.cfg``
3. Add the following section to ``pretix.cfg``:

        [pretix_auth_github]
        label=SSO
        client_id=123456
        client_secret=5675345
        url=https://github.com/login/oauth
        api=https://api.github.com
        allowCreate=0
4. Change ``client_id`` and ``client_secret`` according to your GitHub OAuth app and maybe change the option ``allowCreate`` to decide, whether new accounts may be created by the plugin.

License
-------

As the original plugin, this plugin is released under the terms of the Apache License 2.0
The original plugin ``pretix-auth-okta``is copyright 2020 pretix Team
