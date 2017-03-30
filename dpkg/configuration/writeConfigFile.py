# This writes a simple configuration file with two sections
import configparser

#### TOP LEVEL INFO SECTION ########
title = 'example-cell-migration-tracking-file'
name = 'tracking-file-track_mate'
author = 'paola masuzzo'
author_email = 'paola.masuzzo@ugent.be'
author_institute = 'VIB'

#### TRACKING DATA SECTION ########
x = 'yourX'
y = 'yourY'
z = 'yourZ'
frame = 'yourFrame'
object_id = 'yourObjectID'
link_id = 'yourLinkID'

config = configparser.ConfigParser()
config['TOP_LEVEL_INFO'] = {'title': title,
                            'name': name,
                            'author': author,
                            'author_email': author_email,
                            'author_institute': author_institute}

config['TRACKING_DATA'] = {'x_coord_cmso': x,
                           'y_coord_cmso': y,
                           'z_coord_cmso': z,
                           'frame_cmso': frame,
                           'object_id_cmso': object_id,
                           'link_id_cmso': link_id}


with open('cell_track_dpkg.ini', 'w') as configfile:
    config.write(configfile)
