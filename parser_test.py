import pytz
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


class TestGetDatetime(unittest.TestCase):
    def test_nodatetime(self):
        when = dt.datetime(1998, 11, 2, 12, 23)
        datetime = main.get_datetime(main.ExprCode.TZ_ONLY, when)
        _assert_dt_almost_eq(datetime, dt.datetime.now())

    def test_date(self):
        when = dt.datetime(1989, 3, 15, 1, 50)
        datetime_at = main.get_datetime(main.ExprCode.TZ_DATEAT, when)
        datetime_in = main.get_datetime(main.ExprCode.TZ_DATEIN, when)
        _assert_dt_almost_eq(datetime_at, when)
        _assert_dt_almost_eq(datetime_in, when)

    def test_err(self):
        when = None
        datetime_at = main.get_datetime(main.ExprCode.TZ_DATEAT, when)
        datetime_in = main.get_datetime(main.ExprCode.TZ_DATEIN, when)
        self.assertIsNone(datetime_at)
        self.assertIsNone(datetime_in)


class TestGetTimezone(unittest.TestCase):
    def test_none(self):
        where = None
        tz = main.get_tz(where)
        self.assertIsNone(tz)

    def test_real(self):
        where = "Asia/Tokyo"
        tz = main.get_tz(where)
        self.assertEqual(tz, pytz.timezone(where))

    def test_wrong(self):
        where = "Hyrule/Cocorico"
        tz = main.get_tz(where)
        self.assertIsNone(tz)


class TestReverseTrip(unittest.TestCase):
    def test_reverse(self):
        tz_there = pytz.timezone("Africa/Dakar")
        datetime_here = dt.datetime(2012, 12, 21, 12, 21)
        datetime_there, tz_here = main.reverse_trip(datetime_here, tz_there)
        self.assertEqual(datetime_there, tz_there.localize(datetime_here))
        self.assertIsNone(tz_here)


if __name__ == "__main__":
    unittest.main()
