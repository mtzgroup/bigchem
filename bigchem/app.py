import ssl

from celery import Celery

from .config import settings

bigchem = Celery(
    # Name of top-level module is first argument
    # https://docs.celeryq.dev/en/stable/getting-started/first-steps-with-celery.html#application
    "bigchem",
    broker=settings.bigchem_broker_url,
    backend=settings.bigchem_backend_url,
)

bigchem.conf.update(
    # All configuration documentation here:
    # https://docs.celeryq.dev/en/stable/userguide/configuration.html
    # NOTE: Using pickle serializer so that chords receive python objects.
    # Can use JSON serializer json_dumps from qcio.utils if JSON is preferred.
    broker_connection_retry_on_startup=True,
    task_serializer="pickle",
    accept_content=["pickle"],
    result_serializer="pickle",
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=settings.bigchem_prefetch_multiplier,
    worker_concurrency=settings.bigchem_worker_concurrency,
)

# NOTE: If using SSL secured connection to broker, by default I am disabling
# client-side certificate verification. This makes things easier when running the
# broker behind a reverse proxy (like traefik) that dynamically provisions certificates.
# https://docs.celeryq.dev/en/stable/userguide/configuration.html#std-setting-broker_use_ssl
if "amqps" in settings.bigchem_broker_url:
    bigchem.conf.update(
        broker_use_ssl={
            "cert_reqs": ssl.CERT_NONE,
        },
    )
