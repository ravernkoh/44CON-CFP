# Contributing to 44CON-CFP

#### Contents

[Issues](#issues)

[Pull Requests](#pull-requests)

[Styleguide](#styleguide)

## Issues
When submitting an issue, please use the basic outline below. Feel free to add additional fields but you should, at a minimum, supply these fields.

* **Type:** Examples include '(Minor|Major) Bug', 'Formatting Error', 'Security Issue'
* **Description:** A comprehensive explanation of what the issue is and how it affects the application or data.
* **Investigation:** A brief overview of what might have caused the issue and how it can be reproduced.

If the bug has been flagged by our error tracking platform ([sentry.io](sentry.io)), it is likely that a sentry.io URL will be linked in the comments of the issue.

## Pull Requests
Submitting pull requests is a lot less formal. Usually pull requests are related to outstanding issues, so linking to the relevant issue in the PR description is sufficient. Otherwise a short sentence explaining the reason for the PR will be fine. However, this is reliant on good commit messages and thorough documentation in the code being submitted. The Travis-CI build for the PR will have to pass before it is accepted and, if the volume of untested code increase significantly, you may be expected to submit tests to cover the additional code.

## Styleguide
The gold standard for all code submitted is the [PEP 8 -- Style Guide for Python Code](https://www.python.org/dev/peps/pep-0008/). All code should be Python>=3.6 compliant and rely only on libraries, classes, and methods available to Django>=2.0.
