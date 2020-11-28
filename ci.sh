#!/bin/bash

function main() {
    
    echocol blue "FORMAT WITH BLACK AND ISORT..."
    echocol blue "===================="
    black ultz/ tests/ main.py
    echocol blue "--------------------"
    isort ultz/ tests/
    echocol blue "...DONE."

    echo ""

    echocol green "LINTING WITH PYLINT AND BANDIT..."
    echocol green "================================="
    pylint ultz/
    echocol green "---------------------------------"
    bandit -r ultz/ tests/
    echocol green "...DONE."

    echo ""

    echocol red "LAUNCH TYPE CHECKING WITH MYPY AND TESTS WITH UNITTESTS..."
    echocol red "=========================================================="
    mypy --html-report htmlmypy --strict tests/ ultz/
    echocol red "----------------------------------------------------------"
    coverage run --branch --source=tests -m unittest discover
    echocol red "...DONE."

    echo ""

    echocol magenta "BUILD DOCUMENTATION WITH SPHINX..."
    echocol magenta "=================================="
    (cd docs && make clean coverage html)
    echocol magenta "...DONE."
}


# Little printing helper
# Note: take a look at `tput`
# RED="$(tput setaf 1 2>/dev/null || echo '')"
REDESC='\e[1;31m'
GREENESC='\e[1;32m'
YELLOWESC='\e[1;33m'
BLUEESC='\e[1;34m'
MAGENTAESC='\e[1;35m'
CYANESC='\e[1;36m'
RESETESC='\e[m'   # reset

function echocol() {
    color=$1
    shift
    local text
    local rawtext="$*"
    case $color in
	red|RED|Red)
	    text="${REDESC}${rawtext}${RESETESC}"
	    ;;
	green|GREEN|Green)
	    text="${GREENESC}${rawtext}${RESETESC}"
	    ;;
	yellow|YELLOW|Yellow)
	    text="${YELLOWESC}${rawtext}${RESETESC}"
	    ;;
	blue|BLUE|Blue)
	    text="${BLUEESC}${rawtext}${RESETESC}"
	    ;;
	magenta|MAGENTA|Magenta)
	    text="${MAGENTAESC}${rawtext}${RESETESC}"
	    ;;
	cyan|CYAN|Cyan)
	    text="${CYANESC}${rawtext}${RESETESC}"
	    ;;
    esac
    echo -e "$text"
}

main
