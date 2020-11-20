import unittest
import pytz
import tzwrap


class TestTzWrap(unittest.TestCase):
    def test_classic(self):
        tz = "Africa/Monrovia"
        self.assertEqual(tzwrap.timezone(tz), pytz.timezone(tz))

    def test_shortcut(self):
        tz = "Africa/Monrovia"
        shortcut = "Monrovia"
        self.assertEqual(tzwrap.timezone(shortcut), pytz.timezone(tz))

    def test_wrong(self):
        with self.assertRaises(tzwrap.UnknownTimeZoneError):
            tzwrap.timezone("ChozoPlanet")

    def test_none(self):
        self.assertIsNone(tzwrap.timezone(None))
