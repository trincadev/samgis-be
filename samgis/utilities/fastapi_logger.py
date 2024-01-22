import loguru


def setup_logging(debug: bool = False, formatter: str = "{time} - {level} - ({extra[request_id]}) {message} "
                  ) -> loguru.logger:
    """
    Create a logging instance with log string formatter.

    Args:
        debug: logging debug argument
        formatter: log string formatter

    Returns:
        Logger

    """
    import sys

    logger = loguru.logger
    logger.remove()
    level_logger = "DEBUG" if debug else "INFO"
    logger.add(sys.stdout, format=formatter, level=level_logger)
    logger.info(f"type_logger:{type(logger)}, logger:{logger}.")
    return logger
