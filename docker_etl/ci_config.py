import os
import sys
from pathlib import Path

import click
import jinja2
import yaml
from yaml.scanner import ScannerError

from docker_etl.file_utils import (
    CI_JOB_NAME,
    CI_WORKFLOW_NAME,
    ROOT_DIR,
    find_file_in_jobs,
)

CI_DIR = os.path.join(ROOT_DIR, ".circleci")
CI_CONFIG_TEMPLATE = "config.template.yml"

CI_CONFIG_HEADER = """###
# This config.yml was generated by docker-etl/ci_config.py.
# Changes should be made to templates/config.template.yml and re-generated.
###"""


def validate_yaml(yaml_path: Path) -> bool:
    """Load a yaml file and return the success of the parse."""
    with open(yaml_path) as f:
        try:
            yaml.safe_load(f)
        except ScannerError:
            return False
    return True


def update_config(dry_run: bool = False) -> str:
    """Collect job and workflow configs per job and create new config."""
    template_loader = jinja2.FileSystemLoader(CI_DIR)
    template_env = jinja2.Environment(loader=template_loader)
    config_template = template_env.get_template("config.template.yml")

    job_configs = sorted(find_file_in_jobs(CI_JOB_NAME))
    workflow_configs = sorted(find_file_in_jobs(CI_WORKFLOW_NAME))

    invalid_configs = [
        str(conf.relative_to(ROOT_DIR))
        for conf in job_configs + workflow_configs
        if not validate_yaml(conf)
    ]
    if len(invalid_configs) > 0:
        print("Error: Invalid CI configs", file=sys.stderr)
        print("\n".join(invalid_configs), file=sys.stderr)
        sys.exit(1)

    config_text = config_template.render(
        config_header=CI_CONFIG_HEADER,
        jobs="\n\n".join([file_path.read_text() for file_path in job_configs]),
        workflows="\n\n".join(
            [file_path.read_text() for file_path in workflow_configs]
        ),
    )

    if dry_run:
        print(config_text)
    else:
        with open(ROOT_DIR / ".circleci" / "config.yml", "w") as f:
            f.write(config_text)

    return config_text


@click.command()
@click.option(
    "--dry-run/--no-dry-run",
    default=False,
    help="Dry run will print to stdout instead of overwriting config.yml",
)
def main(dry_run: bool):
    update_config(dry_run)


if __name__ == "__main__":
    main()