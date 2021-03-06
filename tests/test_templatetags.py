# -*- coding: utf-8 -*-
"""
    :copyright: Copyright 2014 by Łukasz Mierzwa
    :contact: l.mierzwa@gmail.com
"""


from __future__ import unicode_literals

from django.test import TestCase
from django.template import Context, Template
from django.test.client import RequestFactory
from django.db.models import Model, CharField


T_LOAD = '{% load django_bootstrap_breadcrumbs %}'

T_BLOCK_CLEAR = '''
{% block breadcrumbs %}
{% clear_breadcrumbs %}
{% endblock %}
'''

T_BLOCK_USER_SAFE_CLEAR = '''
{% block breadcrumbs %}
{% breadcrumb "Home" "/" %}
{% breadcrumb "Login" "login_url" %}
{% breadcrumb actor actor %}
{% breadcrumb "Users and groups" "/users" %}
{% breadcrumb_safe "<span>John</span>" "/john" %}
{% clear_breadcrumbs %}
{% breadcrumb "Cleared" actor %}
{% endblock %}
'''

T_BLOCK_USER = '''
{% block breadcrumbs %}
{% breadcrumb "Home" "/" %}
{% breadcrumb "Users and groups" "/users" %}
{% endblock %}
'''

T_BLOCK_SAFE = '''
{% block breadcrumbs %}
{% breadcrumb_safe "<span>John</span>" "/john" %}
{% endblock %}
'''

T_BLOCK_USER_SAFE = '''
{% block breadcrumbs %}
{% breadcrumb "Home" "/" %}
{% breadcrumb "Login" "login_url" %}
{% breadcrumb actor actor %}
{% breadcrumb "Users and groups" "/users" %}
{% breadcrumb_safe "<span>John</span>" "/john" %}
{% endblock %}
'''

T_BLOCK_NS = '''
{% block breadcrumbs %}
{% breadcrumb "Login2" "ns:login2_url" %}
{% breadcrumb "John" "/john" %}
{% endblock %}
'''

T_BLOCK_NS_FOR = '''
{% block breadcrumbs %}
{% breadcrumb_for "/static" %}<span>Static</span>{% endbreadcrumb_for %}
{% breadcrumb_for ns:login2_url %}Login2{% endbreadcrumb_for %}
{% breadcrumb_for "/john" %}John{% endbreadcrumb_for %}
{% endblock %}
'''

T_BLOCK_NS_FOR_QUOTES = '''
{% block breadcrumbs %}
{% breadcrumb_for "ns:login2_url" %}Login2a{% endbreadcrumb_for %}
{% breadcrumb_for 'ns:login2_url' %}Login2b{% endbreadcrumb_for %}
{% breadcrumb_for "/john" %}John{% endbreadcrumb_for %}
{% endblock %}
'''

T_BLOCK_ESCAPE = '''
{% block breadcrumbs %}
{% breadcrumb "Home" "/" %}
{% breadcrumb "<span>John</span>" "/john" %}
{% endblock %}
'''

T_BLOCK_FOR = '''
{% block breadcrumbs %}
{% breadcrumb_for "/static" %}<span>Static</span>{% endbreadcrumb_for %}
{% breadcrumb_for actor %}{{ actor.name }}{% endbreadcrumb_for %}
{% endblock %}
'''

T_BLOCK_FOR_VAR = '''
{% block breadcrumbs %}
{% breadcrumb_for nonexisting %}404{% endbreadcrumb_for %}
{% breadcrumb_for login_args_url actor.name %}Login Act{% endbreadcrumb_for %}
{% breadcrumb_for login_args_url dummyarg %}Login Actor{% endbreadcrumb_for %}
{% breadcrumb "Home" "/" %}
{% endblock %}
'''

T_BLOCK_RENDER = '''
{% block content %}
<div>{% render_breadcrumbs %}</div>
{% endblock %}
'''

T_BLOCK_RENDER_BS3 = '''
{% block content %}
<div>
{% render_breadcrumbs "django_bootstrap_breadcrumbs/bootstrap3.html" %}
</div>
{% endblock %}
'''


class Actor(Model):

    name = CharField(max_length=128)

    def get_absolute_url(self):
        return '/actor'


class SiteTests(TestCase):

    def setUp(self):
        self.actor = Actor(name='Actor')
        self.factory = RequestFactory()
        self.request = self.factory.get('/')
        self.context = Context({'request': self.request, 'actor': self.actor})

    def test_load(self):
        t = Template(T_LOAD)
        self.assertEqual(t.render(self.context), '')

    def test_clear_breadcrumbs(self):
        t = Template(T_LOAD + T_BLOCK_CLEAR)
        self.assertEqual(t.render(self.context), '\n\n\n\n')

    def test_clear_breadcrumbs_without_request(self):
        t = Template(T_LOAD + T_BLOCK_CLEAR)
        self.assertEqual(t.render(Context()), '\n\n\n\n')

    def test_push_breadcrumbs(self):
        t = Template(T_LOAD + T_BLOCK_USER)
        self.assertEqual(t.render(self.context), '\n\n\n\n\n')

    def test_push_breadcrumb_for(self):
        t = Template(T_LOAD + T_BLOCK_FOR)
        self.assertEqual(t.render(self.context), '\n\n\n\n\n')

    def test_push_breadcrumb_for_without_request(self):
        t = Template(T_LOAD + T_BLOCK_FOR)
        self.assertEqual(t.render(Context()), '\n\n\n\n\n')

    def test_push_breadcrumbs_safe(self):
        t = Template(T_LOAD + T_BLOCK_SAFE)
        self.assertEqual(t.render(self.context), '\n\n\n\n')

    def test_render_empty_breadcrumbs(self):
        t = Template(T_LOAD + T_BLOCK_RENDER)
        self.assertEqual(t.render(self.context), '\n\n<div></div>\n\n')

    def test_render_empty_breadcrumbs_bs3(self):
        t = Template(T_LOAD + T_BLOCK_RENDER_BS3)
        self.assertEqual(t.render(self.context), '\n\n<div>\n\n</div>\n\n')

    def test_render_without_request(self):
        t = Template(T_LOAD + T_BLOCK_USER_SAFE + T_BLOCK_RENDER)
        self.assertNotEqual(t.render(Context()), '')

    def test_render(self):
        t = Template(T_LOAD + T_BLOCK_USER_SAFE + T_BLOCK_RENDER)
        resp = t.render(self.context)
        self.assertTrue('<a href="/">Home</a>' in resp)
        self.assertTrue('<a href="/login">Login</a>' in resp)
        self.assertTrue('<a href="/actor">Actor object</a>' in resp)
        self.assertTrue('<a href="/users">Users and groups</a>' in resp)
        self.assertTrue('<span>John</span>' in resp)
        self.assertTrue('<span class="divider">/</span>' in resp)
        self.assertEqual(len(self.request.META['DJANGO_BREADCRUMB_LINKS']), 5)

    def test_render_bs3(self):
        t = Template(T_LOAD + T_BLOCK_USER_SAFE + T_BLOCK_RENDER_BS3)
        resp = t.render(self.context)
        self.assertTrue('<a href="/">Home</a>' in resp)
        self.assertTrue('<a href="/login">Login</a>' in resp)
        self.assertTrue('<a href="/actor">Actor object</a>' in resp)
        self.assertTrue('<a href="/users">Users and groups</a>' in resp)
        self.assertTrue('<span>John</span>' in resp)
        self.assertEqual(len(self.request.META['DJANGO_BREADCRUMB_LINKS']), 5)

    def test_render_breadcrumb_for(self):
        t = Template(T_LOAD + T_BLOCK_FOR + T_BLOCK_RENDER)
        resp = t.render(self.context)
        self.assertTrue('<a href="/static"><span>Static</span></a>' in resp)
        self.assertTrue('Actor' in resp)
        self.assertTrue('<span class="divider">/</span>' in resp)
        self.assertEqual(len(self.request.META['DJANGO_BREADCRUMB_LINKS']), 2)

    def test_render_breadcrumb_for_variable(self):
        t = Template(T_LOAD + T_BLOCK_FOR_VAR + T_BLOCK_RENDER)
        resp = t.render(self.context)
        self.assertTrue('<a href="nonexisting">404</a>' in resp)
        self.assertTrue('<a href="/login/Actor">Login Act</a>' in resp)
        self.assertTrue('<span class="divider">/</span>' in resp)
        self.assertEqual(len(self.request.META['DJANGO_BREADCRUMB_LINKS']), 4)

    def test_render_ns(self):
        t = Template(T_LOAD + T_BLOCK_NS + T_BLOCK_RENDER)
        resp = t.render(self.context)
        self.assertTrue('<a href="/ns/login2">Login2</a>' in resp)
        self.assertTrue('<span class="divider">/</span>' in resp)
        self.assertEqual(len(self.request.META['DJANGO_BREADCRUMB_LINKS']), 2)

    def test_render_ns_app(self):
        self.context['request'].path = '/login'
        t = Template(T_LOAD + T_BLOCK_NS + T_BLOCK_RENDER)
        resp = t.render(self.context)
        self.assertTrue('<a href="/ns/login2">Login2</a>' in resp)
        self.assertTrue('<span class="divider">/</span>' in resp)
        self.assertEqual(len(self.request.META['DJANGO_BREADCRUMB_LINKS']), 2)

    def test_render_ns_breadcrumb_for(self):
        t = Template(T_LOAD + T_BLOCK_NS_FOR + T_BLOCK_RENDER)
        resp = t.render(self.context)
        self.assertTrue('<a href="/static"><span>Static</span></a>' in resp)
        self.assertTrue('<a href="/ns/login2">Login2</a>' in resp)
        self.assertTrue('<span class="divider">/</span>' in resp)
        self.assertEqual(len(self.request.META['DJANGO_BREADCRUMB_LINKS']), 3)

    def test_render_ns_breadcrumb_for_quotes(self):
        t = Template(T_LOAD + T_BLOCK_NS_FOR_QUOTES + T_BLOCK_RENDER)
        resp = t.render(self.context)
        self.assertTrue('<a href="/ns/login2">Login2a</a>' in resp)
        self.assertTrue('<a href="/ns/login2">Login2b</a>' in resp)
        self.assertTrue('<span class="divider">/</span>' in resp)
        self.assertEqual(len(self.request.META['DJANGO_BREADCRUMB_LINKS']), 3)

    def test_render_escape(self):
        t = Template(T_LOAD + T_BLOCK_ESCAPE + T_BLOCK_RENDER)
        resp = t.render(self.context)
        self.assertTrue('&lt;span&gt;John&lt;/span&gt;' in resp)
        self.assertEqual(len(self.request.META['DJANGO_BREADCRUMB_LINKS']), 2)

    def test_render_cleared(self):
        t = Template(T_LOAD + T_BLOCK_USER_SAFE_CLEAR + T_BLOCK_RENDER)
        resp = t.render(self.context)
        self.assertFalse('<a href="/">Home</a>' in resp)
        self.assertFalse('<a href="/login">Login</a>' in resp)
        self.assertFalse('<a href="/actor">Actor object</a>' in resp)
        self.assertFalse('<a href="/users">Users and groups</a>' in resp)
        self.assertFalse('<span>John</span>' in resp)
        self.assertFalse('<span class="divider">/</span>' in resp)
        self.assertTrue('Cleared' in resp)
        self.assertEqual(len(self.request.META['DJANGO_BREADCRUMB_LINKS']), 1)
