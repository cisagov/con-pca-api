# Third-Party Libraries
from apscheduler.schedulers.background import BackgroundScheduler

# cisagov Libraries
from api.config.environment import EMAIL_MINUTES, FAILED_EMAIL_MINUTES, TASK_MINUTES
from api.phish import emails_job
from api.tasks import failed_emails_job, tasks_job

from utils.logging import setLogger

logger = setLogger("apscheduler")

def startScheduler():
    sched = BackgroundScheduler(logger=logger)
    sched.configure()
    sched.add_job(emails_job, "interval", minutes=EMAIL_MINUTES, max_instances=20)
    sched.add_job(tasks_job, "interval", minutes=TASK_MINUTES, max_instances=20)
    sched.add_job(
        failed_emails_job, "interval", minutes=FAILED_EMAIL_MINUTES, max_instances=3
    )
    sched.start()

    return sched
