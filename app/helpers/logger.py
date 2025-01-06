import logging
import os
import subprocess

import structlog


def get_git_hash():
    try:
        # Get the current Git commit hash (short version)
        return (
            subprocess.check_output(["git", "rev-parse", "--short=15", "HEAD"])
            .strip()
            .decode()
        )
    except subprocess.CalledProcessError:
        return "development"


# Little hack 😊 to suppress 'faiss.loader' and 'httpx' INFO logs
logging.getLogger("faiss.loader").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)

# Set the minimum log level
if os.getenv("ENVIRONMENT", "") == "development":
    structlog.configure(
        wrapper_class=structlog.make_filtering_bound_logger(logging.DEBUG)
    )
else:
    structlog.configure(wrapper_class=structlog.make_filtering_bound_logger(logging.INFO))

# Add release # to logs:-)
structlog.contextvars.bind_contextvars(release=get_git_hash())

log = structlog.get_logger()
