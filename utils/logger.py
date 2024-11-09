# utils/logger.py

import logging

# Define SIM_LOG_MESSAGES with all required keys
SIM_LOG_MESSAGES = {
    "missing_stat_warning": "Missing stat '{field}' for player {player_name}.",
    "invalid_stat_value": "Invalid value for '{field}' for player {player_name}'. Must be between 0 and 1.",
    "missing_columns_error": "Missing required columns: {columns}.",
    "load_player_data": "Loaded player data from {filepath}.",
    "load_player_data_error": "Failed to load player data from {filepath}. Error: {error}",
    "get_player_stats_warning": "Player data not found for '{player_name}' on surface '{surface}'.",
    "error_running_match_simulation": "Error running match simulation: {error}",
    "dataclass_initialized": "PlayerStats dataclass initialized successfully.",
    "variance_stat_value": "Original stat: {stats}, Variance: {variance}, Varied stat: {varied_stat}.",
    "game_result": "Game Result - Winner: {winner}, Aces: {aces}, Double Faults: {double_faults}.",
    # Add other messages as needed
}

def get_logger(name: str) -> logging.Logger:
    """
    Configures and returns a logger with the specified name.

    Args:
        name (str): Name of the logger.

    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Prevent adding multiple handlers if the logger already has handlers
    if not logger.handlers:
        # Create console handler for warnings and above
        c_handler = logging.StreamHandler()
        c_handler.setLevel(logging.WARNING)

        # Create file handler for all logs
        f_handler = logging.FileHandler('simulation.log')
        f_handler.setLevel(logging.INFO)

        # Create formatters
        c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
        f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # Assign formatters to handlers
        c_handler.setFormatter(c_format)
        f_handler.setFormatter(f_format)

        # Add handlers to the logger
        logger.addHandler(c_handler)
        logger.addHandler(f_handler)

    return logger
