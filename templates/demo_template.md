
# {{ title }}

Welcome to {{ app_name }}!

## Features:
{% for feature in features %}
- {{ feature }}
{% endfor %}

## Recent Conversations:
{% for conv in conversations %}
### {{ conv.title }}
- Date: {{ conv.date }}
- Messages: {{ conv.message_count }}
{% endfor %}
        