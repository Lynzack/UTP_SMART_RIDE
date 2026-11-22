from datetime import datetime


def is_eligible(driver, passenger):

    # 1. Check whether travel dates match
    if driver["Date"] != passenger["Date"]:
        return False

    # 2. Prevent users from matching with themselves
    if driver["UserID"] == passenger["UserID"]:
        return False

    # 3. Convert departure times into datetime objects
    driver_time = datetime.strptime(
        str(driver["departureTime"]).strip(), "%I:%M %p"
    )

    passenger_time = datetime.strptime(
        str(passenger["preferredTime"]).strip(), "%I:%M %p"
    )

    # 4. Calculate time difference in minutes
    time_difference = abs(
        (driver_time - passenger_time).total_seconds() / 60
    )

    # 5. Allow a maximum difference of 15 minutes
    return time_difference <= 15