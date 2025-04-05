{% extends "mail_templated/base.tpl" %}

{% block html %}
{{ user.profile_set.first.first_name }} {{user.profile_set.first.last_name}}, this is an <strong>html</strong> message.
<img src='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSCZjbg7CPvOvjKiPGx1scrtXof66lpeadBHw&s'>
{% endblock %}