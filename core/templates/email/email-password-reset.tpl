{% extends "mail_templated/base.tpl" %}

{% block html %}
{{ user }}, this is an <strong>user password reset</strong> message.
<a href="{{ domain }}/accounts/reset-password/{{ token }}/">Reset your password</a>
{% endblock %}