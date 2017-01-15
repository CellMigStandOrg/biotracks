# This writes a simple configuration file with two sections
import configparser

#### TOP LEVEL INFO SECTION ########
title = 'example-cell-migration-tracking-file'
name = 'tracking-file-Essen'
author = 'paola masuzzo'
author_email = 'paola.masuzzo@ugent.be'
author_institute = 'Essen University'

#### TRACKING DATA SECTION ########
joint_identifier = 'Track N'
x_coord_field = 'X'
y_coord_field = 'Y'
time_field = 'Time Sample N'

config = configparser.ConfigParser()
config['TOP_LEVEL_INFO'] = {'title': title,
                            'name': name,
                            'author': author,
                            'author_email': author_email,
                            'author_institute': author_institute}

config['TRACKING_DATA'] = {'joint_identifier': joint_identifier,
                           'x_coord_field': x_coord_field,
                           'y_coord_field': y_coord_field,
                           'time_field': time_field}


with open('cell_track_dpkg.ini', 'w') as configfile:
    config.write(configfile)
