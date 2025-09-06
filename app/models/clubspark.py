from pydantic import BaseModel


class Resource(BaseModel):
    ID: str
    Name: str
    Number: int
    Surface: int
    Category: int


class Venue(BaseModel):
    ID: str
    Name: str
    UrlSegment: str
    Address1: str
    Address2: str | None = None
    Town: str
    County: str
    Postcode: str
    LogoIncludesVenueName: bool
    LtaManaged: bool
    HeaderStyle: int
    Features: int
    LogoWidth: int
    TimeZone: str
    CurrencyCode: str
    Interval: int
    MaximumBookingIntervals: int
    MinimumBookingIntervals: int
    MaximumBookings: int
    AdvancedBookingPeriod: int
    BookingRefundWindow: int
    BookingPaymentEnabled: bool
    GroupBookingEnabled: bool
    Latitude: float
    Longitude: float
    StripePublishableKey: str
    Resources: list[Resource]
    ClosedDates: list[str]  # ISO 8601 date strings
    IsMember: bool
    PrivatePIN: str
    PublicPIN: str
    AccessControl: int
    ParentRegionID: str


class VenueContact(BaseModel):
    VenueID: str
    VenueContactID: str
    ParentRegionID: str
    RegionID: str
    PrivatePIN: str
    VenueSystemRoles: int
    VenueName: str
    VenueUrlSegment: str
    VenueTimeZoneID: str
    VenueIsoTimeZone: str
    CreatedDateTime: str  # ISO 8601 date string
