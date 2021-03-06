import datetime as dt
import unittest

from freezegun import freeze_time

import pytz
import ultz.parser as parser
import ultz.ultz as ultz


class TestGetDatetime(unittest.TestCase):
    @freeze_time("1998-11-02 12:23")
    def test_nodatetime(self) -> None:
        when = dt.datetime(2012, 12, 28, 5, 14)  # Ignored
        datetime = ultz.get_datetime(parser.ExprCode.TZ_ONLY, when)
        self.assertEqual(datetime, dt.datetime.now())

    @freeze_time("1989-03-15 01:50")
    def test_date(self) -> None:
        when = dt.datetime.now()
        datetime_at = ultz.get_datetime(parser.ExprCode.TZ_DATEAT, when)
        datetime_in = ultz.get_datetime(parser.ExprCode.TZ_DATEIN, when)
        self.assertEqual(datetime_at, when)
        self.assertEqual(datetime_in, when)

    def test_err(self) -> None:
        when = None
        datetime_at = ultz.get_datetime(parser.ExprCode.TZ_DATEAT, when)
        datetime_in = ultz.get_datetime(parser.ExprCode.TZ_DATEIN, when)
        self.assertIsNone(datetime_at)
        self.assertIsNone(datetime_in)


class TestGetTimezone(unittest.TestCase):
    def test_none(self) -> None:
        where = None
        tz = ultz.get_tz(where)
        self.assertIsNone(tz)

    def test_real(self) -> None:
        where = "Asia/Tokyo"
        tz = ultz.get_tz(where)
        self.assertEqual(tz, pytz.timezone(where))

    def test_wrong(self) -> None:
        where = "Hyrule/Cocorico"
        tz = ultz.get_tz(where)
        self.assertIsNone(tz)


class TestReverseTrip(unittest.TestCase):
    @freeze_time("2012-12-21 12:21")
    def test_reverse(self) -> None:
        tz_there = pytz.timezone("Africa/Dakar")
        datetime_here = dt.datetime.now()
        datetime_there, tz_here = ultz.reverse_trip(datetime_here, tz_there)
        self.assertEqual(datetime_there, tz_there.localize(datetime_here))
        self.assertIsNone(tz_here)


class TestProcessing(unittest.TestCase):
    def setUp(self) -> None:
        self.ok_icon: str = "images/icon.png"

    def assert_is_error(self, _: str, description: str, icon: str) -> None:
        self.assertEqual(description, "")
        self.assertEqual(icon, "")

    def test_none(self) -> None:
        result, description, icon = ultz.process_input(None)
        self.assert_is_error(result, description, icon)
        self.assertEqual(result, ultz.get_error_msg(ultz.ErrCode.EXPR))

    def test_empty(self) -> None:
        result, description, icon = ultz.process_input("")
        self.assert_is_error(result, description, icon)
        self.assertEqual(result, ultz.get_error_msg(ultz.ErrCode.EXPR))

    @freeze_time("2019")
    def test_dtin(self) -> None:
        mm: int = 12
        dd: int = 2
        HH: int = 12
        MM: int = 27
        year = dt.date.today().year
        when = dt.datetime(year, mm, dd, HH, MM)
        where: str = "Pacific/Chatham"
        expected_datetime = when.astimezone(pytz.timezone(where))

        expression = f"{mm:02}-{dd:02} {HH:02}:{MM:02} in {where}"
        result, description, icon = ultz.process_input(expression)

        self.assertEqual(result, ultz.format_datetime(expected_datetime))
        self.assertEqual(
            description,
            ultz.generate_description(parser.ExprCode.TZ_DATEIN, where, when),
        )
        self.assertEqual(icon, self.ok_icon)

    @freeze_time("1975")
    def test_dtat(self) -> None:
        mm: int = 1
        dd: int = 12
        HH: int = 21
        MM: int = 17
        year = dt.date.today().year
        when = dt.datetime(year, mm, dd, HH, MM)
        where: str = "Europe/Madrid"
        tz = pytz.timezone(where)
        expected_datetime = tz.localize(when).astimezone(None)

        expression = f"{where} at {mm:02}-{dd:02} {HH:02}:{MM:02}"
        result, description, icon = ultz.process_input(expression)

        self.assertEqual(result, ultz.format_datetime(expected_datetime))
        self.assertEqual(
            description,
            ultz.generate_description(
                parser.ExprCode.TZ_DATEAT, where, expected_datetime
            ),
        )

        self.assertEqual(icon, self.ok_icon)

    @freeze_time("1975-01-12 21:17")
    def test_tz(self) -> None:
        where = "Asia/Istanbul"
        result, description, icon = ultz.process_input(where)
        expected_datetime = dt.datetime.now().astimezone(pytz.timezone(where))
        self.assertEqual(result, ultz.format_datetime(expected_datetime))
        self.assertEqual(
            description,
            ultz.generate_description(
                parser.ExprCode.TZ_ONLY, where, expected_datetime
            ),
        )
        self.assertEqual(icon, self.ok_icon)

    def test_wrong_dt(self) -> None:
        expression = "25:89 in Europe/Paris"
        result, description, icon = ultz.process_input(expression)
        self.assertEqual(result, ultz.get_error_msg(ultz.ErrCode.DATE))
        self.assert_is_error(result, description, icon)

    def test_wrong_expr(self) -> None:
        expression = "12:29 in America/New_York at 01:12"
        result, description, icon = ultz.process_input(expression)
        self.assertEqual(result, ultz.get_error_msg(ultz.ErrCode.EXPR))
        self.assert_is_error(result, description, icon)

    def test_wrong_tz(self) -> None:
        expression = "12:29 in YoshiLand/Island"
        result, description, icon = ultz.process_input(expression)
        self.assertEqual(result, ultz.get_error_msg(ultz.ErrCode.TZ))
        self.assert_is_error(result, description, icon)
