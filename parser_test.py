import datetime as dt
import unittest

import main


class TestParseDate(unittest.TestCase):
    def assert_almost_eq(self, actual, expected):
        self.assertAlmostEqual(actual, expected, delta=dt.timedelta(microseconds=100))

    def test_now(self):
        now = dt.datetime.now()
        parsed, code = main.parse_date("now")
        self.assertTrue(code)
        self.assert_almost_eq(parsed, now)

    def test_HH(self):
        HH = 19
        today = dt.date.today()
        time = dt.time(HH)
        expected = dt.datetime.combine(today, time)
        parsed, code = main.parse_date(str(HH))
        self.assertTrue(code)
        self.assert_almost_eq(parsed, expected)

    def test_HHMM(self):
        HH = 4
        MM = 6
        time_input = f"0{HH}:0{MM}"
        today = dt.date.today()
        time = dt.time(HH, MM)
        expected = dt.datetime.combine(today, time)
        parsed, code = main.parse_date(time_input)
        self.assertTrue(code)
        self.assert_almost_eq(parsed, expected)

    def test_YYmmdd(self):
        YY = 2020
        mm = 2
        dd = 13
        time_input = f"{YY}-0{mm}-{dd}"
        expected = dt.datetime(YY, mm, dd)
        parsed, code = main.parse_date(time_input)
        self.assertTrue(code)
        self.assert_almost_eq(parsed, expected)

    def test_YYmmddHHmm(self):
        YY = 2020
        mm = 2
        dd = 13
        HH = 4
        MM = 6
        time_input = f"{YY}-0{mm}-{dd} 0{HH}:0{MM}"
        expected = dt.datetime(YY, mm, dd, HH, MM)
        parsed, code = main.parse_date(time_input)
        self.assertTrue(code)
        self.assert_almost_eq(parsed, expected)

    def test_incorrect(self):
        parsed, code = main.parse_date("IO:54_ZD-LK")
        self.assertFalse(code)
        self.assertIsNone(parsed)


if __name__ == "__main__":
    unittest.main()
