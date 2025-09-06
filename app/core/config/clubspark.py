from pydantic import model_validator

from app.core.config.base import (
    BaseBookingConfig,
    BaseBookingSlot,
    BaseConfig,
    BaseReleaseSchedule,
    BaseUserConfig,
)


class ClubsparkUserConfig(BaseUserConfig):
    email: str | None = None


class ClubsparkBookingSlot(BaseBookingSlot):
    target_day: str
    target_times: list[str]
    target_park: str
    target_courts: list[int]
    double_session: bool = False


class ClubsparkReleaseSchedule(BaseReleaseSchedule):
    pass


class ClubsparkConfig(
    BaseConfig[ClubsparkUserConfig, ClubsparkBookingSlot, ClubsparkReleaseSchedule]
):
    users: list[ClubsparkUserConfig]
    booking_slots: list[ClubsparkBookingSlot]
    release_schedules: list[ClubsparkReleaseSchedule]

    @model_validator(mode="after")
    def validate_release_schedules(self):
        target_parks = {bs.target_park for bs in self.booking_slots}
        schedule_parks = {rs.id for rs in self.release_schedules}

        if schedule_parks - target_parks:
            missing = schedule_parks - target_parks
            raise ValueError(f"Release schedules found for unknown parks: {missing}")

        return self


class ClubsparkBookingConfig(BaseBookingConfig):
    user: ClubsparkUserConfig
    booking_slot: ClubsparkBookingSlot
