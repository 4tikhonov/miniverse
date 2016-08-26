
# Miniverse

This repository may be configured to directly read an existing Dataverse 4.4+ database.
This read access includes the ability to pull metrics from a Dataverse installation.  

However, the repository was initially created as a way to explore/debug/prototype.

## Functions

- In use:
  - Retrieve basic metrics via API or as visualizations
  - Map visualization of Dataverse affiliations
  - Contributions by [@jcabanas17](https://github.com/jcabanas17), [@emunn](https://github.com/emunn),
- Explore/Prototype
  - Using the Django ORM to explore the Dataverse database, create queries that are later translated to Java code
  - Store cached metadata in JSON documents.   


## Metrics set-up


### Set-up

This describes a set-up with two databases:
  1. An existing Dataverse db in Postgres and credentials to at least read the db tables
    - This Database is unmanaged.  e.g. Django does not update or attempt to update the tables.
    - With proper user credentials, you can edit records via the Django Admin--but **DON'T** do this against a production Dataverse
  2. A database for Django to create tables needed for the map and administration.  
    - This can be any relational db.  (Have used Postgres and sqlite)


### Step 1: Pip install, y'all

This assumes you have installed [pip](https://pip.pypa.io/en/stable/installing/) and [virtualenv](https://virtualenv.pypa.io/en/stable/installation/).

- Pull down the miniverse repository
- Install the requirements:

```
# Create a virtualenv
mkvirtualenv miniverse

# cd into the repo
cd miniverse

# install the basic requirements
pip install -r requirements/local.txt
```

### Step 2: Make a settings file

- Create a settings file for a two database set-up.

```
# Make your own settings file: copy "miniverse/settings/local_with_routing_template.py"
#
cp miniverse/settings/local_with_routing_template.py miniverse/settings/local_settings.py
```

- Within your new ```local_settings.py``` file, change the following values:

1. ```SECRET_KEY``` - Set a new secret key value.
  - See: https://docs.djangoproject.com/en/1.9/ref/settings/#secret-key
  - Bad, insecure, but if you must run a local version _on your laptop_: http://www.miniwebtool.com/django-secret-key-generator/
1.  ```DATABASES```
  - Set the ```default``` credentials to a new database for holding the Django/Miniverse apps
  - Set the ```dataverse``` credentials to your existing Dataverse Postgres db
1. ```SWAGGER_HOST```
  - This defaults to ```127.0.0.1:8000```.  If you are not using the Django dev server, set it to your host.  e.g. "metrics.dataverse.org"
1. ```SWAGGER_SCHEME```
  - Related to the host aboe.  Set this value to ```http``` or ```https```.  Default is ```http```
1. **Testing database**
  - If you are running the Django tests, go to (about) line 135 where it reads ```if 'test' in sys.argv or 'test_coverage' in sys.argv:```
  - Make these changes:
    - Make sure the test db is a Postgres db
    - Make sure the test db user has access to create a database and tables

### Step 3: Make your settings file load when you invoke your virtualenv

- From the top ```miniverse``` project directory, edit this file.  (Note: your virtualenv must be active.)

```
# open with vim
vim $VIRTUAL_ENV/bin/postactivate
# OR open with Atom (or open with anything else)
atom vim $VIRTUAL_ENV/bin/postactivate
```

- Add this line to the bottom of the file:  
  - ```export DJANGO_SETTINGS_MODULE=miniverse.settings.local_settings```
- The _complete_ file, including your line, should be

```
#!/bin/bash
# This hook is run after this virtualenv is activated.
export DJANGO_SETTINGS_MODULE=miniverse.settings.local_settings
```

- Save and close the file
- Type: ```source $VIRTUAL_ENV/bin/postactivate```

- Now, each time you use your virtualenv, Django will know which settings to use

### Step 4: Test your settings and run the dev server

- Type ```python manage.py check```
- If everything looks good, run these lines.  
  - If any provide errors (not warnings),
then re-examine.  
  - You will see a warning related to a "OneToOneField", that's OK

```
python manage.py migrate    # creates needed tables
python manage.py createsuperuser    # create a superuser for yourself
python manage.py collectstatic    # collect your static files
```

See if things are working.  Try this:
```
python manage.py runserver
```

Try these urls:
  - Visualization: http://127.0.0.1:8000/metrics/basic-viz
  - APIs: http://127.0.0.1:8000/static/swagger-ui/index.html

### Step 5: Run tests

If you have your **Testing Database** setting in place from Step 2,
you can run the local tests:

```python manage.py test dv_apps.metrics```

If they work, you'll see something similar to this:

```
Installing json fixture 'test_2016_0819' from '/Users/rmp553/Documents/iqss-git/miniverse/dv_apps/metrics/fixtures'.
Processed 10033 object(s).
Resetting sequences
Installed 10033 object(s) from 1 fixture(s)
Test date params
.01 - Count total dataverses: published, unpublished, all
.02 - Test published dataverse counts by month
.03 - Test unpublished dataverse counts by month
.04 - Test all dataverse counts by month
.05 - Count total datasets: published, unpublished, all
.06 - Test published dataset counts by month
.07 - Test unpublished dataset counts by month
.08 - Test all dataset counts by month
.09 - Count total files: published, unpublished, all
.10 - File downloads by month: published,
.11 - File downloads by month: unpublished,
.12 - File downloads by month: all
.13 - Content types of published files
.14 - Content types of published files
.15 - Content types of all files
.16 - Affiliations of published dataverses types
.17 - Affiliations of unpublished dataverses types
.18 - Affiliations of all dataverses types
.19 - File extensions within type
.flush fixtures

... (lots of other stuff) ...

----------------------------------------------------------------------
Ran 20 tests in 12.722s

OK
Destroying test database for alias 'default'...
```

### Step 6: Load map test database

- Load the latest fixture files.  The name will be in this format ```installations_YYYY_MMDD.json``` where YYYY_MMDD will be the date--use the latest.
- From your virtual env run:

```
python manage.py loaddata dv_apps/installations/fixtures/installations_2016_0825.json
```

- If the command above worked, try this url:
  - http://127.0.0.1:8000/map

- On Heroku, the command would be: ```heroku run python manage.py loaddata dv_apps/installations/fixtures/installations_2016_0825.json```

---

## Logo update notes

For logos (related to dv_apps.installations), we are  developing locally and then moving the logos and model references to dev/prod via github.  What does that mean?

#### Scenario 1: Logo file changed directly (on local environment)

If the logo is changed directly--not uploaded through the admin--then:

  1.  Check it into github
  2.  Push version to Heroku: ```git push heroku master```
  3.  Copy the logos to S3 (which Heroku uses for media files):
    - ```heroku run python scripts/copy_logos_to_s3.py```
    - The ```copy_logos_to_s3.py``` script above reads the AWS creds from the Heroku environment
    - If needed ```copy_logos_to_s3.py``` script may be run locally by putting the credentials in the local environ--or directly in the file (but don't check it in)

That should do it.

#### Scenario 2: Logo uploaded through local admin

In this scenario, the logo has changed, but also the references to it.  The steps are similar, but note: 1 and 5:

  1. Create new installation fixtures, naming the output file with the current date:
    ```python manage.py dumpdata installations --indent=4 > dv_apps/installations/fixtures/installations_YYYY_MM.json```
  2. Check the fixture and new image(s) into github.  (The file should have been uploaded to ```media/logos```)
  3.  Push version to Heroku: ```git push heroku master```
  4.  Copy the logos to S3 (which Heroku uses for media files):
    - ```heroku run python scripts/copy_logos_to_s3.py```
  5  Load the new fixtures on Heroku--using the name of the JSON file created in step 1:
    - ``````heroku run python manage.py loaddata dv_apps/installations/fixtures/installations_YYYY_MM.json```

---

## (end of documentation, so far)

---

### Maps Documentation

https://docs.google.com/document/d/1ThlSbw9LWtd12UzUmPxhXdlIlyCiROtBXdcIm8OGc2k/edit?usp=sharing

## Swagger API docs

The swagger UI is available through the following url:

  - http://127.0.0.1:8000/static/swagger-ui/index.html

## Restricted Django Admin - ```RestrictAdminMiddleware```

Using middleware, the Django Admin access may be restricted to addresses listed in ```settings.INTERNAL_IPS```.

When this middeware is active, users going to Django admin urls who are not coming from an IP listed in ```settings.INTERNAL_IPS``` will receive a 404 error.

- To enable this restriction:
    - In settings.MIDDLEWARE_CLASSES, add: ```dv_apps.admin_restrict.middleware.RestrictAdminMiddleware```
    - Example for ```settings.local_settings``` which is importing from ```settings.base```:

```python
MIDDLEWARE_CLASSES += [
    # Restrict by IP address
    'dv_apps.admin_restrict.middleware.RestrictAdminMiddleware',
]
```

- To add acceptable addresses to ```settings.INTERNAL_IPS```
    - You can add full addresses.  e.g. 211.247.10.10
        - e.g., ```INTERNAL_IPS = ('211.247.10.10',)```
    - You can add the 1st two segments of the address:
        - e.g., ```INTERNAL_IPS = ('140.247', '211.247.10.10',)```
    - You can add the 1st three segments of the address:
        - e.g., ```INTERNAL_IPS = ('140.247.10', '211.247.10.10',)```
    - For running django's test server, the default is:
        - e.g., ```INTERNAL_IPS = ('127.0.0.1',)```

  - Dev note: The code for ```RestrictAdminMiddleware``` is in ```dv_apps/middeware.py```

---


# Load Heroku markers

## Preload to S3.  

- Can use boto script in:

```
heroku run python scripts/copy_logos_to_s3.py
```

- Add creds to script and run

## Load fixtures

Load the latest fixture files.  The name will be in this format ```installations_YYYY_MMDD.json``` where YYYY_MMDD will be the date--use the latest.

  - ```heroku run python manage.py loaddata dv_apps/installations/fixtures/installations_2016_0826.json```
