import logging
import unittest
import unittest.mock as mock
import pytz

import ultz.tzwrap as tzwrap

TMagicMock = mock.MagicMock


class TestTzWrap(unittest.TestCase):
    def test_classic(self) -> None:
        tz: str = "Africa/Monrovia"
        self.assertEqual(tzwrap.timezone(tz), pytz.timezone(tz))

    def test_shortcut(self) -> None:
        tz: str = "Africa/Monrovia"
        shortcut: str = "Monrovia"
        self.assertEqual(tzwrap.timezone(shortcut), pytz.timezone(tz))

    def test_wrong_tz(self) -> None:
        with self.assertRaises(tzwrap.UnknownTimeZoneError):
            tzwrap.timezone("ChozoPlanet")

    def test_none(self) -> None:
        self.assertIsNone(tzwrap.timezone(None))

    @mock.patch("builtins.open", new_callable=mock.mock_open)
    @mock.patch("ultz.tzwrap._SHORTHANDS", None)  # Reset to default state
    def test_missing_file(self, mopen: TMagicMock) -> None:
        logging.disable(logging.WARNING)
        mopen.side_effect = OSError()
        with self.assertRaises(pytz.UnknownTimeZoneError):
            print(tzwrap.timezone("Dublin"))
        logging.disable(logging.NOTSET)
