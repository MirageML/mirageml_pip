import datetime

from invoke import task

year = datetime.date.today().year
copyright_header_start = "# Copyright Mirage ML"
copyright_header_full = f"{copyright_header_start} {year}"


@task
def lint(ctx):
    ctx.run("ruff .", pty=True)


@task
def update_build_number(ctx):
    from mirageml_version import build_number as current_build_number

    new_build_number = current_build_number + 1

    assert new_build_number > current_build_number
    with open("mirageml_version/_version_generated.py", "w") as f:
        f.write(
            f"""\
{copyright_header_full}
build_number = {new_build_number}
"""
        )
