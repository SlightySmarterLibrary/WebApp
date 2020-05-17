# WebApp
Web app for the Slighty Smarter Library

### Note:
We used `django-warrant` in order to do
authentication with AWS Cognito. However,
`django-warrant` is no longer maintained.

To fix this:
- We downloaded the
[latest version](https://github.com/MetaMetricsInc/django-warrant)
from Github.
 - We copied the files in the `django_warrant`
 folder to a new app folder in Django.
    ```
    python manage.py startapp djwarrant
    ```
 - Some edits in the files were made in order
to accommodate Django 2.1.1 (which is what we used
so that it works with AWS Elastic BeanStalk) 