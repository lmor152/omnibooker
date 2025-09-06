import datetime
import uuid
from dataclasses import dataclass
from typing import Any, Callable

import pytz

from app.booking.clubspark import make_clubspark_booking
from app.core.config.better import BetterConfig
from app.core.config.clubspark import ClubsparkConfig
from app.core.config.gymbox import GymboxConfig
from app.core.settings import Config
from app.core.settings import settings as app_settings

tz = pytz.timezone(app_settings.app.timezone)
now = datetime.datetime.now(tz)
today = now.replace(hour=0, minute=0, second=0, microsecond=0)
calendar = [
    today + datetime.timedelta(days=i) for i in range(app_settings.app.lookahead_days)
]


@dataclass
class ScheduledTask:
    name: str
    run_at: datetime.datetime
    action: Callable[..., None]
    args: list[Any] | None = None
    kwargs: dict[Any, Any] | None = None


def make_clubspark_schedule(settings: ClubsparkConfig) -> list[ScheduledTask]:
    scheduled: list[ScheduledTask] = []
    for slot in settings.booking_slots:
        release_schedule = settings.get_rs_by_id(slot.target_park)
        release_offset = datetime.timedelta(
            days=release_schedule.days,
            hours=release_schedule.hours,
            minutes=release_schedule.minutes,
        )
        user_config = settings.get_user_by_id(slot.user)

        for future_day in calendar:
            if future_day.strftime("%A").lower() == slot.target_day:
                execution_time = future_day - release_offset
                uid = str(uuid.uuid4())[:4]
                scheduled_task = ScheduledTask(
                    name=f"Clubspark Booking {uid}: {slot.user} {slot.target_day} {slot.target_park} {future_day.date()}",
                    run_at=execution_time,
                    action=make_clubspark_booking,
                    args=[user_config, slot, future_day.strftime("%Y-%m-%d")],
                )
                scheduled.append(scheduled_task)

    return scheduled


def make_better_schedule(settings: BetterConfig) -> list[ScheduledTask]:
    # TODO: implement a better booking tool
    return []


def make_gymbox_schedule(settings: GymboxConfig) -> list[ScheduledTask]:
    # TODO: implement a gymbox booking tool
    return []


def make_schedules(settings: Config):
    clubspark_schedules = make_clubspark_schedule(settings.clubspark)
    better_schedules = make_better_schedule(settings.better)
    gymbox_schedules = make_gymbox_schedule(settings.gymbox)

    return clubspark_schedules + better_schedules + gymbox_schedules
