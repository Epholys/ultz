# ultz

Ultz is a [Ulauncher](https://shop.fairphone.com/fr/spare-parts)'s extension for quick and easy and fast timezone conversion.

## Usage

The default launch keyword of ultz is `tz`.

The query can take 3 different forms:

- `tz timezone`: Query the current time at `timezone`.
- `tz datetime in timezone`: Query the time in `timezone`, at `datetime` here
- `tz timezone at datetime`: Query the time here, at `datetime` in `timezone`

The datetime must be one of the following format:

- (**DATE**:) `[yyyy-]mm-dd`. For example:
  - `1998-11-29` for the 29th of November 1998, right now.
  - `05-11` for the 11th of May of this year, right now.
- (**TIME**:) `HH[:MM[:SS]]`. For example: `12:03:54` for this day, at 12h03m54s.
- `DATE TIME`. For example `09-03 13:23`

The timezone must either be one of the official timezone from the [tz database](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones), or a shorthand. The shorthand are defined in the [tz-shorthands](./ultz/tz-shorthands.csv) file, and was generated so that the last part of the official timezone is enough. For example, `Paris` is a shorthand for `Europe/Paris`.

A full example would be `tz Tokyo at 15:30`, which will returns the time here, at 15:30 in Tokyo.

## Extension

You can of course change the timezone shorthand, but also add a line to [tz-shorthands](./ultz/tz-shorthands.csv) for custom shortcuts.

The format is dead-simple: each line is a shorthand, the shorthand name must be put first in ALL_CAPS, add a comma `,`, and the target timezone just after.

This file was created by:

- First getting the last part of the `/`-separated timezone
- Cleaning by:
  - Removing ambiguities (`Australia/West`, `Brazil/East`, `Brazil/West`)
  - Removing duplicates (the shorter one, if applicable, is conserved, otherwise alphabetically)
- Adding `PST` and `PDT`

## Limitations

As Ulauncher doesn't support arbitrary package requirements, the tz database backend, [pytz](https://pythonhosted.org/pytz/), is included in the repo at a fixed version. If the tz database changes, for example if a country adds or removes light-saving times, this extension must be updated. Please open an issue if it's the case!


## Development Notes

I wanted to learn more about Python, so I deliberately over-engineered the framework around this simple project with:

- Formatter: [Black](https://pypi.org/project/black/) and [isort](https://github.com/PyCQA/isort)
- Linters: [Pylint](http://pylint.pycqa.org/en/latest/) and [bandit](https://github.com/PyCQA/bandit)
- Better code: [MyPy](https://mypy.readthedocs.io/en/stable/) (type checking) and unit tests with mocking
- Documentation: [Sphinx](https://www.sphinx-doc.org/en/master/)

I also wanted to add some continuous integration with Github but dropped the case after seeing it would need even more configuration.

