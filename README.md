# 44CON-CFP

**Author**: Aidan Mitchell <aidan@44con.com>

**Version**: 0.0.1-alpha

## Setup
1. `pip install -r requirements/base.txt`
2. If developing, enable relevant settings:
  * Windows: In Powershell, `$env:DJANGO_SETTINGS_MODULE='gambit.settings.development'`
  * \*nix: `export DJANGO_SETTINGS_MODULE='gambit.settings.development'`
3. If putting into production, enable relevant settings:
  * Windows: In Powershell, `$env:DJANGO_SETTINGS_MODULE='gambit.settings.production'`
  * \*nix: `export DJANGO_SETTINGS_MODULE='gambit.settings.production'`
  * Set an appropriately secure SECRET_KEY environment variable:
    * Windows: In Powershell, `$env:DJANGO_SECRET_KEY='<64-character string>'`
    * \*nix: `export DJANGO_SECRET_KEY='<64-character string>'`
4. Optional: enable virtualenv `~/Envs/gambit/Scripts/activate.ps1`
5. `python manage.py migrate`
