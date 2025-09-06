# Omnibooker

This is a Python-based app for emulating the booking process for various apps. It is useful for when bookings are released in advance but are quickly reserved and you cbf that kind of admin.

The following apps are supported / in the works:

| App | Status |
|-----|--------|
| Clubspark | ✅ Completed  |
| Better    | 📆 Planned    |
| Gymbox    | 📆 Planned    |

## How it works 
This app uses `config.yml` to specify booking slots for the app to attempt to book once bookings open based on the corresponding `release_schedule`.


## How to add new apps 
Apps are stored in the `/bookers` directory and must implement a function to attempt booking based on config files in `/config`.

Each app needs to be reverse engineered based on analysing network traffic. This can be done either: 
* Completing a booking via the browser and analysing traffic in the Network tab
* Proxying your phone traffic through an tool such as MITM to analyse the traffic sent when using a mobile app


## Notes 
* Some APIs will block IP addresses that are non-residential. Running this from cloud may not work for your app
* Set the SMTP environment variables to enable sending notifications about booking results to your email
* The app will require some form of password and/or card info. This info is encrypted but it's still recommended to limit spend by using a virtual card with a spending limit or similar.


