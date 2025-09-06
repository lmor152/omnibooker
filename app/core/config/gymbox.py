from app.core.config.base import (
    BaseBookingConfig,
    BaseBookingSlot,
    BaseConfig,
    BaseReleaseSchedule,
    BaseUserConfig,
)


class GymboxUserConfig(BaseUserConfig):
    pass


class GymboxBookingSlot(BaseBookingSlot):
    pass


class GymboxReleaseSchedule(BaseReleaseSchedule):
    pass


class GymboxConfig(
    BaseConfig[GymboxUserConfig, GymboxBookingSlot, GymboxReleaseSchedule]
):
    users: list[GymboxUserConfig]
    booking_slots: list[GymboxBookingSlot]
    release_schedules: list[GymboxReleaseSchedule]


class GymboxBookingConfig(BaseBookingConfig):
    user: GymboxUserConfig
    booking_slot: GymboxBookingSlot
