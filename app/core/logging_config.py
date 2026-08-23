import logging.config

from ..core.settings import settings


class LoggingConfig:
    LOG_DIR = settings.LOG_DIR
    LOG_FILE = LOG_DIR / "app.log"

    @classmethod
    def setup(cls):
        cls.LOG_DIR.mkdir(parents=True, exist_ok=True)

        logging_config = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                },
                "file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "filename": cls.LOG_FILE,
                    "maxBytes": 2 * 1024 * 1024,
                    "backupCount": 5,
                    "encoding": "utf-8",
                    "formatter": "default",
                },
            },
            "root": {
                "handlers": ["console", "file"],
                "level": "INFO",
            },
            "loggers": {
                "uvicorn.error": {
                    "level": "INFO",
                    "handlers": ["console"],
                    "propagate": False,
                },
                "uvicorn.access": {
                    "level": "INFO",
                    "handlers": ["console"],
                    "propagate": False,
                },
                "app": {
                    "level": "INFO",
                    "handlers": ["console", "file"],
                    "propagate": False,
                },
            },
        }

        logging.config.dictConfig(logging_config)
