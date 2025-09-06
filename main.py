import logging
import time

from app.core.scheduler import Scheduler
from app.core.settings import load_config
from app.tasks.scheduling import make_schedules

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    settings = load_config()
    scheduler = Scheduler()

    scheduled_tasks = make_schedules(settings)
    for task in scheduled_tasks:
        scheduler.schedule_task(
            name=task.name,
            run_at=task.run_at,
            action=task.action,
            args=task.args,
            kwargs=task.kwargs,
        )

    if settings.app.add_debug_task:
        import datetime

        import pytz

        from app.booking.clubspark import make_clubspark_booking

        tz = pytz.timezone(settings.app.timezone)
        scheduler.schedule_task(
            name="debugging task",
            run_at=datetime.datetime.now(tz) + datetime.timedelta(seconds=10),
            action=make_clubspark_booking,
            args=[
                settings.clubspark.get_user_by_id("liam"),
                settings.clubspark.get_bs_by_id("liamthurs"),
                "2025-09-11",
            ],
        )

    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()
