import os
import yaml
import logging.config
import logging


def setup_logging(path: str ='logger.yaml', default_level: int = logging.INFO):
    default_format = '%(asctime)s [%(levelname)s] %(pathname)s:%(lineno)s %(message)s'
    logging.basicConfig(level=default_level, format=default_format)
    if os.path.exists(path):
        with open(path, 'rt') as f:
            try:
                config = yaml.safe_load(f.read())
                logging.config.dictConfig(config)
            except Exception as e:
                print(e)
                print('Error in Logging Configuration. Using default configs')
    else:
        print('Failed to load configuration file. Using default configs')

