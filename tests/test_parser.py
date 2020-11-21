import datetime as dt
import unittest
import parser
from freezegun import freeze_time


class TestParseTime(unittest.TestCase):
    def test_HH(self):
        HH = 19
        expected = dt.time(HH)

        user_input = f"{HH:02}"
        parsed = parser.parse_time(user_input)
        self.assertEqual(parsed, expected)

    def test_HHMM(self):
        HH = 4
        MM = 6
        expected = dt.time(HH, MM)

        user_input = f"{HH:02}:{MM:02}"
        parsed = parser.parse_time(user_input)

        self.assertEqual(parsed, expected)

    def test_incorrect(self):
        parsed = parser.parse_time("89:9")
        self.assertIsNone(parsed)


class TestParseDate(unittest.TestCase):
    @freeze_time("2002-01-23 15:42")
    def test_mmdd(self):
        mm = 10
        dd = 12

        expected = dt.date(dt.date.today().year, mm, dd)

        user_input = f"{mm:02}-{dd:02}"
        parsed = parser.parse_date(user_input)

        self.assertEqual(parsed, expected)

    @freeze_time("1957-02-19 09:31")
    def test_iso(self):
        yyyy = 2004
        mm = 8
        dd = 15

        expected = dt.date(yyyy, mm, dd)

        user_input = f"{yyyy:04}-{mm:02}-{dd:02}"
        parsed = parser.parse_date(user_input)

        self.assertEqual(parsed, expected)

    def test_incorrect(self):
        parsed = parser.parse_date("15-19")
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
        parsed = parser.parse_datetime(user_input)

        self.assertEqual(parsed, expected)

    @freeze_time("2017-06-15 02:45")
    def test_mmdd(self):
        mm = 10
        dd = 12
        date = dt.date(dt.date.today().year, mm, dd)
        time = dt.datetime.now().time()
        expected = dt.datetime.combine(date, time)

        user_input = f"{mm:02}-{dd:02}"
        parsed = parser.parse_datetime(user_input)

        self.assertEqual(parsed, expected)

    @freeze_time("1995-02-03 10:43")
    def test_mmddHHmm(self):
        mm = 2
        dd = 28
        HH = 4
        MM = 6
        expected = dt.datetime(dt.date.today().year, mm, dd, HH, MM)

        input_time = f"{mm:02}-{dd:02} {HH:02}:{MM:02}"
        parsed = parser.parse_datetime(input_time)

        self.assertEqual(parsed, expected)

    def test_incorrect_data(self):
        parsed = parser.parse_datetime("IO:54 ZD-LK")
        self.assertIsNone(parsed)

    def test_incorrect_syntax(self):
        parsed = parser.parse_datetime("07-25 07:25 12:30")
        self.assertIsNone(parsed)
