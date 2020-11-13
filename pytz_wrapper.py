from pytz import timezone as tz, all_timezones as all_tz


def timezone(location):
    return tz(location)


all_timezones = all_tz
