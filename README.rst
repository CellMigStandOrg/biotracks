Biotracks: a standard format for cell migration-derived tracking files
======================================================================

.. image:: https://travis-ci.org/CellMigStandOrg/biotracks.svg?branch=master
    :target: https://travis-ci.org/CellMigStandOrg/biotracks

.. image:: https://badge.fury.io/py/biotracks.svg
    :target: https://badge.fury.io/py/biotracks

Biotracks provides a standard format for cell migration tracking files and a series of converters from popular tracking sofware packages to the biotracks format, which is a specialization of the `Frictionless Tabular Data Package <http://specs.frictionlessdata.io/tabular-data-package/>`_ .


Installation from sources (Python 3 only)
-----------------------------------------

.. code-block::

   python setup.py install

Installation from PiPy
----------------------

.. code-block::

    pip install biotracks

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
              "name": "cmso_objects_table",
              "path": "objects.csv",
              "schema": {
                  "fields": [
                      {
                          "constraints": {
                              "unique": true
                          },
                          "description": "",
                          "format": "default",
                          "name": "cmso_object_id",
                          "title": "",
                          "type": "integer"
                      },
                      {
                          "description": "",
                          "format": "default",
                          "name": "cmso_frame_id",
                          "title": "",
                          "type": "integer"
                      },
                      {
                          "description": "",
                          "format": "default",
                          "name": "cmso_x_coord",
                          "title": "",
                          "type": "number"
                      },
                      {
                          "description": "",
                          "format": "default",
                          "name": "cmso_y_coord",
                          "title": "",
                          "type": "number"
                      }
                  ],
                  "primaryKey": "cmso_object_id"
              }
          },
          {
              "name": "cmso_links_table",
              "path": "links.csv",
              "schema": {
                  "fields": [
                      {
                          "description": "",
                          "format": "default",
                          "name": "cmso_link_id",
                          "title": "",
                          "type": "integer"
                      },
                      {
                          "description": "",
                          "format": "default",
                          "name": "cmso_object_id",
                          "title": "",
                          "type": "integer"
                      }
                  ],
                  "foreignKeys": [
                      {
                          "fields": "cmso_object_id",
                          "reference": {
                              "datapackage": "",
                              "fields": "cmso_object_id",
                              "resource": "cmso_objects_table"
                          }
                      }
                  ]
              }
          }
      ]
  }


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
  cmso_x_coord = the column name pointing to the x coordinate
  cmso_y_coord = the column name pointing to the y coordinate
  cmso_z_coord = the column name pointing to the z coordinate
  cmso_frame_id = the column name pointing to the frame information
  cmso_object_id = the object identifier
  cmso_link_id = the link identifier
  
  
  Examples
  --------
  
  `CELLMIA <https://github.com/CellMigStandOrg/biotracks/tree/master/examples/CELLMIA>`_ .
  `CellProfiler <https://github.com/CellMigStandOrg/biotracks/tree/master/examples/CellProfiler>`_ .
  `ICY <https://github.com/CellMigStandOrg/biotracks/tree/master/examples/ICY>`_ .
  `Mosaic <https://github.com/CellMigStandOrg/biotracks/tree/master/examples/Mosaic>`_ .
  `TrackMate <https://github.com/CellMigStandOrg/biotracks/tree/master/examples/TrackMate>`_ .
  
