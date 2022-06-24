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
        self.level = logging.ERROR

    def emit(self, record):
        """Emit a record to the database."""
        with app.app_context():
            try:
                msg = self.format(record)
                log = {
                    "error_message": msg.replace("ERROR:root:", "")
                    if "ERROR:root:"
                    else msg
                }
                self.loggingManager.save(log)
            except (KeyboardInterrupt, SystemExit):
                raise
            except Exception:
                self.handleError(record)
