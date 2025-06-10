from dataclasses import dataclass


{% for entity in entities -%}
@dataclass
class {{ entity | classify }}:
    pass
{% endfor %}
