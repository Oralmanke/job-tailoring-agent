import logging
import sys

_configured = False


def _configure_root() -> None:
    """Set up console logging once for the whole process.

    Uses a single stream handler with level names and timestamps so output can
    be filtered (INFO/WARNING/ERROR) and later redirected to a file, unlike
    bare print() calls.
    """
    global _configured
    if _configured:
        return
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)-7s %(name)s: %(message)s")
    )
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.addHandler(handler)
    _configured = True


def get_logger(name: str) -> logging.Logger:
    """Return a module-scoped logger, configuring the root logger on first use."""
    _configure_root()
    return logging.getLogger(name)
