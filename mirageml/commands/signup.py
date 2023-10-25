import os

import keyring
import segment.analytics as analytics
import typer

from ..constants import ANALYTICS_WRITE_KEY, SERVICE_ID, supabase

analytics.write_key = ANALYTICS_WRITE_KEY


def signup():
    try:
        # use typer to get user email and password
        email = typer.prompt("Email")
        password = typer.prompt("Password", hide_input=True, confirmation_prompt="Confirm Password")

        response = supabase.auth.sign_up({"email": email, "password": password})
        user = response.user
        session = response.session

        user_id = user.id
        email = user.email
        access_token = session.access_token
        refresh_token = session.refresh_token
        expires_at = session.expires_at

        keyring.set_password(SERVICE_ID, "user_id", user_id)
        keyring.set_password(SERVICE_ID, "email", email)
        keyring.set_password(SERVICE_ID, "access_token", access_token)
        keyring.set_password(SERVICE_ID, "refresh_token", refresh_token)
        keyring.set_password(SERVICE_ID, "expires_at", str(expires_at))
        analytics.identify(
            user_id,
            {
                "email": email,
            },
        )
        typer.secho(f"Successfully signed up as {email}", fg=typer.colors.BRIGHT_GREEN, bold=True)
        os._exit(0)
    except Exception as e:
        typer.secho(f"Error signing up: {e}", fg=typer.colors.BRIGHT_RED, bold=True)
        os._exit(1)
