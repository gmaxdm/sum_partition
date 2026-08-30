import os
import yaml
import logging.config
import logging
import coloredlogs


def setup_logging(path='logger.yaml', default_level=logging.INFO):
    default_format = '%(asctime)s [%(levelname)s] %(pathname)s:%(lineno)s %(message)s'
    logging.basicConfig(level=default_level, format=default_format)
    coloredlogs.install(level=default_level)
    if os.path.exists(path):
        with open(path, 'rt') as f:
            try:
                config = yaml.safe_load(f.read())
                logging.config.dictConfig(config)
                coloredlogs.install()
            except Exception as e:
                print(e)
                print('Error in Logging Configuration. Using default configs')
    else:
        print('Failed to load configuration file. Using default configs')

