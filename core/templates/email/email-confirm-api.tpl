{% extends "mail_templated/base.tpl" %}

{% block html %}
{{ user }}, this is an <strong>email verifications</strong> message.
<a href="{{ domain }}/accounts/api/v1/email-verification/confirm/{{ token }}/">verify your email</a>
{% endblock %}