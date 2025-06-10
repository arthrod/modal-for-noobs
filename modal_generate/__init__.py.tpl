{% if provision_log -%}
import structlog
{% endif -%}
from modal import Image, NetworkFileSystem, Stub

{% if provision_nfs -%}
from .constants import {% if provision_nfs -%}MOUNT_PATH{% endif %}
{% endif -%}
{% if entities | length > 0 -%}
from .schema import {{ entities | map("classify") | join(", ") }}
{% endif -%}

APP_NAME = "{{ name }}"

{% if provision_log -%}
log = structlog.get_logger()
{% endif -%}
{% if provision_nfs -%}
volume = NetworkFileSystem.persisted(f"{APP_NAME}-volume")
{% endif %}
image = (Image.debian_slim()
{% if system_dependencies -%}
.apt_install({{ system_dependencies | tojson }})
{% endif -%}
{% if python_dependencies -%}
.pip_install({{ python_dependencies | tojson }})
{% endif -%})

stub = Stub(APP_NAME)

{% include "functions.py.tpl" %}
