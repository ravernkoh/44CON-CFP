#!/bin/bash

set -o errexit
set -o nounset
set -o pipefail

readonly PROGNAME=$(basename "$0")
readonly PROGDIR=$(readlink -m "$(dirname "$0")")
readonly PROJECT_ROOT="$(readlink -m "$(dirname "$PROGDIR")")"
readonly ARGS="$@"

cmdline() {
    local arg=
    local args=

    for arg; do
        local delim=""
        case "$arg" in
            --settings)   args="${args}-s ";;
            --help)       args="${args}-h ";;
            --debug)      args="${args}-d ";;
            --run-tests)  args="${args}-t ";;
            *) [[ "${arg:0:1}" == "-" ]] || delim="\""
                args="${args}${delim}${arg}${delim} ";;
        esac
    done

    eval set -- "$args"

    while getopts "s:hdt" OPTION; do
        case $OPTION in
        s)
            readonly SETTINGS=${OPTARG}
            ;;
        h)
            usage
            exit 0
            ;;
        d)
            readonly DEBUG=1
            ;;
        t)
            readonly RUN_TESTS=1
            ;;
        *)
            ;;
        esac
    done

    if [[ -z ${SETTINGS+0} ]]; then
        printf "You must provide a -s/--settings value e.g. development, production etc." >&2
        exit 1
    fi
    return 0
}

prepare_env() {
    local build_dir="$PROJECT_ROOT/build"
    local custom_less_vars="$build_dir/variables.less"
    local flat_ui_dir="$PROJECT_ROOT/bower_components/flat-ui"
    local flat_ui_less="$flat_ui_dir/less/flat-ui.less"
    local css_dst="$flat_ui_dir/dist/css/flat-ui.min.css"
    local flat_ui_less_vars="$flat_ui_dir/less/variables.less"

    export DJANGO_SETTINGS_MODULE="gambit.settings.$SETTINGS"

    cd "$PROJECT_ROOT" || exit 1
    # This is just for reference because otherwise it will overwrite the config anytime this script is run
    #cp "$PROJECT_ROOT/gambit/config.example.yaml" "$PROJECT_ROOT/gambit/config.yaml"

    # Initialise db with models/changes
    python "$PROJECT_ROOT"/manage.py makemigrations gambit
    python "$PROJECT_ROOT"/manage.py migrate

    # Construct front-end assets
    if [[ ! -z ${DEBUG+0} ]]; then
        printf "\e[31;1m[?]\e[0m Install assets from bower\n" >&2
    fi
    bower install --save --production "$build_dir"/bower.json
    # If variables.less has been modified, this will update the dist copy with your own values otherwise it will use the 44CON-CFP defaults
    if [[ ! -z ${DEBUG+0} ]]; then
        printf "\e[31;1m[?]\e[0m Copying custom LESS variables to dist dir\n" >&2
    fi
    cp "$custom_less_vars" "$flat_ui_less_vars"
    lessc --source-map-less-inline --source-map-map-inline --clean-css "$flat_ui_less" "$css_dst"
    # Aggregate static resources
    if [[ ! -z ${DEBUG+0} ]]; then
        printf "\e[31;1m[?]\e[0m Collecting the static assets for Django\n" >&2
    fi
    python "$PROJECT_ROOT"/manage.py collectstatic --noinput --clear --verbosity 0
    # Apply django_compressor
    if [[ ! -z ${DEBUG+0} ]]; then
        printf "\e[31;1m[?]\e[0m Attempting to compress the various HTML, CSS, and JS front-end assets\n" >&2
    fi
    python "$PROJECT_ROOT"/manage.py compress --force --verbosity 0
}

run_tests() {
    cd "$PROJECT_ROOT" || exit 1
    if [[ ! -z ${DEBUG+0} ]]; then
        printf "\e[31;1m[?]\e[0m Running coverage tests\n"
    fi
    coverage run --source="$PROJECT_ROOT" "$PROJECT_ROOT"/manage.py test gambit
}

main() {
    cmdline "$ARGS"
    prepare_env
    if [[ ! -z ${RUN_TESTS+0} ]]; then
        run_tests
    fi
}

usage() {
    printf "usage: %s options

    OPTIONS:
    \t-s --settings\tproduction or development
    \t-h --help\tshow this help

    Examples:
    \tRun in development mode:
    \t  %s -s development\n\n" "$PROGNAME" "$PROGNAME"
}

main
