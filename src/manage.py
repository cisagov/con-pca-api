#!/usr/bin/env python
import os
import sys


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    try:
        from django.core.management import execute_from_command_line

        # if os.environ.get("DEBUG_PTVSD", 0) == 1:
        #     import ptvsd

        #     ptvsd.enable_attach(address=("0.0.0.0", 5678))
        #     print("NOT Attached remote debugger")
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)
