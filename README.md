# 44CON-CFP

**Author**: Aidan Mitchell <aidan@44con.com>

**Version**: 0.1.0

## Hey, read this...
This application was designed to replace the CFP system we used for 44CON 2016 and 2017. We wanted something that fit our needs and didn't come with a lot of unnecessary cruft. As it stands, this project is very, *very* early in the development lifecycle and will undoubtedly present a number of bugs and issues if run in a production environment. If you intend to reuse this project for your own conference, I would advise going through the entire codebase manually and evaluating whether it's sufficiently mature for your purposes (there's ~4000 lines of code (as of 2018-02-05) so it's not too significant a task).

## Setup
These are extremely rudimentary instructions to build the development environment - some of which will be relevant for preparing a production environment. Previous experience with a Django project is probably necessary to troubleshoot through setup.

1. Get dependencies for Django: `pip install -r requirements/base.txt`
2. Update `gambit/config.yaml` with your own secret key, anymail settings, postgresql details, and sentry DSN. If you've got your own mail setup, alternative database deployment, or use a different error tracking solution, you will need to make the relevant changes in settings/base.py or override them in settings/YOUR-OWN-SETTINGS-FILE.py
3. Add the core database tables: `python manage.py migrate`
4. Prepare the project-specific tables: `python manage.py makemigrations gambit`
5. Commit to database: `python manage.py migrate`
6. Collect CSS and JavaScript assets: `bower install --save --production`
7. *Optional* Modify the variables.less file to change the site colour scheme: `cp variables.less bower_components/flat-ui/less`
8. *Optional (dependent on 7)* Generate minified CSS and source map: `lessc --source-map=bower_components/flat-ui/dist/css/flat-ui-44con.css.map --clean-css bower_components/flat-ui/less/flat-ui.less bower_components/flat-ui/dist/css/flat-ui-44con.min.css`
9. Copy bower assets and project assets to static directory: `python manage.py collectstatic --clear`

Steps 6 to 9 can be achieved with `bash prepare_assets.sh`. **Important:** Some database objects are currently critical for certain pages due to bad coding decisions. This will be rectified in future releases but for now, the singular FrontPage and SubmissionDeadline objects should be generated using the admin interface after creating a superuser account. When created, the admin UI will restrict from creating more objects under these models. Again, this is poor design choice and will be corrected in the future but, for the time being, avoid trying to create more of these objects. The logic of the application shouldn't really be affected if you do but shit happens and it likely will.
