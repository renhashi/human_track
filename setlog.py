from logging import getLogger, StreamHandler, DEBUG, FileHandler, Formatter

#LOG setting
def set_logfile():
    logger = getLogger(__name__)
    handler = StreamHandler()
    handler.setLevel(DEBUG)
    logger.setLevel(DEBUG)
    logger.addHandler(handler)
    fh = FileHandler('./system.log')
    logger.addHandler(fh)
    logger.propagate = False
    formatter = Formatter('%(asctime)s:%(lineno)d:%(levelname)s:%(message)s')
    fh.setFormatter(formatter)
    handler.setFormatter(formatter)

    return logger