# This reads a configuration file
import configparser
global config_file
config_file = r'C:\Users\paola\Desktop\cell_track_dpkg.ini'


def readconfigfile(config_file):
    """Read a simple configuration file.

    Keyword arguments:
    config_file -- the file to read
    """
    config = configparser.ConfigParser()
    config.read(config_file)
    print('Sections of the config file: {}'.format(config.sections()))

    config_dict = {}
    for section in config.sections():
        config_dict[section] = {}
        for option in config.options(section):
            config_dict[section][option] = config.get(section, option)
    return config_dict
