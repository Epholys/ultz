import os
import csv
import logging
from typing import Optional, Union, Dict, TYPE_CHECKING

import pytz
from pytz.exceptions import UnknownTimeZoneError as UTZE

_logger = logging.getLogger(__name__)

UnknownTimeZoneError = UTZE

_shortcuts: Optional[Dict[str, str]] = None

if TYPE_CHECKING:
    PyTzInfo = Union[pytz._UTCclass, pytz._StaticTzInfo, pytz._DstTzInfo]
else:
    PyTzInfo = Union[pytz.tzinfo.StaticTzInfo, pytz.tzinfo.DstTzInfo]

_shortcuts_filename = "tz-shortcuts.csv"


def _populate_shortcuts() -> None:
    global _shortcuts
    _shortcuts = {}
    try:
        curr_dir = os.path.dirname(os.path.realpath(__file__))
        file_name = _shortcuts_filename
        full_path = curr_dir + "/" + file_name
        with open(full_path) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=",")
            for row in csv_reader:
                _shortcuts[row[0]] = row[1]
    except OSError:
        _logger.warning("Error while opening the data file, shortcuts inaccessible")
        pass


def timezone(
    zone: Optional[str],
) -> Optional[PyTzInfo]:
    global _shortcuts

    if not zone:
        return None

    zone = zone.upper()

    if _shortcuts is None:
        _logger.info("Populating _shortcuts for the first time")
        _populate_shortcuts()

    if _shortcuts is not None and zone in _shortcuts:
        zone = _shortcuts[zone]

    return pytz.timezone(zone)
