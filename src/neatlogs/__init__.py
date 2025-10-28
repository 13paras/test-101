"""
Neatlogs - LLM Call Tracking Library
==========================================

A comprehensive LLM tracking system.
Automatically captures and logs all LLM API calls with detailed metrics.
"""

from .core import get_tracker, LLMTracker
from .instrumentation.manager import setup_import_monitor
import logging
import atexit
import threading
import os
from typing import List, Optional

__version__ = "1.1.7"
__all__ = ['init', 'get_tracker', 'add_tags', 'get_langchain_callback_handler']

# --- Global Tracker Instance and Initialization ---

_global_tracker: Optional[LLMTracker] = None
_init_lock = threading.Lock()


def init(
    api_key: str,
    tags: Optional[List[str]] = None,
    debug: bool = False,
    log_level: Optional[str] = None
):
    """
    Initialize the Neatlogs tracking system.


    Args:
        api_key (str): API key for the session. Will be persisted and logged.
        tags (List[str], optional): List of tags to associate with the tracking session.
        debug (bool): Enable debug logging. Defaults to False.
        log_level (str, optional): Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
                                   Can also be set via NEATLOGS_LOG_LEVEL environment variable.
                                   If not specified, defaults to INFO or DEBUG if debug=True.

    Returns:
        LLMTracker: The initialized tracker instance.

    Example:
        >>> import neatlogs
        >>> tracker = neatlogs.init(
        ...     api_key="your_api_key",
        ...     tags=["tag1", "tag2"],
        ...     log_level="ERROR"
        ... )
        >>> # Now all calls are automatically tracked!
    """

    session_id = None
    agent_id = None
    thread_id = None

    global _global_tracker

    # Determine log level from parameters or environment variable
    effective_log_level = log_level or os.getenv('NEATLOGS_LOG_LEVEL')
    if effective_log_level:
        level_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        numeric_level = level_map.get(effective_log_level.upper(), logging.INFO)
        logging.basicConfig(level=numeric_level)
    elif debug:
        logging.basicConfig(level=logging.DEBUG)

    with _init_lock:
        if _global_tracker is None:
            _global_tracker = LLMTracker(
                api_key=api_key,
                session_id=session_id,
                agent_id=agent_id,
                thread_id=thread_id,
                tags=tags,
                log_level=effective_log_level if 'effective_log_level' in locals() else None,
            )
            from .instrumentation import manager
            manager.instrument_all(_global_tracker)

            # Log initialization info
            logging.info("🚀 Neatlogs Tracker initialized successfully!")
            logging.info(f"   📊 Session: {_global_tracker.session_id}")
            logging.info(f"   🤖 Agent: {_global_tracker.agent_id}")
            logging.info(f"   🧵 Thread: {_global_tracker.thread_id}")
            if tags:
                logging.info(f"   🏷️  Tags: {tags}")

    return _global_tracker


def get_langchain_callback_handler(api_key: Optional[str] = None, tags: Optional[List[str]] = None):
    """
    Get the LangChain callback handler for Neatlogs tracking.


    This function lazily imports the callback handler to avoid triggering
    framework detection when it's not needed.

    Args:
        api_key (str, optional): API key for the tracker.
        tags (List[str], optional): Tags to associate with the tracking session.

    Returns:
        NeatlogsLangchainCallbackHandler: The callback handler instance.
    """
    from .integration.callbacks.langchain.callback import NeatlogsLangchainCallbackHandler
    return NeatlogsLangchainCallbackHandler(api_key=api_key, tags=tags)


def add_tags(tags: List[str]):
    """
    Add tags to the current Neatlogs tracker.


    Args:
        tags (list): List of tags to add

    Example:
        >>> neatlogs.add_tags(["production", "customer-support", "v2.1"])
    """
    tracker = get_tracker()
    if not tracker:
        raise RuntimeError(
            "Tracker not initialized. Call neatlogs.init() first.")

    tracker.add_tags(tags)


# --- Automatic Instrumentation Setup ---
# This is the core of the "magic". The import hook is set up
# the moment the neatlogs library is imported.
setup_import_monitor()


def _shutdown_neatlogs():
    """Shutdown the Neatlogs tracker and clean up resources on exit."""
    logging.debug("Neatlogs: atexit handler '_shutdown_neatlogs' called.")
    tracker = get_tracker()
    if tracker:
        tracker.shutdown()
    logging.debug("Neatlogs: atexit handler '_shutdown_neatlogs' finished.")


# Ensure that all data is sent and resources are cleaned up on exit.
atexit.register(_shutdown_neatlogs)


# Configure a default handler for the library's logger.
# This prevents "No handler found" warnings if the user of the library
# does not configure logging.
logging.getLogger(__name__).addHandler(logging.NullHandler())
