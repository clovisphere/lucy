import logging
import os
import subprocess

import structlog


def get_git_hash():
    try:
        # Get the current Git commit hash (short version)
        return (
            subprocess.check_output(["git", "rev-parse", "--short=8", "HEAD"])
            .strip()
            .decode()
        )
    except subprocess.CalledProcessError:
        return "development"


# Set the minimum log level

# fmt: off
logging.basicConfig(level=logging.DEBUG) if os.getenv("ENVIRONMENT") == "development" \
        else logging.basicConfig(level=logging.INFO)
# fmt: on

# Add release # to logs:-)
structlog.contextvars.bind_contextvars(release=get_git_hash())

log = structlog.get_logger()
