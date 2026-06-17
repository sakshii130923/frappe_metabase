import time

import frappe
import jwt


def generate_embed_token(
    resource_type: str,
    resource_id: int,
    params: dict | None = None,
    expiry_min: int | None = None,
) -> str:
    """
    Generate a signed JWT for Metabase static embedding.

    Args:
        resource_type: "dashboard" or "question"
        resource_id: Metabase numeric ID
        params: dict of locked filter params (already resolved)
        expiry_min: token expiry in minutes (falls back to settings default)

    Returns:
        Signed JWT token string
    """
    settings = frappe.get_single("Metabase Settings")

    if not settings.server_url or not settings.get_password("secret_key"):
        frappe.throw(
            "Metabase is not configured. Go to Metabase Settings and add your "
            "server URL and embedding secret key.",
            title="Metabase Not Configured",
        )

    secret_key = settings.get_password("secret_key")
    expiry = expiry_min or settings.default_expiry_min or 10

    payload = {
        "resource": {resource_type: resource_id},
        "params": params or {},
        "exp": round(time.time()) + (expiry * 60),
    }

    token = jwt.encode(payload, secret_key, algorithm="HS256")

    return token


def build_embed_url(
    resource_type: str,
    token: str,
    show_border: bool = False,
    show_title: bool = False,
    dark_mode: bool = False,
) -> str:
    """
    Build the full Metabase embed iframe URL.

    Args:
        resource_type: "dashboard" or "question"
        token: signed JWT token
        show_border: show Metabase border
        show_title: show Metabase title bar
        dark_mode: apply night theme

    Returns:
        Full embed URL string
    """
    settings = frappe.get_single("Metabase Settings")
    server_url = settings.server_url.rstrip("/")

    bordered = "true" if show_border else "false"
    titled = "true" if show_title else "false"
    theme = "&theme=night" if dark_mode else ""

    url = (
        f"{server_url}/embed/{resource_type}/{token}"
        f"#bordered={bordered}&titled={titled}{theme}"
    )

    return url
