# Standard Python Libraries
import logging
import time

# cisagov Libraries
from api.app import app
from api.manager import LoggingManager

class DatabaseHandler(logging.Handler):
    '''
    Customized logging handler that adds logs to a collection.
    '''
    def __init__(self):
        logging.Handler.__init__(self)
        self.loggingManager = LoggingManager()
        self.level = logging.ERROR

    def emit(self, record):
        with app.app_context():
            # Set current time
            tm = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(record.created))
            try:
                msg = self.format(record)
                log = {"error_message": msg, "datetime": tm}
                self.loggingManager.save(log)

            except:
                self.handleError(record)