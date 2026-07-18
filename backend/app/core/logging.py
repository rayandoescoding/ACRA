import logging
import sys


def setup_logging() -> None:
    """
    Configures standard application logging with consistent format and handlers.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
        force=True,  # Override default system logs configurations if any
    )
