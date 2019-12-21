#!/bin/bash

# build.sh
# pseudo-idempotent automated build process for gambit
# will:
#   * apply new migrations
#   * collect new/modified static files
#   * pull down remote (bower) packages
#   * compile less components
#   * compress any relevant assets
#   * attempt to create an admin user using env vars
# wont:
#   * call your mother for you
#   * fix your poor code

set -o errexit
set -o nounset
set -o pipefail

readonly PROGNAME=$(basename "$0")
readonly PROGDIR=$(dirname "$0")
readonly PROJECT_ROOT="$(dirname "$PROGDIR")"
readonly ARGS=( "$@" )

usage() {
    printf "usage: %s options
    By default this script will just collect any static assets and compile them as appropriate.
    Apply flags as necessary.

    REQUIRED FLAGS:
        -s --settings           production or development

    OPTIONAL FLAGS:
        -p --prep-database      process and apply migrations
        -a --create-admin       create administrative account from env vars DJANGO_ADMIN_USERNAME and DJANGO_ADMIN_PASSWORD (requires -p)
        -c --collect-packages   pull down packages in bower.json
        -l --compile-less       generate flat-ui CSS from variable.less
        -d --debug              show verbose output on commands
        -t --run-tests          execute coverage
        -h --help               show this help

    Examples:
        Run in development mode with verbose command output:
          %s -s development -d
        Run in production mode and create administrative user:
          DJANGO_ADMIN_USERNAME=\"admin\" DJANGO_ADMIN_PASSWORD=\"password\" %s -s production\n\n" "$PROGNAME" "$PROGNAME" "$PROGNAME"
}

cmdline() {
    local arg=
    local args=

    for arg; do
        local delim=""
        case "$arg" in
            --settings)          args="${args}-s ";;
            --prep-database)     args="${args}-p ";;
            --create-admin)      args="${args}-a ";;
            --collect-packages)  args="${args}-c ";;
            --compile-less)      args="${args}-l ";;
            --help)              args="${args}-h ";;
            --debug)             args="${args}-d ";;
            --run-tests)         args="${args}-t ";;
            *) [[ "${arg:0:1}" == "-" ]] || delim="\""
                args="${args}${delim}${arg}${delim} ";;
        esac
    done

    eval set -- "$args"

    while getopts "s:paclhdt" OPTION; do
        case $OPTION in
        s)
            readonly SETTINGS=${OPTARG}
            ;;
        p)
            readonly PREP_DATABASE=1
            ;;
        a)
            readonly CREATE_ADMIN=1
            ;;
        c)
            readonly PULL_BOWER=1
            ;;
        l)
            readonly COMPILE_LESS=1
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

    if [[ -z ${ARGS[@]+0} ]]; then
        usage
        exit 0
    fi
    if [[ -z ${SETTINGS+0} ]]; then
        printf "You must provide a -s/--settings value e.g. development, production etc.\n" >&2
        exit 1
    fi
    if [[ -n ${CREATE_ADMIN+0} ]]; then
        if [[ -z ${PREP_DATABASE+0} ]]; then
            printf "Must prep database to create admin (-a requires -p).\n"
            exit 1
        fi
        if [[ -z ${DJANGO_ADMIN_USERNAME+0} ]] || [[ -z ${DJANGO_ADMIN_PASSWORD+0} ]]; then
            printf "You must set the DJANGO_ADMIN_USERNAME and DJANGO_ADMIN_PASSWORD environment variables.\n"
            printf "e.g. export DJANGO_ADMIN_USERNAME=\"admin\"\n"
            exit 1
        fi
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
    local gambit_dir="$PROJECT_ROOT"

    export DJANGO_SETTINGS_MODULE="gambit.settings.$SETTINGS"

    cd "$gambit_dir" || exit 1
    # This is just for reference because otherwise it will overwrite the config anytime this script is run
    #cp "$PROJECT_ROOT/gambit/config.example.yaml" "$PROJECT_ROOT/scaffold/config.yaml"

    # If -j, don't bother with all the other fuss
    # TODO: This should be split between the DB related stuff and the remote asset collection
    if [[ -n ${PREP_DATABASE+0} ]]; then
        # Initialise db with models/changes
        python3 "$gambit_dir"/manage.py makemigrations gambit
        python3 "$gambit_dir"/manage.py migrate

        # Create a super user account using env vars
        if [[ -n ${DEBUG+0} ]]; then
            printf "\e[31;1m[?]\e[0m Adding admin account if it doesn't exist; username: \"%s\" password: \"%s\"\n" "$DJANGO_ADMIN_USERNAME" "$DJANGO_ADMIN_PASSWORD" >&2
        fi
        if [[ -n ${CREATE_ADMIN+0} ]]; then
            su_script="from django.contrib.auth.models import User;
username = '$DJANGO_ADMIN_USERNAME';
password = '$DJANGO_ADMIN_PASSWORD';
email = 'null@example.com';

if User.objects.filter(username=username).count()==0:
    User.objects.create_superuser(username, email, password);
else:
    pass"
            printf "%s" "$su_script" | python3 "$gambit_dir"/manage.py shell
        fi
    fi
    if [[ -n ${PULL_BOWER+0} ]]; then
        # Construct front-end assets
        if [[ -n ${DEBUG+0} ]]; then
            printf "\e[31;1m[?]\e[0m Install assets from bower\n" >&2
        fi
        bower install --allow-root --save --production "$build_dir"/bower.json
    fi
    if [[ -n ${COMPILE_LESS+0} ]]; then
        # If variables.less has been modified, this will update the dist copy with your own values otherwise it will use the 44CON-CFP defaults
        if [[ -n ${DEBUG+0} ]]; then
            printf "\e[31;1m[?]\e[0m Copying custom LESS variables to dist dir\n" >&2
        fi
        cp "$custom_less_vars" "$flat_ui_less_vars"
        lessc --source-map-less-inline --source-map-map-inline --clean-css "$flat_ui_less" "$css_dst"
    fi

    # Aggregate static resources
    if [[ -n ${DEBUG+0} ]]; then
        printf "\e[31;1m[?]\e[0m Collecting the static assets for Django\n" >&2
    fi
    python3 "$gambit_dir"/manage.py collectstatic --noinput --clear --verbosity 0
    # Apply django_compressor
    if [[ -n ${DEBUG+0} ]]; then
        printf "\e[31;1m[?]\e[0m Attempting to compress the various HTML, CSS, and JS front-end assets\n" >&2
    fi
    python3 "$gambit_dir"/manage.py compress --force --verbosity 0
}

run_tests() {
    cd "$gambit_dir" || exit 1
    if [[ -n ${DEBUG+0} ]]; then
        printf "\e[31;1m[?]\e[0m Running coverage tests\n"
    fi
    coverage run --source="$gambit_dir" "$gambit_dir"/manage.py test gambit
}

main() {
    cmdline "${ARGS[@]}"
    prepare_env
    if [[ -n ${RUN_TESTS+0} ]]; then
        run_tests
    fi
}

main
