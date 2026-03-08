from celery import Celery
from app import create_app
from celery.schedules import crontab

def make_celery():
    app = create_app()
    celery = Celery(
        app.import_name,
        broker='redis://localhost:6379/0',
        backend='redis://localhost:6379/0'
    )

    celery.conf.beat_schedule = {
        'daily-remainder-job':{
            'task': 'tasks.daily_remainder',
            'schedule': crontab(hour=8, minute=0),
        },
        'monthly-report-job' : {
            'task': 'tasks.monthly_doctor_report',
            'schedule': crontab(day_of_month=1, hour=10, minute=0),
        },
    }

    celery.conf.update(app.config)
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
            
    celery.Task = ContextTask
    return celery

celery = make_celery()
import tasks