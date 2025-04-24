{% extends "mail_templated/base.tpl" %}

{% block html %}
{{ user }}, this is an <strong>email verifications</strong> message.
<a href="http://127.0.0.1:8000/accounts/api/v1/activation/confirm/{{ token }}/">فعال سازی حساب کاربری</a>

{% endblock %}