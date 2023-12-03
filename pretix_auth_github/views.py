import logging
import requests
from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _
from pretix.base.models import User
from pretix.base.models.auth import EmailAddressTakenError
from pretix.control.views.auth import process_login
from pretix.helpers.urls import build_absolute_uri
from urllib.parse import quote

logger = logging.getLogger(__name__)


def start_view(request):
    request.session['pretix_auth_github_nonce'] = get_random_string(32)
    url = (
            settings.CONFIG_FILE.get('pretix_auth_github', 'url') +
            '/authorize?client_id={client_id}&none={nonce}&redirect_uri={redirect_uri}&state={state}&response_type=code&response_mode=query&scope=read:user,user:email'
    ).format(
        client_id=settings.CONFIG_FILE.get('pretix_auth_github', 'client_id'),
        nonce=request.session['pretix_auth_github_nonce'],
        state=quote(request.session['pretix_auth_github_nonce'] + '#' + request.GET.get('next', '')),
        redirect_uri=quote(build_absolute_uri('plugins:pretix_auth_github:return'))
    )
    return redirect(url)


def return_view(request):
    # check for error state
    if 'error' in request.GET:
        logger.warning('GitHub login failed. Response: ' + request.META['QUERY_STRING'])
        messages.error(request, _('Login was not successful. Error: {message}').format(message=request.GET.get('error_description')))
        return redirect(reverse('control:auth.login'))

    if 'state' not in request.GET:
        logger.exception('GitHub login did not send a state.')
        messages.error(request, _('Login was not successful due to a technical error.'))
        return redirect(reverse('control:auth.login'))

    nonce, next = request.GET['state'].split('#')
    if nonce != request.session['pretix_auth_github_nonce']:
        logger.exception('GitHub login sent an invalid nonce in the state parameter.')
        messages.error(request, _('Login request timed out, please try again.'))
        return redirect(reverse('control:auth.login'))
    if next:
        request._github_next = next

    try:
        r = requests.post(
            settings.CONFIG_FILE.get('pretix_auth_github', 'url') + '/access_token',
            headers = {
                "Accept": "application/json"
            },
            data={
                'client_id': settings.CONFIG_FILE.get('pretix_auth_github', 'client_id'),
                'client_secret': settings.CONFIG_FILE.get('pretix_auth_github', 'client_secret'),
                'redirect_uri': build_absolute_uri('plugins:pretix_auth_github:return'),
                'code': request.GET.get('code'),
            }
        )
        r.raise_for_status()
        response = r.json()
        if not "access_token" in response:
            logger.exception('GitHub login failed.')
            messages.error(request, _('Login was not successful due to a technical error.'))
            return redirect(reverse('control:auth.login'))
        access_token = response['access_token']

        r = requests.get(
            settings.CONFIG_FILE.get('pretix_auth_github', 'api') + '/user',
            headers={
                'Authorization': f'Bearer {access_token}'
            }
        )
        r.raise_for_status()
        response = r.json()
    except:
        logger.exception('GitHub login failed.')
        messages.error(request, _('Login was not successful due to a technical error.'))
        return redirect(reverse('control:auth.login'))

    r_emails = requests.get(
        settings.CONFIG_FILE.get('pretix_auth_github', 'api') + '/user/emails',
        headers={
            'Authorization': f'Bearer {access_token}'
        }
    )
    r_emails.raise_for_status()
    emails = r_emails.json()
    email = None
    for e in emails:
        if e["primary"] == True:
            email = e["email"]
            break
    
    if email is None:
        messages.error(
            request, _('Could not determine email address.')
        )
        return redirect(reverse('control:auth.login'))

    if settings.CONFIG_FILE.get('pretix_auth_github', 'allowCreate') != "1":
        try:
            u = User.objects.get(email=email)
        except:
            messages.error(
                request, _('User does not exist')
            )
            return redirect(reverse('control:auth.login'))

    try:
        u = User.objects.get_or_create_for_backend(
            'github', response['login'], email,
            set_always={},
            set_on_creation={
                'fullname': '{} {}'.format(
                    response.get('given_name', ''),
                    response.get('family_name', ''),
                ),
            }
        )
    except EmailAddressTakenError:
        messages.error(
            request, _('We cannot create your user account as a user account in this system '
                    'already exists with the same email address.')
        )
        return redirect(reverse('control:auth.login'))
    else:
        return process_login(request, u, keep_logged_in=False)
