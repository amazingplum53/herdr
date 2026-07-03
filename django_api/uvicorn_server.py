from multiprocessing import cpu_count
import uvicorn

import sys
import os

from utils.keys import handle_secrets
from utils.variables import load_variables


def bootstrap():
    STACK = os.getenv("STACK", "local")
    print(f"Using {STACK} env file")

    load_variables(STACK)
    handle_secrets(STACK)

bootstrap()

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_api.settings")

from django.conf import settings


no_of_workers = 1 if settings.DEBUG else cpu_count()

if __name__ == "__main__":
    uvicorn.run(
        "django_api.asgi:application", 
        host="0.0.0.0",
        port=8000,
        workers=no_of_workers,
        timeout_keep_alive=5,
        log_level="info",
        reload=settings.DEBUG,
        lifespan="off"
    )