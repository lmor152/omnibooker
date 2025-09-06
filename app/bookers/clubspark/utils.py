import datetime

from app.core.config.clubspark import ClubsparkBookingSlot
from app.models.clubspark_responses import ResourceSlot, TimeSlot


def rank_slots(
    slots: list[TimeSlot], booking_slot: ClubsparkBookingSlot
) -> list[tuple[int, ResourceSlot]]:
    preferred_times_ints = [timestr_to_int(t) for t in booking_slot.target_times]
    preferred_courts = [f"Court {i}" for i in booking_slot.target_courts]

    ranked_slots: list[tuple[int | float, int, ResourceSlot]] = []
    for ts in slots:
        time_rank = index_rank(ts.Time, preferred_times_ints)
        for resource in ts.Resources:
            court_rank = index_rank(resource.Name, preferred_courts)

            total_rank = 100 * time_rank + court_rank
            ranked_slots.append((total_rank, ts.Time, resource))

    # remove the invalid slots before sorting
    valid_slots = [
        (rank, time, resource) for (rank, time, resource) in ranked_slots if rank < 9999
    ]
    valid_slots.sort()
    return [(time, resource) for (_, time, resource) in valid_slots]


def index_rank(item: str | int, preferred_list: list[str] | list[int]) -> int | float:
    """Return the index of item in preferred_list, or len(preferred_list) if not found."""
    if item not in preferred_list:
        return float("inf")

    return preferred_list.index(item)  # type: ignore


def timestr_to_int(time: str) -> int:
    """Convert a time string in HH:MM to integer representing minutes since midnight."""
    try:
        hour, minute = map(int, time.split(":"))
        return hour * 60 + minute
    except ValueError as err:
        raise ValueError(
            f"Invalid time format: {time}. Expected HH:MM format."
        ) from err


def timestr_to_time(time: str) -> datetime.time:
    """Convert a time string in HH:MM to a datetime.time object."""
    try:
        hour, minute = map(int, time.split(":"))
        return datetime.time(hour=hour, minute=minute)
    except ValueError as err:
        raise ValueError(
            f"Invalid time format: {time}. Expected HH:MM format."
        ) from err
