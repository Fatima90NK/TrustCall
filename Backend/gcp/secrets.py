import os
from functools import lru_cache

try:
    from google.cloud import secretmanager
except Exception:
    secretmanager = None


@lru_cache(maxsize=128)
def get_secret(secret_id: str, version: str = "latest") -> str | None:
    env_value = os.getenv(secret_id)
    if env_value:
        return env_value

    if "/" not in secret_id:
        return None

    project_id = os.getenv("PROJECT_ID")
    if not project_id or secretmanager is None:
        return None

    try:
        client = secretmanager.SecretManagerServiceClient()
        candidates = [secret_id, secret_id.replace("/", "-")]

        for candidate in candidates:
            name = f"projects/{project_id}/secrets/{candidate}/versions/{version}"
            try:
                response = client.access_secret_version(request={"name": name})
                return response.payload.data.decode("utf-8")
            except Exception:
                continue

        return None
    except Exception:
        return None
