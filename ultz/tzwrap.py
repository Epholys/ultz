""":mod:`ultz`'s wrapper around `pytz <https://pythonhosted.org/pytz/>`_"""

import os
import csv
import logging
from typing import Optional, Union, Dict, TYPE_CHECKING

import pytz


_logger = logging.getLogger(__name__)

_shorthands: Optional[Dict[str, str]] = None
"""A dictionary linking a shorthand to the full timezone.

For example, ``Paris`` could be a shorthand for ``Europe/Paris``.
"""

_shortcuts_filename = "tz-shortcuts.csv"


def _populate_shorthands() -> None:
    """Populate the ``_shorthands`` dictionary

    Read the csv file indicated by ``_shortcuts_filename`` and insert it into
    ``_shorthands``.

    If the file could not be read, logs a warning a continue.
    """
    global _shorthands
    _shorthands = {}
    try:
        curr_dir = os.path.dirname(os.path.realpath(__file__))
        file_name = _shortcuts_filename
        full_path = curr_dir + "/" + file_name
        with open(full_path) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=",")
            for row in csv_reader:
                _shorthands[row[0]] = row[1]
    except OSError:
        _logger.warning("Error while opening the data file, shortcuts inaccessible")
        pass


# Due to the limitation of ulauncher, pytz is imported as-is as a directory, so a lot of
# the features that usually work seamlessly are more difficult. For type checking, I
# manually copied the type data from typeshed, and it had some quirks that forces the
# inelegant code below that dissociate the interpreter phase from the type-checking one.
if TYPE_CHECKING:
    PyTzInfo = Union[pytz._UTCclass, pytz._StaticTzInfo, pytz._DstTzInfo]
else:
    PyTzInfo = Union[pytz.tzinfo.StaticTzInfo, pytz.tzinfo.DstTzInfo]


UnknownTimeZoneError = pytz.UnknownTimeZoneError


def timezone(
    zone: Optional[str],
) -> Optional[PyTzInfo]:
    """Return a `pytz <https://pythonhosted.org/pytz/>`_'s :py:class:`tzinfo` from a string

    This simple wrapper allow the use of shorthands defined in a separate file, whose
    filename is in ``_shorthands``. It first checks if a shorthand exists, and if so
    replace the query by the full name. Then, it simply forwards the queried timezone
    name to `pytz.timezone() <https://pythonhosted.org/pytz/>`_.

    :param zone: The queried timezone. Can be ``None``.
    :returns: The corresponding and appropriate `pytz
              <https://pythonhosted.org/pytz/>`_'s tzinfo if it exists, None otherwise.

    .. note:: `pytz <https://pythonhosted.org/pytz/>`_'s tzinfo slightly differs from
              Python's :py:class:`tzinfo`. So they are not interchangeable.
    """

    global _shorthands

    if not zone:
        return None

    # Follow the default format of pytz.
    zone = zone.upper()

    # Populate _shorthands lazily and only once.
    if _shorthands is None:
        _logger.info("Populating _shortcuts for the first time")
        _populate_shorthands()

    if _shorthands is not None and zone in _shorthands:
        zone = _shorthands[zone]

    return pytz.timezone(zone)
