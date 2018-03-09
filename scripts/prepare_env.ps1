param([String]$settings="development")

$VIRTUALENV_ROOT = "$($HOME)\Envs"
$VIRTUALENV_NAME = "gambit"
$ACTIVATE_VENV = "$VIRTUALENV_ROOT\$VIRTUALENV_NAME\Scripts\activate.ps1"

function Main() {
  $env:DJANGO_SETTINGS_MODULE="gambit.settings.$settings"
  & $ACTIVATE_VENV
}

Main
