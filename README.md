# 44CON-CFP

**Author**: Aidan Mitchell <aidan@44con.com>

**Version**: 0.0.1-alpha

## Setup
1. `pip install -r requirements/base.txt`
2. Enable dev settings:
    * Windows: In Powershell, `$env:DJANGO_SETTINGS_MODULE='gambit.settings.development'`
    * \*nix: `export DJANGO_SETTINGS_MODULE='gambit.settings.development'`
    * Optional: enable virtualenv `~/Envs/gambit/Scripts/activate.ps1`
3. `python manage.py migrate`
