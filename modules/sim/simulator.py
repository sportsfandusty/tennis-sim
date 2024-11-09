# modules/sim/simulator.py

import time
import numpy as np
from typing import Dict, Optional, List, Any
import logging
import pandas as pd  

from modules.sim.simconfig import (
    PlayerStats,
    calculate_fantasy_points,
    get_player_stats,
    SIM_LOG_MESSAGES,
    sim_logger
)


def simulate_game(server_stats: PlayerStats, returner_stats: PlayerStats) -> Dict[str, Any]:
    """
    Simulates a single tennis game between server and returner with detailed logs.
    
    Args:
        server_stats (PlayerStats): Statistics for the serving player.
        returner_stats (PlayerStats): Statistics for the receiving player.
    
    Returns:
        Dict[str, Any]: Dictionary containing 'winner', 'aces', and 'double_faults'.
    """
    # Initialize scores
    score_map = {0: '0', 1: '15', 2: '30', 3: '40'}
    server_points = 0
    returner_points = 0
    point_number = 1  # To track point sequence
    advantage = None  # None, 'server', or 'returner'
    
    # Initialize counters
    game_aces = 0
    game_double_faults = 0

    sim_logger.debug(f"Starting game: Server ({server_stats.Player}) vs Returner ({returner_stats.Player})\n")

    while True:
        sim_logger.debug(f"--- Point {point_number} ---")
        point_number += 1

        # Debug: Current points before the point
        current_server_score = score_map.get(server_points, '40+')
        current_returner_score = score_map.get(returner_points, '40+')
        sim_logger.debug(f"Current Points -> Server: {current_server_score}, Returner: {current_returner_score}")

        # Check for Deuce or Advantage before serving
        if server_points >= 3 and returner_points >= 3:
            if advantage is None:
                sim_logger.debug("DEUCE!")
            elif advantage == 'server':
                sim_logger.debug(f"Server ({server_stats.Player}) has ADVANTAGE.")
            elif advantage == 'returner':
                sim_logger.debug(f"Returner ({returner_stats.Player}) has ADVANTAGE.")

        # Determine if first serve is in
        first_serve_in = np.random.rand() < server_stats.FirstServePercentage
        if first_serve_in:
            sim_logger.debug(f"{server_stats.Player} successfully lands a first serve.")
            # Determine if it's an ace
            is_ace = np.random.rand() < server_stats.AcePercentage
            if is_ace:
                sim_logger.debug(f"{server_stats.Player} serves an ACE!")
                game_aces += 1
                point_winner = 'server'
            else:
                # Determine if server wins the point on first serve
                if np.random.rand() < server_stats.FirstServeWonPercentage:
                    sim_logger.debug(f"{server_stats.Player} wins the point on first serve.")
                    point_winner = 'server'
                else:
                    sim_logger.debug(f"{returner_stats.Player} wins the point on {server_stats.Player}'s first serve.")
                    point_winner = 'returner'
        else:
            # First serve is a fault, attempt second serve
            sim_logger.debug(f"{server_stats.Player} faults the first serve.")
            # Determine if second serve is a double fault
            second_serve_fault = np.random.rand() < server_stats.DoubleFaultPercentage
            if second_serve_fault:
                sim_logger.debug(f"{server_stats.Player} commits a DOUBLE FAULT!")
                game_double_faults += 1
                point_winner = 'returner'
            else:
                sim_logger.debug(f"{server_stats.Player} successfully lands a second serve.")
                # Determine if server wins the point on second serve
                if np.random.rand() < server_stats.SecondServeWonPercentage:
                    sim_logger.debug(f"{server_stats.Player} wins the point on second serve.")
                    point_winner = 'server'
                else:
                    sim_logger.debug(f"{returner_stats.Player} wins the point on {server_stats.Player}'s second serve.")
                    point_winner = 'returner'

        # Update points based on who won the point
        if point_winner == 'server':
            if server_points < 3 or returner_points < 3:
                server_points += 1
                sim_logger.debug(f"{server_stats.Player} wins the point. Score: Server {score_map.get(server_points, '40')}, Returner {score_map.get(returner_points, '0')}\n")
            else:
                if advantage == 'server':
                    sim_logger.debug(f"{server_stats.Player} wins the game!\n")
                    return {'winner': server_stats.Player, 'aces': game_aces, 'double_faults': game_double_faults}
                elif advantage == 'returner':
                    advantage = None
                    sim_logger.debug("DEUCE!\n")
                else:
                    advantage = 'server'
                    sim_logger.debug(f"{server_stats.Player} gains ADVANTAGE.\n")
        else:
            if returner_points < 3 or server_points < 3:
                returner_points += 1
                sim_logger.debug(f"{returner_stats.Player} wins the point. Score: Server {score_map.get(server_points, '0')}, Returner {score_map.get(returner_points, '40')}\n")
            else:
                if advantage == 'returner':
                    sim_logger.debug(f"{returner_stats.Player} wins the game!\n")
                    return {'winner': returner_stats.Player, 'aces': game_aces, 'double_faults': game_double_faults}
                elif advantage == 'server':
                    advantage = None
                    sim_logger.debug("DEUCE!\n")
                else:
                    advantage = 'returner'
                    sim_logger.debug(f"{returner_stats.Player} gains ADVANTAGE.\n")

        # Check for game win conditions outside Deuce
        if server_points >= 4 and server_points - returner_points >= 2:
            sim_logger.debug(f"Game won by {server_stats.Player}!\n")
            return {'winner': server_stats.Player, 'aces': game_aces, 'double_faults': game_double_faults}
        elif returner_points >= 4 and returner_points - server_points >= 2:
            sim_logger.debug(f"Game won by {returner_stats.Player}!\n")
            return {'winner': returner_stats.Player, 'aces': game_aces, 'double_faults': game_double_faults}


def simulate_set(server_id: int, player1_stats: PlayerStats, player2_stats: PlayerStats) -> Dict[str, Any]:
    """
    Simulate a single set between two players, tracking game outcomes and counts.

    Args:
        server_id (int): ID of the serving player (1 or 2).
        player1_stats (PlayerStats): Statistics for Player 1.
        player2_stats (PlayerStats): Statistics for Player 2.

    Returns:
        Dict[str, Any]: Dictionary containing set winner, game outcomes, 'aces', 'double_faults', and breaks.
    """
    player1_games = 0
    player2_games = 0
    games = []
    clean_set = True  # Assume clean set until a game is lost
    set_aces = 0
    set_double_faults = 0
    player1_breaks = 0
    player2_breaks = 0

    while True:
        if server_id == 1:
            server = player1_stats
            returner = player2_stats
            serving_player = 'player1'
            receiving_player = 'player2'
        else:
            server = player2_stats
            returner = player1_stats
            serving_player = 'player2'
            receiving_player = 'player1'

        game_result = simulate_game(server, returner)
        winner = game_result['winner']
        aces = game_result['aces']
        double_faults = game_result['double_faults']

        set_aces += aces
        set_double_faults += double_faults

        games.append(winner)

        # Update game counts
        if winner == player1_stats.Player:
            player1_games += 1
            if serving_player != 'player1':
                player1_breaks += 1  # Player1 broke Player2's serve
        else:
            player2_games += 1
            if serving_player != 'player2':
                player2_breaks += 1  # Player2 broke Player1's serve
            clean_set = False  # Player lost a game in this set

        sim_logger.debug(f"Game {len(games)}: {serving_player} serves. Winner: {winner}. {'Break!' if (winner != serving_player) else 'No Break.'}")

        # Check for set win
        if (player1_games >= 6 or player2_games >= 6) and abs(player1_games - player2_games) >= 2:
            set_winner = 'player1' if player1_games > player2_games else 'player2'
            sim_logger.debug(f"Set Winner: {set_winner}, Games: {player1_games}-{player2_games}")
            return {
                'set_winner': set_winner,
                'games': games,
                'CleanSet': clean_set,
                'aces': set_aces,
                'double_faults': set_double_faults,
                'player1_breaks': player1_breaks,
                'player2_breaks': player2_breaks
            }

        # Tie-break condition
        if player1_games == 6 and player2_games == 6:
            tie_break_winner = simulate_tie_break(server_id, player1_stats, player2_stats)
            if tie_break_winner == 'player1':
                player1_games += 1
            else:
                player2_games += 1
            games.append(tie_break_winner)
            set_winner = 'player1' if player1_games > player2_games else 'player2'
            sim_logger.debug(f"Tie-Break Winner: {set_winner}, Games: {player1_games}-{player2_games}")
            return {
                'set_winner': set_winner,
                'games': games,
                'CleanSet': False,  # Tie-break implies the set wasn't clean
                'aces': set_aces,
                'double_faults': set_double_faults,
                'player1_breaks': player1_breaks,
                'player2_breaks': player2_breaks
            }

        # Alternate server
        server_id = 2 if server_id == 1 else 1


def simulate_tie_break(server_id: int, player1_stats: PlayerStats, player2_stats: PlayerStats) -> str:
    """
    Simulate a tie-break game in a tennis match.

    Args:
        server_id (int): ID of the serving player (1 or 2).
        player1_stats (PlayerStats): Statistics for Player 1.
        player2_stats (PlayerStats): Statistics for Player 2.

    Returns:
        str: 'player1' or 'player2' indicating the tie-break winner.
    """
    player1_points = 0
    player2_points = 0
    points_played = 0

    while True:
        points_played += 1
        # Determine current server based on tie-break rules
        if points_played == 1:
            current_server_id = server_id
        else:
            # After the first point, players alternate every two points
            current_server_id = 2 if ((points_played - 1) // 2) % 2 == 1 else 1

        # Assign server and returner based on current_server_id
        if current_server_id == 1:
            server = player1_stats
            returner = player2_stats
            server_player = 'player1'
        else:
            server = player2_stats
            returner = player1_stats
            server_player = 'player2'

        # Simulate the point
        game_result = simulate_game(server, returner)
        point_winner = 'player1' if game_result['winner'] == player1_stats.Player else 'player2'

        # Track aces and double faults if needed
        # For simplicity, not tracked here

        if point_winner == 'player1':
            player1_points += 1
        else:
            player2_points += 1

        sim_logger.debug(
            f"Tie-Break Point: {point_winner}, Current Score: Player1={player1_points}, Player2={player2_points}"
        )

        # Check for tie-break win condition
        if (player1_points >= 7 or player2_points >= 7) and abs(player1_points - player2_points) >= 2:
            tie_break_winner = 'player1' if player1_points > player2_points else 'player2'
            sim_logger.debug(f"Tie-Break Winner: {tie_break_winner}")
            return tie_break_winner


def simulate_match(player1_stats: PlayerStats, player2_stats: PlayerStats, best_of: int = 3) -> Dict[str, Any]:
    """
    Simulate a full tennis match between two players.

    Args:
        player1_stats (PlayerStats): Statistics for Player 1.
        player2_stats (PlayerStats): Statistics for Player 2.
        best_of (int, optional): Number of sets to play. Defaults to 3.

    Returns:
        Dict[str, Any]: Dictionary containing match winner, detailed set results, and fantasy points.
    """
    # Reset match-specific statistics before starting the match
    player1_stats.reset_match_stats()
    player2_stats.reset_match_stats()

    player1_sets = 0
    player2_sets = 0
    set_num = 1
    server_id = 1  # Assuming Player 1 serves first
    sets = []  # To store set-by-set outcomes

    # Initialize count-based statistics
    player1_fantasy_counts = {
        'Aces': 0,
        'DoubleFaults': 0,
        'GamesWon': 0,
        'GamesLost': 0,
        'SetsWon': 0,
        'SetsLost': 0,
        'Breaks': 0,
        'CleanSet': False,
        'StraightSets': False,
        'NoDoubleFault': True,
        'TenPlusAces': False,
        'FifteenPlusAces': False
    }

    player2_fantasy_counts = {
        'Aces': 0,
        'DoubleFaults': 0,
        'GamesWon': 0,
        'GamesLost': 0,
        'SetsWon': 0,
        'SetsLost': 0,
        'Breaks': 0,
        'CleanSet': False,
        'StraightSets': False,
        'NoDoubleFault': True,
        'TenPlusAces': False,
        'FifteenPlusAces': False
    }

    match_start_time = time.time()

    while True:
        set_result = simulate_set(server_id, player1_stats, player2_stats)
        set_winner = set_result['set_winner']
        games = set_result['games']
        clean_set = set_result['CleanSet']
        set_aces = set_result['aces']
        set_double_faults = set_result['double_faults']
        player1_breaks = set_result.get('player1_breaks', 0)
        player2_breaks = set_result.get('player2_breaks', 0)

        # Update set counts
        if set_winner == 'player1':
            player1_sets += 1
            player1_fantasy_counts['SetsWon'] += 1
            player2_fantasy_counts['SetsLost'] += 1
        else:
            player2_sets += 1
            player2_fantasy_counts['SetsWon'] += 1
            player1_fantasy_counts['SetsLost'] += 1

        # Update game counts
        player1_fantasy_counts['GamesWon'] += games.count(player1_stats.Player)
        player1_fantasy_counts['GamesLost'] += games.count(player2_stats.Player)
        player2_fantasy_counts['GamesWon'] += games.count(player2_stats.Player)
        player2_fantasy_counts['GamesLost'] += games.count(player1_stats.Player)

        # Update break points
        player1_fantasy_counts['Breaks'] += player1_breaks
        player2_fantasy_counts['Breaks'] += player2_breaks

        # Update Aces and Double Faults
        # Assuming aces and double faults are attributed to the server
        player1_fantasy_counts['Aces'] += set_aces if set_winner == 'player1' else 0
        player1_fantasy_counts['DoubleFaults'] += set_double_faults if set_winner == 'player1' else 0
        player2_fantasy_counts['Aces'] += set_aces if set_winner == 'player2' else 0
        player2_fantasy_counts['DoubleFaults'] += set_double_faults if set_winner == 'player2' else 0

        # Update No Double Fault Bonus
        if (set_winner == 'player1' and set_double_faults > 0) or \
           (set_winner == 'player2' and set_double_faults > 0):
            if set_winner == 'player1':
                player1_fantasy_counts['NoDoubleFault'] = False
            else:
                player2_fantasy_counts['NoDoubleFault'] = False

        # Update TenPlusAces and FifteenPlusAces Bonuses
        if player1_fantasy_counts['Aces'] >= 15:
            player1_fantasy_counts['FifteenPlusAces'] = True
        elif player1_fantasy_counts['Aces'] >= 10:
            player1_fantasy_counts['TenPlusAces'] = True

        if player2_fantasy_counts['Aces'] >= 15:
            player2_fantasy_counts['FifteenPlusAces'] = True
        elif player2_fantasy_counts['Aces'] >= 10:
            player2_fantasy_counts['TenPlusAces'] = True

        # Update Clean Set Bonus
        if clean_set:
            if set_winner == 'player1':
                player1_fantasy_counts['CleanSet'] = True
            else:
                player2_fantasy_counts['CleanSet'] = True

        sets.append({
            'set_number': set_num,
            'winner': set_winner,
            'games': games,
            'CleanSet': clean_set
        })

        sim_logger.debug(f"Set {set_num} Winner: {set_winner}, Score: Player1={player1_sets}-Player2={player2_sets}")

        # Check for match winner
        required_sets = (best_of // 2) + 1
        if player1_sets == required_sets or player2_sets == required_sets:
            match_winner = 'player1' if player1_sets > player2_sets else 'player2'
            match_duration = time.time() - match_start_time

            # Determine Straight Sets Bonus
            straight_sets = (player1_sets == required_sets and player2_sets == 0) or \
                            (player2_sets == required_sets and player1_sets == 0)
            if straight_sets:
                if match_winner == 'player1':
                    player1_fantasy_counts['StraightSets'] = True
                else:
                    player2_fantasy_counts['StraightSets'] = True

            # Prepare stats for fantasy points calculation for both players
            fantasy_stats_player1 = {
                'MatchPlayed': True,
                'AdvancedByWalkover': False,
                'Aces': player1_fantasy_counts['Aces'],
                'DoubleFaults': player1_fantasy_counts['DoubleFaults'],
                'GamesWon': player1_fantasy_counts['GamesWon'],
                'GamesLost': player1_fantasy_counts['GamesLost'],
                'SetsWon': player1_fantasy_counts['SetsWon'],
                'SetsLost': player1_fantasy_counts['SetsLost'],
                'CleanSet': player1_fantasy_counts['CleanSet'],
                'StraightSets': player1_fantasy_counts['StraightSets'],
                'NoDoubleFault': player1_fantasy_counts['NoDoubleFault'],
                'TenPlusAces': player1_fantasy_counts['TenPlusAces'],
                'FifteenPlusAces': player1_fantasy_counts['FifteenPlusAces'],
                'Breaks': player1_fantasy_counts['Breaks']
            }

            fantasy_stats_player2 = {
                'MatchPlayed': True,
                'AdvancedByWalkover': False,
                'Aces': player2_fantasy_counts['Aces'],
                'DoubleFaults': player2_fantasy_counts['DoubleFaults'],
                'GamesWon': player2_fantasy_counts['GamesWon'],
                'GamesLost': player2_fantasy_counts['GamesLost'],
                'SetsWon': player2_fantasy_counts['SetsWon'],
                'SetsLost': player2_fantasy_counts['SetsLost'],
                'CleanSet': player2_fantasy_counts['CleanSet'],
                'StraightSets': player2_fantasy_counts['StraightSets'],
                'NoDoubleFault': player2_fantasy_counts['NoDoubleFault'],
                'TenPlusAces': player2_fantasy_counts['TenPlusAces'],
                'FifteenPlusAces': player2_fantasy_counts['FifteenPlusAces'],
                'Breaks': player2_fantasy_counts['Breaks']
            }

            # Calculate Fantasy Points
            player1_fantasy_points = calculate_fantasy_points(
                stats=fantasy_stats_player1,
                match_won=(match_winner == 'player1'),
                best_of=best_of
            )

            player2_fantasy_points = calculate_fantasy_points(
                stats=fantasy_stats_player2,
                match_won=(match_winner == 'player2'),
                best_of=best_of
            )

            # Log Fantasy Points Breakdown
            sim_logger.debug(f"{player1_stats.Player} Fantasy Points: {player1_fantasy_points}")
            sim_logger.debug(f"{player2_stats.Player} Fantasy Points: {player2_fantasy_points}")

            # Return match results with separate fantasy points
            return {
                'winner': match_winner,
                'sets': sets,
                'player1_fantasy_points': player1_fantasy_points,
                'player2_fantasy_points': player2_fantasy_points,
                'duration': match_duration
            }

        set_num += 1
        server_id = 2 if server_id == 1 else 1


def run_match_simulation(player1_name: str, player2_name: str, surface: str, player_data: pd.DataFrame,
                        best_of: int = 3) -> Optional[Dict[str, Any]]:
    """
    Run a single match simulation between two players.

    Args:
        player1_name (str): Name of Player 1.
        player2_name (str): Name of Player 2.
        surface (str): Surface type ('Hard', 'Clay', 'Grass', 'All').
        player_data (pd.DataFrame): DataFrame containing player statistics.
        best_of (int, optional): Number of sets to play. Defaults to 3.

    Returns:
        Optional[Dict[str, Any]]: Dictionary containing match winner, detailed set results, and fantasy points.
    """
    try:
        player1_stats_row = get_player_stats(player1_name, surface, player_data)
        player2_stats_row = get_player_stats(player2_name, surface, player_data)

        if player1_stats_row is None or player2_stats_row is None:
            missing_player = player1_name if player1_stats_row is None else player2_name
            sim_logger.error(SIM_LOG_MESSAGES["error_running_match_simulation"].format(
                error=f"Player data not found for {missing_player}."
            ))
            return None
    except ValueError as ve:
        sim_logger.error(SIM_LOG_MESSAGES["error_running_match_simulation"].format(error=str(ve)))
        return None

    # Extract relevant statistics based on PlayerStats annotations
    player1_stats_data = {k: v for k, v in player1_stats_row.to_dict().items() if k in PlayerStats.REQUIRED_FIELDS}
    player2_stats_data = {k: v for k, v in player2_stats_row.to_dict().items() if k in PlayerStats.REQUIRED_FIELDS}

    try:
        player1_stats = PlayerStats(**player1_stats_data)
        player2_stats = PlayerStats(**player2_stats_data)
        sim_logger.info(SIM_LOG_MESSAGES["dataclass_initialized"])
    except ValueError as ve:
        sim_logger.error(SIM_LOG_MESSAGES["error_running_match_simulation"].format(error=str(ve)))
        return None

    try:
        match_result = simulate_match(player1_stats, player2_stats, best_of)
        return match_result
    except Exception as e:
        sim_logger.error(SIM_LOG_MESSAGES["error_running_match_simulation"].format(error=str(e)))
        return None
