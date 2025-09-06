from app.core.config.base import (
    BaseBookingConfig,
    BaseBookingSlot,
    BaseConfig,
    BaseReleaseSchedule,
    BaseUserConfig,
)


class BetterUserConfig(BaseUserConfig):
    pass


class BetterBookingSlot(BaseBookingSlot):
    pass


class BetterReleaseSchedule(BaseReleaseSchedule):
    pass


class BetterConfig(
    BaseConfig[BetterUserConfig, BetterBookingSlot, BetterReleaseSchedule]
):
    users: list[BetterUserConfig]
    booking_slots: list[BetterBookingSlot]
    release_schedules: list[BetterReleaseSchedule]


class BetterBookingConfig(BaseBookingConfig):
    user: BetterUserConfig
    booking_slot: BetterBookingSlot
