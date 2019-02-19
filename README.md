# 44CON-CFP

[![Requirements Status](https://requires.io/github/rawhex/44CON-CFP/requirements.svg?branch=master)](https://requires.io/github/rawhex/44CON-CFP/requirements/?branch=master) [![Coverage Status](https://coveralls.io/repos/github/rawhex/44CON-CFP/badge.svg?branch=master)](https://coveralls.io/github/rawhex/44CON-CFP?branch=master) [![Build Status](https://travis-ci.org/rawhex/44CON-CFP.svg?branch=master)](https://travis-ci.org/rawhex/44CON-CFP) [![Application Version](https://img.shields.io/badge/version-0.1.1-orange.svg)](https://github.com/rawhex/44CON-CFP) ![Supported versions of Python](https://img.shields.io/badge/Python-3.6.8-blue.svg) ![Supported versions of Django](https://img.shields.io/badge/Django-2.1.7-green.svg) [![License](https://img.shields.io/badge/license-GPLv3-yellow.svg)](https://github.com/nimxj/44CON-CFP/blob/master/LICENSE)

## Hey, read this...

This application was designed to replace the CFP system we used for 44CON 2016 and 2017. We wanted something that fit our needs and didn't come with a lot of unnecessary cruft. As it stands, this project is very, *very* early in the development lifecycle and will undoubtedly present a number of bugs and issues if run in a production environment. If you intend to reuse this project for your own conference, I would advise going through the entire codebase manually and evaluating whether it's sufficiently mature for your purposes (there's ~6k-8k lines of code that matter (as of 2019) so it's not too significant a task).

As of February 2019, this application is going through a phase of upgrades to make the codebase significantly more mature. The entire MVC is being overhauled to integrate [DRF](https://www.django-rest-framework.org/) in order to reduce the amount of per-request processing that is being done by the views. This will massively improve the performance across the application but specifically on the heaviest section of the site - the submissions listing page. There should be very few changes as far as functionality goes and the hope is for this migration to be relatively seamless. It will then enable the development of the non-MVP modules that have been discussed by the 44CON team e.g. mailing function, interactive forms, programme committee management, CRM-style controls for front page. 

## Dependencies

Building, running, and maintaining this project requires at-minimum the following software. The Python dependencies are available in `requirements/base.txt`.

### Project-wide

* Python 3.6+
* postgresql

### Build process

* npm/nodejs
    * less
    * less-plugin-clean-css
    * bower

## Setup

These are extremely rudimentary instructions to build the development environment - some of which will be relevant for preparing a production environment. Previous experience with a Django project is probably necessary to troubleshoot through setup.

1. Get dependencies for Django: `pip install -r requirements/base.txt`
2. Copy `gambit/config.example.yaml` to `gambit/config.yaml` and update it with your own secret key, anymail settings, postgresql details, and sentry DSN. If you've got your own mail setup, alternative database deployment, or use a different error tracking solution, you will need to make the relevant changes in settings/base.py or override them in settings/YOUR-OWN-SETTINGS-FILE.py
3. Prepare the project-specific tables: `python manage.py makemigrations gambit`
4. Initialise the database by adding the core database tables and integrating migrations: `python manage.py migrate`
6. Collect CSS and JavaScript assets: `bower install --save --production build/bower.json`
7. *Optional* Modify the variables.less file to change the site colour scheme: `cp build/variables.less bower_components/flat-ui/less`
8. *Optional (dependent on 7)* Generate minified CSS and source map: `lessc --source-map-less-inline --source-map-map-inline --clean-css bower_components/flat-ui/less/flat-ui.less bower_components/flat-ui/dist/css/flat-ui.min.css`
9. Copy bower assets and project assets to static directory: `python manage.py collectstatic --clear`
10. Compress JS/CSS assets: `python manage.py compress`

Steps 3 to 10 can be achieved using `build/build.sh`. It requires a `-s` option with a single argument referencing the settings file which should be used e.g. *development* or *production*. Usage can be displayed with `-h`. You can also supply `-t` to run coverage tests which is useful to ensure the environment has setup correctly.

## Usage

Some database objects are currently critical for certain pages due to bad coding decisions. This will be rectified in future releases but for now, the singular FrontPage and SubmissionDeadline objects should be generated using the admin interface after creating a superuser account. When created, the admin UI will restrict from creating more objects under these models. Again, this is poor design choice and will be corrected in the future but, for the time being, avoid trying to create more of these objects. The logic of the application shouldn't really be affected if you do but shit happens and it likely will.

## Contribute

Yes, absolutely. Contributions to the project are very welcome. This project is entirely open source and hopefully will eventually become a stable option for conferences looking for a modular, modifiable, and simple CFP. For more information on contributing, please read our [Contribution](https://github.com/rawhex/44CON-CFP/blob/master/CONTRIBUTING.md) doc.

## License

[GPLv3](https://github.com/rawhex/44CON-CFP/blob/master/LICENSE) (c) 2017-2019 Sense/Net Ltd.
