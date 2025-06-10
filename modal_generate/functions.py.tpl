{% for remote_function in remote_functions -%}
@stub.function(
    image=image,
    {% if remote_function.gpu -%}
    gpu={{ remote_function.gpu }},
    {% endif -%}
    {% if remote_function.keep_warm -%}
    keep_warm={{ remote_function.keep_warm }},
    {% endif -%}
    {% if remote_function.timeout -%}
    timeout={{ remote_function.timeout }},
    {% endif -%}
    {% if remote_function.volume -%}
    network_file_systems={MOUNT_PATH: volume},
    {% endif -%}
)
def {{ remote_function.name }}():
    pass
{% endfor -%}
