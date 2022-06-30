"""Define a custom logging handler to send ERROR messages to the database."""

# Standard Python Libraries
import logging

# cisagov Libraries
from api.app import app
from api.manager import LoggingManager


class DatabaseHandler(logging.Handler):
    """Customized logging handler that adds logs to a collection."""

    def __init__(self):
        """Initialize the handler, load the loggingManager."""
        logging.Handler.__init__(self)
        self.loggingManager = LoggingManager()

    def emit(self, record):
        """Emit a record to the database."""
        extra = {k: v for k, v in record.__dict__.items()}
        with app.app_context():
            try:
                msg = self.format(record)
                if "source" in extra and "source_type" in extra:
                    log = {
                        "error_message": msg,
                        "source": extra["source"],
                        "source_type": extra["source_type"],
                    }
                else:
                    log = {
                        "error_message": msg,
                    }
                self.loggingManager.save(log)
            except (KeyboardInterrupt, SystemExit):
                raise
            except Exception:
                self.handleError(record)


def setLogger(name):
    """Easily set the logger with both handlers."""
    formatter = logging.Formatter("%(levelname)s:%(name)s:%(message)s")
    sh = logging.StreamHandler()
    dh = DatabaseHandler()
    sh.setLevel(logging.INFO)
    dh.setLevel(logging.ERROR)
    sh.setFormatter(formatter)
    dh.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.addHandler(sh)
    logger.addHandler(dh)
    return logger
