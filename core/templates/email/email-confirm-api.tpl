{% extends "mail_templated/base.tpl" %}

{% block html %}
{{ user }}, this is an <strong>email verifications</strong> message.
<a href="http://127.0.0.1:80/accounts/api/v1/activation/confirm/{{ token }}/">verify your email</a>
{% endblock %}