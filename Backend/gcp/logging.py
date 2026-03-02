import logging

try:
    from google.cloud import logging as cloud_logging
except Exception:
    cloud_logging = None


def configure_logging() -> None:
    try:
        if cloud_logging is None:
            raise RuntimeError("Cloud logging package unavailable")

        client = cloud_logging.Client()
        client.setup_logging()
    except Exception:
        logging.basicConfig(level=logging.INFO)
