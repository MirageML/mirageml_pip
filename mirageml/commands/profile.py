import keyring
import typer

from ..constants import SERVICE_ID


def profile():
    email = keyring.get_password(SERVICE_ID, "email")
    typer.secho("Current Profile", fg=typer.colors.BRIGHT_GREEN, bold=True)
    typer.echo(f"Email: {email}")
