import os
from pathlib import Path

import click
import questionary
from jinja2 import Environment, select_autoescape
from slugify import slugify

from .filter import keep_warm_filter, num_gpu_filter, gpu_model_filter
from .schema import RemoteFunctionDefinition
from .template import AbsolutePathLoader, render_template
from .utils import classify


templates_folder = Path(__file__).resolve().parents[1] / 'templates'

env = Environment(
    loader=AbsolutePathLoader(templates_folder),
    autoescape=select_autoescape(['py'])
)
env.filters['classify'] = classify


@click.group()
def cli():
    pass


@cli.command()
@click.argument('name', required=True)
@click.option('--output-path', '-o', help='Output application path')
@click.option('--namespace', '-n', default=None, help='Prefix for application name')
def generate(name: str, output_path: str, namespace: str):
    click.echo(f"Generate a new Modal application: {name}")

    if namespace:
        namespace = slugify(namespace)

    provision_nfs = questionary.confirm("Add persistent storage?", default=False).ask()
    provision_log = questionary.confirm("Add structured logging?", default=True).ask()

    # System dependencies
    add_system_dependency = questionary.confirm("Add system dependencies?", default=False).ask()
    system_dependencies = []
    while add_system_dependency:
        system_dependencies.append(questionary.text("Name of dependency?").ask())
        add_system_dependency = questionary.confirm("Add another system dependency?", default=False).ask()

    # Python dependencies
    add_python_dependency = questionary.confirm("Add Python dependencies?", default=False).ask()
    python_dependencies = []
    if provision_log:
        python_dependencies.append("structlog")
    while add_python_dependency:
        python_dependencies.append(questionary.text("Name of dependency?").ask())
        add_python_dependency = questionary.confirm("Add another Python dependency?", default=True).ask()

    # Remote functions
    add_remote_function = questionary.confirm("Add remote functions?", default=True).ask()
    remote_functions = []
    while add_remote_function:
        function_name = questionary.text("Name of remote function?").ask()
        if not function_name:
            break
        remote_function_definition = RemoteFunctionDefinition(name=function_name)

        keep_warm = questionary.confirm("Keep function warm?", default=False).ask()
        keep_warm = questionary.text("Instances?").skip_if(not keep_warm, default=False).ask()
        keep_warm = keep_warm_filter(keep_warm)
        remote_function_definition.keep_warm = keep_warm

        provision_gpu = questionary.confirm("Enable GPU support?", default=False).ask()
        gpu_model = questionary.select("GPU model?",
                                       choices=["any", "T4", "L4", "A10G", "A100", "H100"],
                                       default="A10G").skip_if(not provision_gpu, default=None).ask()
        gpu_model = gpu_model_filter(gpu_model)
        num_gpus = questionary.text("Number of GPUs", default="1").skip_if(not provision_gpu, default=None).ask()
        num_gpus = num_gpu_filter(num_gpus)
        remote_function_definition.gpu = gpu_model
        remote_function_definition.num_gpus = num_gpus

        mount_volume = questionary.confirm("Mount persistent storage?", default=False).skip_if(not provision_nfs).ask()
        remote_function_definition.volume = mount_volume

        provision_secret = questionary.confirm("Provision secret?", default=False).ask()
        secret = questionary.text("Name of secret?").skip_if(not provision_secret, default=None).ask()
        remote_function_definition.secret = secret

        remote_functions.append(remote_function_definition)

        add_remote_function = questionary.confirm("Add another remote function?", default=False).ask()

    add_entity = questionary.confirm("Add entity?", default=False).ask()
    entities = []
    while add_entity:
        entity_name = questionary.text("Name of entity").ask()
        entities.append(slugify(entity_name))
        add_entity = questionary.confirm("Add another entity?").ask()

    name_components = [slugify(component) for component in name.split('.')]
    if output_path is None:
        output_path = os.path.join(*name_components)
    else:
        if not os.path.isabs(output_path):
            output_path = os.path.join(os.getcwd(), output_path)

    normalized_name = '-'.join([part for part in [namespace, name_components[-1]] if part])

    variables = {
        "name": normalized_name,
        "python_dependencies": python_dependencies,
        "remote_functions": remote_functions,
        "system_dependencies": system_dependencies,
        "entities": entities,
        "provision_nfs": provision_nfs,
        "provision_log": provision_log,
    }

    render_template(env, "__init__.py.tpl", variables, output_path)
    render_template(env, "constants.py.tpl", variables, output_path)
    render_template(env, "schema.py.tpl", variables, output_path)

    click.secho(f"You can now run our deploy the app:\n\n"
                f"\t$ modal deploy {name}\n"
                f"\t$ modal run {name}\n",
                fg="green",
                bold=True)


if __name__ == "__main__":
    cli()
