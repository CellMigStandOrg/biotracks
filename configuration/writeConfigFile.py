import configparser

config = configparser.ConfigParser()
config['TOP_LEVEL_INFO'] = {'title': 'cell-migration-tracking-file',
                            'name': 'tracking-file',
                            'author': 'paola masuzzo',
                            'author_email': 'paola.masuzzo@ugent.be'}

config['TRACKING_DATA'] = {'joint_identifier': 'Track N',
                           'x_coord_field': 'X',
                           'y_coord_field': 'Y',
                           'time_field': 'Time Sample N'}


with open('cell_track_dpkg.ini', 'w') as configfile:
    config.write(configfile)
