from __future__ import annotations

import logging

from mcp_trace.config import get_settings
from mcp_trace.database import init_db
from mcp_trace.server import mcp, set_run_store
from mcp_trace.storage.run_store import RunStore

logger = logging.getLogger(__name__)


def configure_logging(log_level: str) -> None:
    level = getattr(logging, log_level.upper(), logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


def main() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)
    init_db(settings)
    set_run_store(RunStore())

    import mcp_trace.tools  # noqa: F401

    logger.info("Starting mcp-trace")
    logger.info("DB: %s", settings.db_url)
    mcp.run()


if __name__ == "__main__":
    main()
