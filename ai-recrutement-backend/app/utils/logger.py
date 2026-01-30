from loguru import logger
import sys
import logging


def setup_logging() -> None:
    logger.remove()
    logger.add(
        sys.stdout,
        level="INFO",
        backtrace=False,
        diagnose=False,
        enqueue=True,
        )
    # Redirige le logging standard Python vers Loguru
    class InterceptHandler(logging.Handler):
        def emit(self, record):
            # Récupère le niveau de log
            level = logger.level(record.levelname).name if record.levelname in logger._core.levels else record.levelno
            logger.opt(depth=6, exception=record.exc_info).log(level, record.getMessage())
    logging.basicConfig(handlers=[InterceptHandler()], level=0)
    logging.getLogger().handlers = [InterceptHandler()]
