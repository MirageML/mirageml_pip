import os

import keyring
import segment.analytics as analytics
import typer

from ..constants import ANALYTICS_WRITE_KEY, SERVICE_ID, supabase

analytics.write_key = ANALYTICS_WRITE_KEY


def login():
    try:
        user_id = keyring.get_password(SERVICE_ID, "user_id")
        email = typer.prompt("Email")
        password = typer.prompt(
            "Password", hide_input=True, confirmation_prompt="Confirm Password" if user_id is None else False
        )
        response = None
        try:
            if user_id:
                response = supabase.auth.sign_in_with_password({"email": email, "password": password})
            else:
                response = supabase.auth.sign_up({"email": email, "password": password})
        except Exception as e:
            if str(e) == "User already registered":
                response = supabase.auth.sign_in_with_password({"email": email, "password": password})
            else:
                raise e

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
        typer.secho("Successfully logged in", fg=typer.colors.BRIGHT_GREEN, bold=True)
        os._exit(0)
    except Exception as e:
        print(e)
        typer.secho("Error logging in. Please try again", fg=typer.colors.BRIGHT_RED, bold=True)
        os._exit(1)
