import os
from typing import Any, Generic, List, TypeVar

from cryptography.fernet import Fernet
from pydantic import BaseModel, field_validator

U = TypeVar("U", bound="BaseUserConfig")
B = TypeVar("B", bound="BaseBookingSlot")
R = TypeVar("R", bound="BaseReleaseSchedule")


class BaseUserConfig(BaseModel):
    id: str
    username: str
    password: str
    card_number: str
    card_expiry: str
    card_cvc: str

    @field_validator(
        "password", "card_number", "card_expiry", "card_cvc", mode="before"
    )
    def decrypt_fields(cls, v: str) -> str:
        f = Fernet(os.environ["ENCRYPTION_KEY"])
        return f.decrypt(v.encode()).decode()


class BaseReleaseSchedule(BaseModel):
    id: str
    days: int
    hours: float
    minutes: int


class BaseBookingSlot(BaseModel):
    user: str
    id: str | None = None


class BaseConfig(BaseModel, Generic[U, B, R]):
    users: List[U]
    booking_slots: List[B]
    release_schedules: List[R]

    def get_rs_by_id(self, rs_id: str) -> R:
        for rs in self.release_schedules:
            if rs.id == rs_id:
                return rs
        raise ValueError(f"Release schedule with ID {rs_id} not found")

    def get_user_by_id(self, user_id: str) -> U:
        for u in self.users:
            if u.id == user_id:
                return u

        raise ValueError(f"User with ID {user_id} not found")

    def get_bs_by_id(self, bs_id: str) -> B:
        for bs in self.booking_slots:
            if bs.id == bs_id:
                return bs

        raise ValueError(f"Booking slot with ID {bs_id} not found")


class BaseBookingConfig(BaseModel):
    user: Any
    booking_slot: Any
