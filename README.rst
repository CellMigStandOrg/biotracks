Biotracks: a standard format for cell migration-derived tracking files
======================================================================

.. image:: https://travis-ci.org/CellMigStandOrg/biotracks.svg?branch=master
    :target: https://travis-ci.org/CellMigStandOrg/biotracks

.. image:: https://badge.fury.io/py/biotracks.svg
    :target: https://badge.fury.io/py/biotracks

Biotracks provides a standard format for cell migration tracking files and a series of converters to this format from popular tracking sofware packages. The biotracks format is a specialization of the `Frictionless Tabular Data Package <http://specs.frictionlessdata.io/tabular-data-package/>`_ .


Installation (Python 3 only)
----------------------------

.. code-block::

   python setup.py install


Usage
-----

Move to the ``scripts`` directory and run:

.. code-block:: bash

  python create_dpkg.py your_tracking_file

This will create a tabular data package directory containing:

+ a csv file for the **objects** (e.g., cells)
+ a csv file for the **links** (linear collections of objects)
+ the json descriptor file for the data package

The latter will look like this:

.. code-block:: json

  {
      "name": "cmso_tracks",
      "resources": [
          {
              "name": "objects_table",
              "path": "objects.csv",
              "schema": {
                  "fields": [
                      {
                          "constraints": {
                              "unique": true
                          },
                          "description": "",
                          "format": "default",
                          "name": "object_id_cmso",
                          "title": "",
                          "type": "integer"
                      },
                      {
                          "description": "",
                          "format": "default",
                          "name": "frame_cmso",
                          "title": "",
                          "type": "integer"
                      },
                      {
                          "description": "",
                          "format": "default",
                          "name": "x_coord_cmso",
                          "title": "",
                          "type": "number"
                      },
                      {
                          "description": "",
                          "format": "default",
                          "name": "y_coord_cmso",
                          "title": "",
                          "type": "number"
                      }
                  ],
                  "primaryKey": "object_id_cmso"
              }
          },
          {
              "name": "links_table",
              "path": "links.csv",
              "schema": {
                  "fields": [
                      {
                          "description": "",
                          "format": "default",
                          "name": "link_id_cmso",
                          "title": "",
                          "type": "integer"
                      },
                      {
                          "description": "",
                          "format": "default",
                          "name": "object_id_cmso",
                          "title": "",
                          "type": "integer"
                      }
                  ],
                  "foreignKeys": [
                      {
                          "fields": "object_id_cmso",
                          "reference": {
                              "datapackage": "",
                              "fields": "object_id_cmso",
                              "resource": "objects_table"
                          }
                      }
                  ]
              }
          }
      ]
  }

The script also creates plots of trajectories and turning angles.


Configuration
-------------

Some formats require a configuration file that specifies how to map object IDs, coordinate names, etc. This file must be in the `INI <https://en.wikipedia.org/wiki/INI_file>`_ format with two sections:

+ TOP_LEVEL_INFO: specifies a name for the data package and additional (optional) information
+ TRACKING_DATA: specifies how to map information from the source format to the biotracks column headers

You can provide a configuration file by passing it via the ``-c`` option to ``create_dpkg.py``; if this option is not set, the script will look for a ``biotracks.ini`` file in the same directory as your tracking file; if this is not found, the script will use default names for both the overall package and the column headers.

Example:

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
