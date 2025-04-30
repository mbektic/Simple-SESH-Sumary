"""
Logging configuration module for Simple-SESH-Summary.

This module provides a comprehensive logging configuration with both console and file output,
log rotation, and detailed error information for troubleshooting.
"""
import os
import sys
import logging
import logging.handlers
from datetime import datetime
from typing import Optional, Dict, Any

# Default log directory
LOG_DIR = "logs"

# Log levels mapping
LOG_LEVELS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL
}

def ensure_log_directory(log_dir: str = LOG_DIR) -> str:
    """
    Ensure the log directory exists, creating it if necessary.
    
    Args:
        log_dir (str): Path to the log directory
        
    Returns:
        str: Path to the log directory
        
    Raises:
        PermissionError: If the directory cannot be created due to permission issues
    """
    try:
        if not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        return log_dir
    except Exception as e:
        # If we can't create the log directory, fall back to the current directory
        print(f"Warning: Could not create log directory {log_dir}: {e}")
        print(f"Falling back to current directory for logs")
        return "."

def configure_logging(
    level: str = "info",
    log_file: Optional[str] = None,
    log_dir: str = LOG_DIR,
    max_size: int = 10 * 1024 * 1024,  # 10 MB
    backup_count: int = 5,
    console: bool = True
) -> Dict[str, Any]:
    """
    Configure logging with both console and file handlers.
    
    Args:
        level (str): Log level (debug, info, warning, error, critical)
        log_file (Optional[str]): Name of the log file. If None, a default name with timestamp will be used
        log_dir (str): Directory to store log files
        max_size (int): Maximum size of each log file in bytes before rotation
        backup_count (int): Number of backup log files to keep
        console (bool): Whether to log to console
        
    Returns:
        Dict[str, Any]: Dictionary with logging configuration details
        
    Raises:
        ValueError: If an invalid log level is provided
    """
    # Validate log level
    if level.lower() not in LOG_LEVELS:
        valid_levels = ", ".join(LOG_LEVELS.keys())
        raise ValueError(f"Invalid log level: {level}. Valid levels are: {valid_levels}")
    
    log_level = LOG_LEVELS[level.lower()]
    
    # Create a root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove any existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create formatters
    console_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    file_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(name)s - %(filename)s:%(lineno)d - %(funcName)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Add a console handler if requested
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(log_level)
        root_logger.addHandler(console_handler)
    
    # Add file handler
    log_dir = ensure_log_directory(log_dir)
    
    if log_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = f"sesh_summary_{timestamp}.log"
    
    log_path = os.path.join(log_dir, log_file)
    
    try:
        file_handler = logging.handlers.RotatingFileHandler(
            log_path,
            maxBytes=max_size,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(log_level)
        root_logger.addHandler(file_handler)
    except Exception as e:
        # If we can't create the file handler, log a warning and continue with console only
        if console:
            logging.warning(f"Could not create log file {log_path}: {e}")
            logging.warning("Continuing with console logging only")
        else:
            # If console logging is also disabled, we need to enable it as a fallback
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(console_formatter)
            console_handler.setLevel(log_level)
            root_logger.addHandler(console_handler)
            logging.warning(f"Could not create log file {log_path}: {e}")
            logging.warning("Falling back to console logging")
    
    # Log the configuration
    logging.info(f"Logging configured with level: {level.upper()}")
    if log_dir != ".":
        logging.info(f"Log directory: {os.path.abspath(log_dir)}")
    logging.info(f"Log file: {log_path}")
    
    return {
        "level": level,
        "log_file": log_path,
        "log_dir": log_dir,
        "max_size": max_size,
        "backup_count": backup_count,
        "console": console
    }

def log_exception(exc_info=None):
    """
    Log an exception with detailed traceback information.
    
    Args:
        exc_info: Exception information from sys.exc_info(). If None, it will be obtained.
    """
    if exc_info is None:
        exc_info = sys.exc_info()
    
    if exc_info[0] is not None:  # If there's an actual exception
        logging.error(
            "Exception occurred",
            exc_info=exc_info
        )

def log_system_info():
    """
    Log system information that might be useful for troubleshooting.
    """
    import platform
    
    logging.info("System Information:")
    logging.info(f"  Python version: {platform.python_version()}")
    logging.info(f"  Platform: {platform.platform()}")
    logging.info(f"  System: {platform.system()} {platform.release()}")
    logging.info(f"  Machine: {platform.machine()}")
    logging.info(f"  Processor: {platform.processor()}")

    # Log environment variables that might be relevant
    env_vars = ["PATH", "PYTHONPATH", "TEMP", "TMP"]
    for var in env_vars:
        if var in os.environ:
            logging.debug(f"  {var}: {os.environ[var]}")