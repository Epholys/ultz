import os
import csv
import logging

from pytz import timezone as tz
from pytz.exceptions import UnknownTimeZoneError as UTZE

_logger = logging.getLogger(__name__)

UnknownTimeZoneError = UTZE

_shortcuts = None


def _populate_shortcuts():
    global _shortcuts
    _shortcuts = {}
    try:
        curr_dir = os.path.dirname(os.path.realpath(__file__))
        file_name = "tz-shortcuts.csv"
        full_path = curr_dir + "/" + file_name
        with open(full_path) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=",")
            for row in csv_reader:
                _shortcuts[row[0]] = row[1]
    except OSError:
        _logger.warning("Error while opening the data file, shortcuts inaccessible")
        pass


def timezone(zone):
    global _shortcuts

    if not zone:
        return None

    zone = zone.upper()

    if _shortcuts is None:
        _logger.info("Populating _shortcuts for the first time")
        _populate_shortcuts()

    if zone in _shortcuts:
        zone = _shortcuts[zone]

    return tz(zone)
