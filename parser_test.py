import pytz
import datetime as dt
import unittest
import main
from freezegun import freeze_time


class TestParseTime(unittest.TestCase):
    def test_HH(self):
        HH = 19
        expected = dt.time(HH)

        user_input = f"{HH:02}"
        parsed = main.parse_time(user_input)
        self.assertEqual(parsed, expected)

    def test_HHMM(self):
        HH = 4
        MM = 6
        expected = dt.time(HH, MM)

        user_input = f"{HH:02}:{MM:02}"
        parsed = main.parse_time(user_input)

        self.assertEqual(parsed, expected)

    def test_incorrect(self):
        parsed = main.parse_time("89:9")
        self.assertIsNone(parsed)


class TestParseDate(unittest.TestCase):
    @freeze_time("2002-01-23 15:42")
    def test_mmdd(self):
        mm = 10
        dd = 12

        expected = dt.date(dt.date.today().year, mm, dd)

        user_input = f"{mm:02}-{dd:02}"
        parsed = main.parse_date(user_input)

        self.assertEqual(parsed, expected)

    def test_incorrect(self):
        parsed = main.parse_time("9-19")
        self.assertIsNone(parsed)


class TestParseDateTime(unittest.TestCase):
    @freeze_time("2005-04-23 12:23")
    def test_HHMM(self):
        HH = 14
        MM = 26
        date = dt.date.today()
        time = dt.time(HH, MM)
        expected = dt.datetime.combine(date, time)

        user_input = f"{HH:02}:{MM:02}"
        parsed = main.parse_datetime(user_input)

        self.assertEqual(parsed, expected)

    @freeze_time("2017-06-15 02:45")
    def test_mmdd(self):
        mm = 10
        dd = 12
        date = dt.date(dt.date.today().year, mm, dd)
        time = dt.datetime.now().time()
        expected = dt.datetime.combine(date, time)

        user_input = f"{mm:02}-{dd:02}"
        parsed = main.parse_datetime(user_input)

        self.assertEqual(parsed, expected)

    @freeze_time("1995-02-03 10:43")
    def test_mmddHHmm(self):
        mm = 2
        dd = 28
        HH = 4
        MM = 6
        expected = dt.datetime(dt.date.today().year, mm, dd, HH, MM)

        input_time = f"{mm:02}-{dd:02} {HH:02}:{MM:02}"
        parsed = main.parse_datetime(input_time)

        self.assertEqual(parsed, expected)

    def test_incorrect(self):
        parsed = main.parse_datetime("IO:54 ZD-LK")
        self.assertIsNone(parsed)


class TestGetDatetime(unittest.TestCase):
    @freeze_time("1998-11-02 12:23")
    def test_nodatetime(self):
        when = dt.datetime(2012, 12, 28, 5, 14)  # Ignored
        datetime = main.get_datetime(main.ExprCode.TZ_ONLY, when)
        self.assertEqual(datetime, dt.datetime.now())

    @freeze_time("1989-03-15 01:50")
    def test_date(self):
        when = dt.datetime.now()
        datetime_at = main.get_datetime(main.ExprCode.TZ_DATEAT, when)
        datetime_in = main.get_datetime(main.ExprCode.TZ_DATEIN, when)
        self.assertEqual(datetime_at, when)
        self.assertEqual(datetime_in, when)

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
    @freeze_time("2012-12-21 12:21")
    def test_reverse(self):
        tz_there = pytz.timezone("Africa/Dakar")
        datetime_here = dt.datetime.now()
        datetime_there, tz_here = main.reverse_trip(datetime_here, tz_there)
        self.assertEqual(datetime_there, tz_there.localize(datetime_here))
        self.assertIsNone(tz_here)


class TestProcessing(unittest.TestCase):
    def setUp(self):
        self.expr_err_msg = "Incorrect expression"
        self.date_err_msg = "Incorrect date"
        self.tz_err_msg = "Incorrect timezone"
        self.ok_icon = "images/icon.png"

    def assert_is_error(self, _, description, icon):
        self.assertEqual(description, "")
        self.assertEqual(icon, "")

    def test_none(self):
        result, description, icon = main.process_input(None)
        self.assert_is_error(result, description, icon)
        self.assertEqual(result, self.expr_err_msg)

    def test_empty(self):
        result, description, icon = main.process_input("")
        self.assert_is_error(result, description, icon)
        self.assertEqual(result, self.expr_err_msg)

    @freeze_time("2019")
    def test_dtin(self):
        mm = 12
        dd = 2
        HH = 12
        MM = 27
        year = dt.date.today().year
        when = dt.datetime(year, mm, dd, HH, MM)
        where = "Pacific/Chatham"
        expected_datetime = when.astimezone(pytz.timezone(where))

        expression = f"{mm:02}-{dd:02} {HH:02}:{MM:02} in {where}"
        result, description, icon = main.process_input(expression)

        self.assertEqual(result, main.format_datetime(expected_datetime))
        self.assertEqual(
            description,
            main.generate_description(main.ExprCode.TZ_DATEIN, where, when),
        )
        self.assertEqual(icon, self.ok_icon)

    @freeze_time("1975")
    def test_dtat(self):
        mm = 1
        dd = 12
        HH = 21
        MM = 17
        year = dt.date.today().year
        when = dt.datetime(year, mm, dd, HH, MM)
        where = "Europe/Madrid"
        tz = pytz.timezone(where)
        expected_datetime = tz.localize(when).astimezone(None)

        expression = f"{where} at {mm:02}-{dd:02} {HH:02}:{MM:02}"
        result, description, icon = main.process_input(expression)

        self.assertEqual(result, main.format_datetime(expected_datetime))
        self.assertEqual(
            description,
            main.generate_description(
                main.ExprCode.TZ_DATEAT, where, expected_datetime
            ),
        )

        self.assertEqual(icon, self.ok_icon)

    @freeze_time("1975-01-12 21:17")
    def test_tz(self):
        where = "Asia/Istanbul"
        result, description, icon = main.process_input(where)
        expected_datetime = dt.datetime.now().astimezone(pytz.timezone(where))
        self.assertEqual(result, main.format_datetime(expected_datetime))
        self.assertEqual(
            description,
            main.generate_description(main.ExprCode.TZ_ONLY, where, expected_datetime),
        )
        self.assertEqual(icon, self.ok_icon)

    def test_wrong_dt(self):
        expression = "25:89 in Europe/Paris"
        result, description, icon = main.process_input(expression)
        self.assertEqual(result, self.date_err_msg)
        self.assert_is_error(result, description, icon)

    def test_wrong_expr(self):
        expression = "12:29 in America/New_York at 01:12"
        result, description, icon = main.process_input(expression)
        self.assertEqual(result, self.expr_err_msg)
        self.assert_is_error(result, description, icon)


if __name__ == "__main__":
    unittest.main()
