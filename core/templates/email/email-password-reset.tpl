{% extends "mail_templated/base.tpl" %}

{% block html %}
{{ user }}, this is an <strong>user password reset</strong> message.
<a href="http://127.0.0.1:80/accounts/reset-password/{{ token }}/">Reset your password</a>
{% endblock %}