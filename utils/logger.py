import logging


def setup_logging(app) -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter(
            '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
        )
    )
    handler.setLevel(logging.INFO)
    app.logger.setLevel(logging.INFO)
    if not app.logger.handlers:
        app.logger.addHandler(handler)
    app.logger.propagate = False


def get_logger(name: str = __name__) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter('[%(asctime)s] %(levelname)s in %(module)s: %(message)s')
        )
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger
