{% extends "mail_templated/base.tpl" %}

{% block html %}
{{ user.profile_set.first.first_name }} {{user.profile_set.first.last_name}}, this is an <strong>email verifications</strong> message.
<p>{{token}}</p>
{% endblock %}