# modules/sim/simconfig.py

import pandas as pd
from typing import Optional, Dict, Any, ClassVar, List
from dataclasses import dataclass
import logging

from utils.logger import SIM_LOG_MESSAGES, get_logger

# Initialize logger
sim_logger = get_logger('simulation')


@dataclass
class PlayerStats:
    """
    Dataclass representing a player's statistics using only rate (percentage-based) stats.
    """
    Player: str
    Surface: str
    League: str
    FirstServePercentage: float
    AcePercentage: float
    FirstServeWonPercentage: float
    SecondServeWonPercentage: float
    DoubleFaultPercentage: float
    ServiceGamesWonPercentage: float
    ReturnGamesWonPercentage: float
    PointsWonPercentage: float
    GamesWonPercentage: float
    SetsWonPercentage: float
    TieBreaksWonPercentage: float
    BreakPointsSavedPercentage: float
    BreakPointsConvertedPercentage: float
    FirstServeReturnPointsWonPercentage: float
    SecondServeReturnPointsWonPercentage: float
    ReturnPointsWonPercentage: float
    ServicePointsWonPercentage: float
    BreakPointsFacedPerServiceGame: float
    AceAgainstPercentage: float
    AcesAgainstPerReturnGame: float
    BreakPointChancesPerReturnGame: float

    # Class variable listing all required fields for validation
    REQUIRED_FIELDS: ClassVar[List[str]] = [
        'Player',
        'Surface',
        'League',
        'FirstServePercentage',
        'AcePercentage',
        'FirstServeWonPercentage',
        'SecondServeWonPercentage',
        'DoubleFaultPercentage',
        'ServiceGamesWonPercentage',
        'ReturnGamesWonPercentage',
        'PointsWonPercentage',
        'GamesWonPercentage',
        'SetsWonPercentage',
        'TieBreaksWonPercentage',
        'BreakPointsSavedPercentage',
        'BreakPointsConvertedPercentage',
        'FirstServeReturnPointsWonPercentage',
        'SecondServeReturnPointsWonPercentage',
        'ReturnPointsWonPercentage',
        'ServicePointsWonPercentage',
        'BreakPointsFacedPerServiceGame',
        'AceAgainstPercentage',
        'AcesAgainstPerReturnGame',
        'BreakPointChancesPerReturnGame'
    ]

    def __post_init__(self):
        """
        Validate that all required fields are present and within valid ranges.
        """
        for field_name in self.REQUIRED_FIELDS:
            value = getattr(self, field_name, None)
            if value is None:
                sim_logger.error(SIM_LOG_MESSAGES["missing_stat_warning"].format(
                    field=field_name,
                    player_name=self.Player
                ))
                raise ValueError(f"Missing required field: {field_name}")
            if isinstance(value, float) and not (0.0 <= value <= 1.0):
                sim_logger.error(SIM_LOG_MESSAGES["invalid_stat_value"].format(
                    field=field_name,
                    player_name=self.Player
                ))
                raise ValueError(f"Invalid value for {field_name}: {value}. Must be between 0 and 1.")

    def reset_match_stats(self):
        """
        Reset match-specific statistics to their default values before starting a new match.
        """
        pass  # No action needed as counts are handled in simulator.py


def load_player_data(filepath: str) -> pd.DataFrame:
    """
    Load player statistics from a CSV file, utilizing only rate (percentage-based) stats.

    Args:
        filepath (str): Path to the CSV file.

    Returns:
        pd.DataFrame: DataFrame containing player statistics.
    """
    try:
        player_data = pd.read_csv(filepath)
        player_data = player_data.copy()  # Work on a copy to avoid SettingWithCopyWarning

        # Ensure all required columns are present
        required_columns = [
            'Player',
            'Surface',
            'League',
            'FirstServePercentage',
            'AcePercentage',
            'FirstServeWonPercentage',
            'SecondServeWonPercentage',
            'DoubleFaultPercentage',
            'ServiceGamesWonPercentage',
            'ReturnGamesWonPercentage',
            'PointsWonPercentage',
            'GamesWonPercentage',
            'SetsWonPercentage',
            'TieBreaksWonPercentage',
            'BreakPointsSavedPercentage',
            'BreakPointsConvertedPercentage',
            'FirstServeReturnPointsWonPercentage',
            'SecondServeReturnPointsWonPercentage',
            'ReturnPointsWonPercentage',
            'ServicePointsWonPercentage',
            'BreakPointsFacedPerServiceGame',
            'AceAgainstPercentage',
            'AcesAgainstPerReturnGame',
            'BreakPointChancesPerReturnGame'
        ]
        missing_columns = [col for col in required_columns if col not in player_data.columns]
        if missing_columns:
            sim_logger.error(SIM_LOG_MESSAGES["missing_columns_error"].format(
                columns=', '.join(missing_columns)
            ))
            raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")

        # Standardize the 'Player' column to lowercase for case-insensitive matching
        player_data['Player_lower'] = player_data['Player'].str.lower()

        sim_logger.info(SIM_LOG_MESSAGES["load_player_data"].format(filepath=filepath))
        return player_data
    except Exception as e:
        # Corrected logging statement with both 'filepath' and 'error'
        sim_logger.error(SIM_LOG_MESSAGES["load_player_data_error"].format(filepath=filepath, error=e))
        return pd.DataFrame()


def get_player_stats(player_name: str, surface: str, player_data: pd.DataFrame) -> Optional[pd.Series]:
    """
    Retrieve player statistics based on name and surface.

    Args:
        player_name (str): Name of the player.
        surface (str): Surface type ('Hard', 'Clay', 'Grass', or 'All').
        player_data (pd.DataFrame): DataFrame containing player statistics.

    Returns:
        Optional[pd.Series]: Player statistics if found, else None.
    """
    player_name_lower = player_name.lower()
    surface_lower = surface.lower()

    # Filter based on the standardized 'Player_lower' name and 'Surface'
    player_row = player_data[
        (player_data['Player_lower'] == player_name_lower) &
        (player_data['Surface'].str.lower() == surface_lower)
    ]

    if player_row.empty:
        # Attempt to find stats with 'All' surfaces
        player_row = player_data[
            (player_data['Player_lower'] == player_name_lower) &
            (player_data['Surface'].str.lower() == 'all')
        ]

    if player_row.empty:
        sim_logger.warning(SIM_LOG_MESSAGES["get_player_stats_warning"].format(
            player_name=player_name, surface=surface
        ))
        return None

    return player_row.iloc[0]  # Return a single row as a Series


def calculate_fantasy_points(stats: Dict[str, Any], match_won: bool, best_of: int) -> float:
    """
    Calculate DraftKings fantasy points for a tennis player based on match statistics.

    Args:
        stats (Dict[str, Any]): Dictionary containing player's match statistics and bonuses.
            Expected keys:
                - 'MatchPlayed' (bool)
                - 'AdvancedByWalkover' (bool)
                - 'Aces' (int)
                - 'DoubleFaults' (int)
                - 'GamesWon' (int)
                - 'GamesLost' (int)
                - 'SetsWon' (int)
                - 'SetsLost' (int)
                - 'CleanSet' (bool)
                - 'StraightSets' (bool)
                - 'NoDoubleFault' (bool)
                - 'TenPlusAces' (bool)
                - 'FifteenPlusAces' (bool)
                - 'Breaks' (int)
        match_won (bool): Indicates whether the player won the match.
        best_of (int): Number of sets to play (3 or 5).

    Returns:
        float: Calculated fantasy points.
    """
    points = 0.0

    # Base Points
    if stats.get('MatchPlayed', False):
        points += 30  # Match Played

    if stats.get('AdvancedByWalkover', False):
        points += 30  # Advanced By Walkover

    # Match Outcome
    if match_won:
        if best_of == 3:
            points += 6  # Match Won for Best of 3
        elif best_of == 5:
            points += 5  # Match Won for Best of 5

    # Games
    games_won = stats.get('GamesWon', 0)
    games_lost = stats.get('GamesLost', 0)
    if best_of == 3:
        points += games_won * 2.5  # Game Won
        points -= games_lost * 2    # Game Lost
    elif best_of == 5:
        points += games_won * 2      # Game Won
        points -= games_lost * 1.6  # Game Lost

    # Sets
    sets_won = stats.get('SetsWon', 0)
    sets_lost = stats.get('SetsLost', 0)
    if best_of == 3:
        points += sets_won * 6    # Set Won
        points -= sets_lost * 3   # Set Lost
    elif best_of == 5:
        points += sets_won * 5    # Set Won
        points -= sets_lost * 2.5  # Set Lost

    # Aces
    aces = stats.get('Aces', 0)
    if best_of == 3:
        points += aces * 0.4  # Ace
    elif best_of == 5:
        points += aces * 0.25  # Ace

    # Double Faults
    double_faults = stats.get('DoubleFaults', 0)
    points -= double_faults * 1  # Double Fault

    # Breaks
    breaks = stats.get('Breaks', 0)
    if best_of == 3:
        points += breaks * 0.75  # Break Point Converted
    elif best_of == 5:
        points += breaks * 0.5  # Break Point Converted

    # Bonuses
    if stats.get('CleanSet', False):
        if best_of == 3:
            points += 4  # Clean Set Bonus for Best of 3
        elif best_of == 5:
            points += 2.5  # Clean Set Bonus for Best of 5

    if stats.get('StraightSets', False):
        if best_of == 3:
            points += 6  # Straight Sets Bonus for Best of 3
        elif best_of == 5:
            points += 5  # Straight Sets Bonus for Best of 5

    if stats.get('NoDoubleFault', False):
        if best_of == 3:
            points += 2.5  # No Double Fault Bonus for Best of 3
        elif best_of == 5:
            points += 5    # No Double Fault Bonus for Best of 5

    if stats.get('TenPlusAces', False):
        points += 2  # 10+ Ace Bonus

    if stats.get('FifteenPlusAces', False):
        points += 2  # 15+ Ace Bonus

    sim_logger.debug(f"Calculating fantasy points: {points} from stats: {stats}, Match Won: {match_won}, Best of: {best_of}")
    return points
