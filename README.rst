A datapackage representation of cell migration-derived tracking files.
******************************************************************************

This Python project aims to create a simple Python package to produce data packages of cell migration tracking files. The final goal is to have a uniform, standardized way to represent these data, as in `Frictionless Data <http://frictionlessdata.io/>`_ and `Data Packages <http://frictionlessdata.io/data-packages/>`_ .

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
  x_coord_cmso = the column name pointing to the x coordinate
  y_coord_cmso = the column name pointing to the y coordinate
  z_coord_cmso = the column name pointing to the z coordinate
  frame_cmso = the column name pointing to the frame information
  object_id_cmso = the object identifier
  link_id_cmso = the link identifier


+  **step 2** - run:

.. code-block:: python

  python dpkg.python your_tracking_file

this will create a **dp** directory containing:

+ a *csv* file for the **objects** (i.e. cells)
+ a *csv* file for the **links** (i.e. a linear collection of objects)
+ and a **dp.json** file containing the *json* schemas of the two *csv* files.


This last file will look something like this:

.. code-block:: json

  {
      "resources": [{
          "name": "objectsTable",
          "schema": {
              "primaryKey": "SPOT_ID",
              "fields": [{
                  "name": "SPOT_ID",
                  "title": "",
                  "description": "",
                  "constraints": {
                      "unique": true
                  },
                  "type": "integer",
                  "format": "default"
              }, {
                  "type": "integer",
                  "name": "FRAME",
                  "title": "",
                  "format": "default",
                  "description": ""
              }, {
                  "type": "number",
                  "name": "POSITION_X",
                  "title": "",
                  "format": "default",
                  "description": ""
              }, {
                  "type": "number",
                  "name": "POSITION_Y",
                  "title": "",
                  "format": "default",
                  "description": ""
              }]
          },
          "path": "objects.csv"
      }, {
          "name": "linksTable",
          "schema": {
              "foreignKeys": [{
                  "fields": "SPOT_ID",
                  "reference": {
                      "resource": "objectsTable",
                      "fields": "SPOT_ID",
                      "datapackage": ""
                  }
              }],
              "fields": [{
                  "type": "integer",
                  "name": "LINK_ID",
                  "title": "",
                  "format": "default",
                  "description": ""
              }, {
                  "type": "integer",
                  "name": "SPOT_ID",
                  "title": "",
                  "format": "default",
                  "description": ""
              }]
          },
          "path": "links.csv"
      }],
      "name": "CMSO_tracks",
      "title": "A CMSO data package representation of cell tracking data",
      "author_email": "paola.masuzzo@email.com",
      "author_institute": "VIB",
      "author": "paola masuzzo"
  }

Then, the datapackage is pushed to a **pandas** dataframe. At the moment, this dataframe is used to create simple visualizations of links and turning angles.
