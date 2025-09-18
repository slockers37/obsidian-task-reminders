from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

from sender import execute_send

class ReminderScheduler:
    def __init__(self, db_path: str):
        jobstores = {
            'default': SQLAlchemyJobStore(url=f'sqlite:///{db_path}')
        }
        self.scheduler = BackgroundScheduler(jobstores=jobstores)

    def schedule_task(self, task_id: str, due: datetime):
        """Schedules a reminder for a given task."""
        job = self.scheduler.add_job(
            execute_send,
            'date',
            run_date=due,
            args=[task_id],
            id=task_id,
            replace_existing=True
        )
        return job

    def start(self):
        self.scheduler.start()

    def stop(self):
        self.scheduler.shutdown()
