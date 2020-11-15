import datetime as dt
import unittest

import main


def _assert_dt_almost_eq(actual, expected, message=""):
    unittest.TestCase().assertAlmostEqual(
        actual, expected, delta=dt.timedelta(microseconds=100), msg=message
    )


class TestParseTime(unittest.TestCase):
    def test_HH(self):
        HH = 19
        expected = dt.time(HH)

        user_input = f"{HH:02}"
        parsed = main.parse_time(user_input)
        _assert_dt_almost_eq(parsed, expected)

    def test_HHMM(self):
        HH = 4
        MM = 6
        expected = dt.time(HH, MM)

        user_input = f"{HH:02}:{MM:02}"
        parsed = main.parse_time(user_input)
        _assert_dt_almost_eq(parsed, expected)

    def test_incorrect(self):
        parsed = main.parse_time("89:9")
        self.assertIsNone(parsed)


class TestParseDate(unittest.TestCase):
    def test_mmdd(self):
        mm = 10
        dd = 12
        expected = dt.date(dt.date.today().year, mm, dd)

        user_input = f"{mm:02}-{dd:02}"
        parsed = main.parse_date(user_input)
        _assert_dt_almost_eq(parsed, expected)

    def test_incorrect(self):
        parsed = main.parse_time("9-19")
        self.assertIsNone(parsed)


class TestParseDateTime(unittest.TestCase):
    def test_HHMM(self):
        HH = 14
        MM = 26
        date = dt.date.today()
        time = dt.time(HH, MM)
        expected = dt.datetime.combine(date, time)

        user_input = f"{HH:02}:{MM:02}"
        parsed = main.parse_datetime(user_input)
        _assert_dt_almost_eq(parsed, expected)

    def test_mmdd(self):
        mm = 10
        dd = 12
        date = dt.date(dt.date.today().year, mm, dd)
        time = dt.datetime.now().time()
        expected = dt.datetime.combine(date, time)

        user_input = f"{mm:02}-{dd:02}"
        parsed = main.parse_datetime(user_input)
        _assert_dt_almost_eq(parsed, expected)

    def test_mmddHHmm(self):
        mm = 2
        dd = 28
        HH = 4
        MM = 6
        expected = dt.datetime(dt.date.today().year, mm, dd, HH, MM)

        input_time = f"{mm:02}-{dd:02} {HH:02}:{MM:02}"
        parsed = main.parse_datetime(input_time)
        _assert_dt_almost_eq(parsed, expected)

    def test_incorrect(self):
        parsed = main.parse_datetime("IO:54 ZD-LK")
        self.assertIsNone(parsed)


if __name__ == "__main__":
    unittest.main()
