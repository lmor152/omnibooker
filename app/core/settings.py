from dataclasses import dataclass
from typing import Union, cast

import yaml
from dotenv import load_dotenv
from pydantic import BaseModel
from pydantic_settings import BaseSettings

from app.core.config.better import (
    BetterBookingSlot,
    BetterConfig,
    BetterReleaseSchedule,
    BetterUserConfig,
)
from app.core.config.clubspark import (
    ClubsparkBookingSlot,
    ClubsparkConfig,
    ClubsparkReleaseSchedule,
    ClubsparkUserConfig,
)
from app.core.config.gymbox import (
    GymboxBookingSlot,
    GymboxConfig,
    GymboxReleaseSchedule,
    GymboxUserConfig,
)

UserConfigType = Union[BetterUserConfig, GymboxUserConfig, ClubsparkUserConfig]
BookingSlotType = Union[BetterBookingSlot, GymboxBookingSlot, ClubsparkBookingSlot]
ReleaseScheduleType = Union[
    BetterReleaseSchedule, GymboxReleaseSchedule, ClubsparkReleaseSchedule
]

_ = load_dotenv()


class AppConfig(BaseSettings):
    timezone: str
    lookahead_days: int
    emails_enabled: bool
    add_debug_task: bool
    encryption_key: str
    smtp_username: str
    smtp_password: str
    smtp_host: str
    smtp_port: int
    email_from: str


class Config(BaseModel):
    app: AppConfig
    clubspark: ClubsparkConfig
    better: BetterConfig
    gymbox: GymboxConfig


@dataclass
class ConfigLoader:
    user_model: type[UserConfigType]
    booking_slot_model: type[BookingSlotType]
    release_schedule_model: type[ReleaseScheduleType]


model_loader_map = {
    "better": ConfigLoader(
        user_model=BetterUserConfig,
        booking_slot_model=BetterBookingSlot,
        release_schedule_model=BetterReleaseSchedule,
    ),
    "gymbox": ConfigLoader(
        user_model=GymboxUserConfig,
        booking_slot_model=GymboxBookingSlot,
        release_schedule_model=GymboxReleaseSchedule,
    ),
    "clubspark": ConfigLoader(
        user_model=ClubsparkUserConfig,
        booking_slot_model=ClubsparkBookingSlot,
        release_schedule_model=ClubsparkReleaseSchedule,
    ),
}


def load_config(config_path: str = "config.yml") -> "Config":
    _ = load_dotenv()
    with open(config_path, "r") as file:
        config_data = yaml.safe_load(file)

    app_config = AppConfig.model_validate(config_data["app"])

    users: dict[str, list[UserConfigType]] = {}
    for booker_key, user_configs in config_data["users"].items():
        for user_config in user_configs:
            users[booker_key] = users.get(booker_key, [])
            model = model_loader_map[booker_key].user_model
            users[booker_key].append(model.model_validate(user_config))

    # Process booking slots for each booker type
    booking_slots: dict[str, list[BookingSlotType]] = {}
    for booker_key, slots in config_data["booking_slots"].items():
        for slot in slots:
            booking_slots[booker_key] = booking_slots.get(booker_key, [])
            model = model_loader_map[booker_key].booking_slot_model
            booking_slots[booker_key].append(model.model_validate(slot))

    # Process release schedules for each booker type
    release_schedules: dict[str, list[ReleaseScheduleType]] = {}
    for booker_key, schedules in config_data["release_schedules"].items():
        for schedule in schedules:
            release_schedules[booker_key] = release_schedules.get(booker_key, [])
            model = model_loader_map[booker_key].release_schedule_model
            release_schedules[booker_key].append(model.model_validate(schedule))

    return Config(
        app=app_config,
        clubspark=ClubsparkConfig(
            users=cast(list[ClubsparkUserConfig], users.get("clubspark", [])),
            booking_slots=cast(
                list[ClubsparkBookingSlot], booking_slots.get("clubspark", [])
            ),
            release_schedules=cast(
                list[ClubsparkReleaseSchedule], release_schedules.get("clubspark", [])
            ),
        ),
        better=BetterConfig(
            users=cast(list[BetterUserConfig], users.get("better", [])),
            booking_slots=cast(
                list[BetterBookingSlot], booking_slots.get("better", [])
            ),
            release_schedules=cast(
                list[BetterReleaseSchedule], release_schedules.get("better", [])
            ),
        ),
        gymbox=GymboxConfig(
            users=cast(list[GymboxUserConfig], users.get("gymbox", [])),
            booking_slots=cast(
                list[GymboxBookingSlot], booking_slots.get("gymbox", [])
            ),
            release_schedules=cast(
                list[GymboxReleaseSchedule], release_schedules.get("gymbox", [])
            ),
        ),
    )


settings = load_config()
