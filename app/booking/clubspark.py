import logging

from app.bookers.clubspark.app_booker import AppBooker
from app.bookers.clubspark.stripe_manager import StripeManager
from app.bookers.clubspark.utils import rank_slots
from app.core.config.clubspark import ClubsparkBookingSlot, ClubsparkUserConfig
from app.core.settings import settings
from app.tasks.emails import send_email

LOGGER = logging.getLogger(__name__)


def make_clubspark_booking(
    user: ClubsparkUserConfig, booking_slot: ClubsparkBookingSlot, date: str
) -> None:
    try:
        _make_clubspark_booking(user, booking_slot, date)

    except Exception as e:
        print(f"Error occurred while making booking: {e}")
        if settings.app.emails_enabled:
            send_email(
                f"Failed to book {booking_slot.target_park} on {date}",
                f"Error occurred while making booking: {e}",
                user.email,
            )
        else:
            LOGGER.info("Suppressing email send")


def _make_clubspark_booking(
    user: ClubsparkUserConfig, booking_slot: ClubsparkBookingSlot, date: str
) -> None:
    booker = AppBooker(user)
    stripe = StripeManager()
    current_user = booker.get_current_user()
    duration = 120 if booking_slot.double_session else 60

    available_slots = booker.get_availability_times(
        venue_slug=booking_slot.target_park, date=date, duration=duration
    )

    if len(available_slots.Times) == 0:
        raise ValueError("There are no available slots for the requested date")
    LOGGER.info("Available Slots:")
    for slot in available_slots.Times:
        LOGGER.info(f"    {slot}")

    ranked_slots = rank_slots(available_slots.Times, booking_slot)

    if len(ranked_slots) == 0:
        raise ValueError(
            "There are no available slots that meet the requested times/courts"
        )
    LOGGER.info("Ranked Slots:")
    for slot in ranked_slots:
        LOGGER.info(f"    {slot}")

    venue_settings = booker.get_app_settings(booking_slot.target_park)

    LOGGER.info("Venue Settings:")
    LOGGER.info(venue_settings)

    card_month, card_year = user.card_expiry.split("/")
    payment_method = stripe.payment_method(
        stripe_account=venue_settings.Venue.StripeAccountID,
        stripe_key=venue_settings.StripePublishableKey,
        card_number=user.card_number,
        card_exp_year=str(int(card_year)),
        card_exp_month=str(int(card_month)),
        card_cvc=user.card_cvc,
        email=current_user.EmailAddress,
    )

    LOGGER.info("Created Payment Method:")
    LOGGER.info(payment_method)

    retry_cap = 3
    for i, (time, resource) in enumerate(ranked_slots):
        i += 1
        if i > retry_cap:
            LOGGER.info("Hit retry cap - exiting")
            return

        LOGGER.info("Attempting to book slot:")
        LOGGER.info(f"{time}, {resource}")
        try:
            payment = booker.create_payment(
                current_user.FirstName + " " + current_user.LastName,
                cost=resource.Cost,
                payment_method_id=payment_method.id,
                scope=resource.SessionID,
                venue_id=venue_settings.Venue.ID,
            )

            LOGGER.info("Payment Made:")
            LOGGER.info(payment)
            if payment.ID is None:
                raise ValueError("Error during payment creation")

            booked_session = booker.request_session(
                venue_slug=booking_slot.target_park,
                payment_token=payment.ID,
                duration=duration,
                date=date,
                total_paid=resource.Cost,
                start_time=time,
                resource_id=resource.ID,
                session_id=resource.SessionID,
            )

            LOGGER.info("Booked session:")
            LOGGER.info(booked_session)

            if booked_session.Result < 0:
                raise ValueError("Error reserving session after payment")
            else:
                return
        except Exception as e:
            LOGGER.error(f"Error occurred while booking session: {e}")
