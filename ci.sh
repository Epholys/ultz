#!/bin/bash
coverage run --branch --source=tests -m unittest discover
mypy --html-report htmlmypy --strict tests/ ultz/
bandit -r ultz/ tests/
