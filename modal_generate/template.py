import os
import subprocess
from typing import Any

import click
from jinja2 import BaseLoader, Environment


class AbsolutePathLoader(BaseLoader):
    def __init__(self, base_dir):
        self.base_dir = base_dir

    def get_source(self, environment, template):
        abs_template_path = os.path.join(self.base_dir, template)
        if not os.path.exists(abs_template_path):
            raise FileNotFoundError(f"Template '{abs_template_path}' does not exist")

        with open(abs_template_path, 'r') as f:
            source = f.read()

        mtime = os.path.getmtime(abs_template_path)

        return source, abs_template_path, lambda: mtime == os.path.getmtime(abs_template_path)


def render_template(env: Environment,
                    template: str,
                    variables: dict[str, Any],
                    output_path: str):
    filename = ".".join([part for part in template.split(".") if part != "tpl"])
    dist_path = os.path.join(str(output_path), filename)
    template = env.get_template(template)
    output = template.render(variables)

    os.makedirs(os.path.dirname(dist_path), exist_ok=True)
    with open(dist_path, 'w') as f:
        f.write(output)

    _format_template(str(dist_path))


def _format_template(file: str):
    try:
        subprocess.run(["ruff", "format", file], capture_output=True, check=True)
    except subprocess.CalledProcessError:
        click.secho(f"Failed formatting file: {file}", fg="yellow", bold=True)
