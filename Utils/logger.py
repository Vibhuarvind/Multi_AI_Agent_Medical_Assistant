"""Centralized logging configuration for all agents."""

import logging
import sys

# Global flag to ensure root logger is only configured once
_LOGGING_CONFIGURED = False


def get_logger(name: str) -> logging.Logger:
    """
    Returns a configured logger with consistent formatting.
    
    Args:
        name: Logger name (typically __name__ from calling module)
    
    Returns:
        Configured logger instance
    """
    global _LOGGING_CONFIGURED
    
    # Configure root logger only once
    if not _LOGGING_CONFIGURED:
        root = logging.getLogger()
        
        # Clear any existing handlers to prevent duplicates
        root.handlers.clear()
        
        root.setLevel(logging.INFO)
        
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.INFO)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        
        root.addHandler(handler)
        _LOGGING_CONFIGURED = True
    
    # Return a child logger (inherits from root)
    return logging.getLogger(name)


def configure_root_logger():
    """
    Configure the root logger for the entire application.
    (Legacy function - now handled automatically by get_logger)
    """
    get_logger("root")

