import os

# Set cycle minutes or 90 days
CYCLE_MINUTES = int(os.environ.get("CYCLE_MINUTES", 129600))

# Give some time for final phishing numbers to go
# through before starting a new subscription
CAMPAIGN_MINUTES = int(CYCLE_MINUTES * 2 / 3)

# Set monthly minutes or 30 days
MONTHLY_MINUTES = int(os.environ.get("MONTHLY_MINUTES", 43200))

# set yearly minutes or 365 days
YEARLY_MINUTES = int(os.environ.get("YEARLY_MINUTES", 525600))
