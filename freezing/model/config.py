import logging
import os
from datetime import tzinfo

import pytz
from colorlog import ColoredFormatter
from envparse import env

envfile = os.environ.get("APP_SETTINGS", os.path.join(os.getcwd(), ".env"))

if os.path.exists(envfile):
    env.read_envfile(envfile)

_basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


class Config:
    DEBUG: bool = env("DEBUG", cast=bool, default=False)

    # It is valid to use the model classes without this configured, as we do from
    # freezing-nq, so this variable is optional.
    SQLALCHEMY_URL = env("SQLALCHEMY_URL", default="")

    TIMEZONE: tzinfo = env(
        "TIMEZONE",
        default="America/New_York",
        postprocessor=lambda val: pytz.timezone(val),
    )


config = Config()


def init_logging(loglevel: int = logging.INFO, color: bool = False):
    """
    Initialize the logging subsystem and create a logger for this class,
    using passed in optparse options.

    :param level: The log level (e.g. logging.DEBUG)
    :return:
    """

    ch = logging.StreamHandler()
    ch.setLevel(loglevel)

    if color:
        formatter = ColoredFormatter(
            "%(log_color)s%(levelname)-8s%(reset)s [%(name)s] %(message)s",
            datefmt=None,
            reset=True,
            log_colors={
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "red",
            },
        )
    else:
        formatter = logging.Formatter("%(levelname)-8s [%(name)s] %(message)s")

    ch.setFormatter(formatter)

    loggers = [
        logging.getLogger("freezing"),
        logging.getLogger("stravalib"),
        logging.getLogger("requests"),
        logging.root,
    ]

    for l in loggers:
        if l is logging.root:
            l.setLevel(logging.DEBUG)
        else:
            l.setLevel(logging.INFO)
        l.addHandler(ch)
