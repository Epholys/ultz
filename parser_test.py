import datetime as dt
import unittest

import main


class TestParseDate(unittest.TestCase):
    def assert_almost_eq(self, actual, expected, message=""):
        self.assertAlmostEqual(
            actual, expected, delta=dt.timedelta(microseconds=100), msg=message
        )

    def test_HH(self):
        HH = 19
        today = dt.date.today()
        time = dt.time(HH)
        expected = dt.datetime.combine(today, time)
        parsed = main.parse_datetime(str(HH))
        self.assert_almost_eq(parsed, expected)

    def test_HHMM(self):
        HH = 4
        MM = 6
        time_input = f"0{HH}:0{MM}"
        today = dt.date.today()
        time = dt.time(HH, MM)
        expected = dt.datetime.combine(today, time)
        parsed = main.parse_datetime(time_input)
        self.assert_almost_eq(parsed, expected)

    def test_mmdd(self):
        mm = 12
        dd = 31
        time_input = f"{mm}-{dd}"
        expected_time = dt.datetime.now().time()
        expected_date = dt.date(dt.date.today().year, mm, dd)
        expected = dt.datetime.combine(expected_date, expected_time)
        parsed = main.parse_datetime(time_input)
        self.assert_almost_eq(parsed, expected)

    def test_mmddHHmm(self):
        mm = 2
        dd = 28
        HH = 4
        MM = 6
        time_input = f"0{mm}-{dd} 0{HH}:0{MM}"
        expected = dt.datetime(dt.date.today().year, mm, dd, HH, MM)
        parsed = main.parse_datetime(time_input)
        self.assert_almost_eq(parsed, expected)

    def test_incorrect(self):
        parsed = main.parse_datetime("IO:54 ZD-LK")
        self.assertIsNone(parsed)


if __name__ == "__main__":
    unittest.main()
