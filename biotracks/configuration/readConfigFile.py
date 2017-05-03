# This reads a configuration file
import configparser


def readconfigfile(configurationFile):
    """Read a simple configuration file.

    Keyword arguments:
    configurationFile -- the file to read
    """
    config = configparser.ConfigParser()
    config.read(configurationFile)

    print('Sections of the configuration file: {}'.format(config.sections()))

    config_dict = {}
    for section in config.sections():
        config_dict[section] = {}
        for option in config.options(section):
            config_dict[section][option] = config.get(section, option)
    return config_dict
