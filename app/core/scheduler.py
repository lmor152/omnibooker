from datetime import datetime
from typing import Any, Callable, Optional

from apscheduler.schedulers.background import BackgroundScheduler  # type: ignore
from apscheduler.triggers.date import DateTrigger  # type: ignore


class Scheduler:
    def __init__(self) -> None:
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()  # type: ignore

    def schedule_task(
        self,
        name: str,
        run_at: datetime,
        action: Callable[..., None],
        args: Optional[list[Any]] = None,
        kwargs: Optional[dict[Any, Any]] = None,
    ) -> None:
        self.scheduler.add_job(  # type: ignore
            func=action,
            trigger=DateTrigger(run_date=run_at),
            args=args if args else [],
            kwargs=kwargs if kwargs else {},
            id=name,
            name=name,
            replace_existing=True,
        )

    def shutdown(self) -> None:
        self.scheduler.shutdown()  # type: ignore
