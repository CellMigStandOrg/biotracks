A datapackage representation of cell migration-derived tracking files.
******************************************************************************

This Python project aims to create a simple Python package to produce data packages of cell migration tracking files. The final goal is to have a uniform, standardized way to represent these data, as in: http://frictionlessdata.io/ and http://frictionlessdata.io/data-packages/.

Steps to follow to use the package:

+ **step 1** - modify the parameters in the file *writeConfigFile.py*, go to the directory containing your tracking file and run:

.. code-block:: python

  python writeConfigFile.py

this will create the *.ini configuration file*

This file should look something like this:

.. code-block::

  [TOP_LEVEL_INFO]
  author = the author of the dp
  title = a title describing the dp
  name = a name for the dp
  author_institute = the insitute of the author
  author_email = a valid email address

  [TRACKING_DATA]
  x_coord_field = the field pointing to the x coordinate
  y_coord_field = the field pointing to the y coordinate
  time_field = the field pointing to the time information
  joint_identifier = the track identifier joining objects and events


+  **step 2** - run:

.. code-block:: python

  python dpkg.python your_tracking_file

this will create a **dp** directory containing:

+ a *.csv* file for the **objects** (cells)
+ a *.csv* file for the **events** (tracks)
+ and finally a **dp.json** file containing the schemas of the two.


This last file will look something like this:

.. code-block:: json

    {
          "author_institute": "Essen University",
          "author_email": "paola.masuzzo@ugent.be",
          "author": "paola masuzzo",
          "resources": [{
              "schema": {
                  "fields": [{
                      "name": "Track N",
                      "type": "integer",
                      "title": "",
                      "format": "default",
                      "description": "",
                      "constraints": {
                          "unique": true
                      }
                  }, {
                      "type": "integer",
                      "format": "default",
                      "description": "",
                      "name": "events_size",
                      "title": ""
                  }],
                  "primaryKey": "Track N"
              },
              "name": "eventsTable",
              "path": "events.csv"
          }, {
              "schema": {
                  "fields": [{
                      "type": "integer",
                      "format": "default",
                      "description": "",
                      "name": "index",
                      "title": ""
                  }, {
                      "type": "integer",
                      "format": "default",
                      "description": "",
                      "name": "Line",
                      "title": ""
                  }, {
                      "type": "integer",
                      "format": "default",
                      "description": "",
                      "name": "Track N",
                      "title": ""
                  }, {
                      "type": "integer",
                      "format": "default",
                      "description": "",
                      "name": "Time Sample N",
                      "title": ""
                  }, {
                      "type": "integer",
                      "format": "default",
                      "description": "",
                      "name": "X",
                      "title": ""
                  }, {
                      "type": "integer",
                      "format": "default",
                      "description": "",
                      "name": "Y",
                      "title": ""
                  }],
                  "foreignKeys": [{
                      "reference": {
                          "resource": "eventsTable",
                          "datapackage": "",
                          "fields": "Track N"
                      },
                      "fields": "Track N"
                  }]
              },
              "name": "objectsTable",
              "path": "objects.csv"
          }],
          "title": "example-cell-migration-tracking-file",
          "name": "tracking-file-Essen"
      }


Then, the datapackage is pushed to a **pandas** dataframe. At the moment, this dataframe is used to creates simple visualizations of tracks and turning angles.
