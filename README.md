# 44CON-CFP

**Author**: Aidan Mitchell <aidan@44con.com>

**Version**: 0.0.1-beta

## Setup
1. `pip install -r requirements/base.txt`
2. Update `gambit/config.yaml`
3. `python manage.py migrate`
4. `python manage.py makemigrations gambit`
5. `python manage.py migrate`
6. `bower install --save --production`
7. `cp variables.less bower_components/flat-ui/less`
8. `lessc --source-map=.\bower_components\flat-ui\dist\css\flat-ui-44con.css.map --clean-css bower_components/flat-ui/less/flat-ui.less bower_components/flat-ui/dist/css/flat-ui-44con.min.css`
