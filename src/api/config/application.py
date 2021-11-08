"""Application Config."""
# cisagov Libraries
from api.manager import ConfigManager
from api.schemas.config_schema import ConfigPostSchema


class AppConfig:
    """AppConfig."""

    config = {
        "REPORTING_FROM_ADDRESS": None,
        "REPORTING_INTERFACE_TYPE": None,
        "REPORTING_SMTP_HOST": None,
        "REPORTING_SMTP_USERNAME": None,
        "REPORTING_SMTP_PASSWORD": None,
        "REPORTING_MAILGUN_DOMAIN": None,
        "REPORTING_MAILGUN_API_KEY": None,
        "REPORTING_SES_ARN": None,
    }

    def __init__(self):
        """Init."""
        self.config_manager = ConfigManager()
        self.load()

    def get(self, key):
        """Get config by key."""
        self.load()
        return self.config[key]

    def load(self):
        """Load settings from database."""
        for c in self.config_manager.all():
            self.config[c["key"]] = c["value"]
        return self.config

    def update(self, data):
        """Update with new settings."""
        self.load()
        data = ConfigPostSchema().load(data)
        for k, v in self.config.items():
            if k in data:
                v = data[k]
                self.config[k] = v
            self.config_manager.upsert(
                query={"key": k},
                data={"key": k, "value": v},
            )
        return self.config
