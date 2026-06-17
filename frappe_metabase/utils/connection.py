import requests


def test_metabase_connection(server_url: str, secret_key: str) -> tuple[bool, str]:
    """
    Test connectivity to a Metabase instance.

    Hits the /api/health endpoint to verify the server is reachable,
    then validates the secret key by checking the /api/session/properties
    endpoint.

    Args:
        server_url: Metabase server URL (e.g. http://localhost:3000)
        secret_key: Embedding secret key

    Returns:
        Tuple of (success: bool, message: str)
    """
    server_url = server_url.rstrip("/")

    # Step 1: Check if server is reachable
    try:
        health_url = f"{server_url}/api/health"
        response = requests.get(health_url, timeout=10)

        if response.status_code != 200:
            return (
                False,
                f"Server returned status {response.status_code}. "
                f"Is Metabase running at {server_url}?",
            )

        health = response.json()
        if health.get("status") != "ok":
            return (
                False,
                f"Metabase health check returned: {health.get('status', 'unknown')}",
            )

    except requests.ConnectionError:
        return (
            False,
            f"Cannot connect to {server_url}. Check the URL and ensure "
            "Metabase is running.",
        )
    except requests.Timeout:
        return (False, f"Connection to {server_url} timed out after 10 seconds.")
    except Exception as e:
        return (False, f"Unexpected error: {str(e)}")

    # Step 2: Validate that embedding is enabled
    try:
        props_url = f"{server_url}/api/session/properties"
        response = requests.get(props_url, timeout=10)

        if response.status_code == 200:
            props = response.json()
            embedding_enabled = props.get("enable-embedding", False) or props.get(
                "token-features", {}
            ).get("embedding", False)

            if not embedding_enabled:
                return (
                    True,
                    "Connected, but embedding may not be enabled. "
                    "Check Metabase Admin → Settings → Embedding.",
                )

    except Exception:
        # Non-critical — connection works, just can't verify embedding status
        pass

    # Step 3: Validate secret key by attempting a token generation
    if not secret_key:
        return (True, "Connected to Metabase, but no secret key provided.")

    try:
        import jwt

        # Generate a test token — if this works, the key format is valid
        jwt.encode({"test": True}, secret_key, algorithm="HS256")
    except Exception as e:
        return (
            True,
            f"Connected to Metabase, but secret key may be invalid: {str(e)}",
        )

    return (True, "Connected — Metabase is reachable and secret key is valid.")
