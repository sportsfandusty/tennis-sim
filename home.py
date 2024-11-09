# main.py

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objs as go
import time
from modules.sim.simconfig import load_player_data
from modules.sim.simulator import run_match_simulation, PlayerStats



st.set_page_config(page_title="Tennis Simulator", layout="wide")




# Load player data
@st.cache_data
def get_player_data():
    filepath = 'data/tennis/player_stats_with_id.csv'  # Adjust the path as needed
    data = load_player_data(filepath)
    if data.empty:
        st.error("Player data could not be loaded. Please check the CSV file.")
    return data

player_data = get_player_data()

# Ensure 'Category' column exists for ATP/WTA
if 'Category' not in player_data.columns:
    # Assuming 'League' can indicate ATP or WTA
    # Adjust based on actual data
    # For example, 'ATP' for male players, 'WTA' for female players
    player_data['Category'] = player_data['League'].apply(
        lambda x: 'ATP' if 'ATP' in x.upper() else 'WTA' if 'WTA' in x.upper() else 'Unknown'
    )

# Sidebar for player and surface selection
st.sidebar.header("v0.1.0-alpha")
st.sidebar.header("Simulation Settings")
# Select Surface Type
available_surfaces = player_data['Surface'].unique().tolist()
available_surfaces = [surf for surf in available_surfaces if surf.lower() != 'unknown']
selected_surface = st.sidebar.selectbox("Select Surface Type", options=available_surfaces, index=0)

# Select Player
selected_player = st.sidebar.selectbox("Select Player", options=player_data['Player'].unique())

# Filter opponents based on selected player's category and surface
player_filtered_data = player_data[
    (player_data['Player'] == selected_player) &
    (player_data['Surface'] == selected_surface)
]

if player_filtered_data.empty:
    st.error(f"{selected_player} does not have statistics for the {selected_surface} surface.")
    st.stop()

selected_player_row = player_filtered_data.iloc[0]
selected_category = selected_player_row['Category']

# Get valid opponents
valid_opponents = player_data[
    (player_data['Category'] == selected_category) &
    (player_data['Surface'] == selected_surface)
]['Player'].tolist()
if selected_player in valid_opponents:
    valid_opponents.remove(selected_player)  # Remove self from opponents

# Check if there are valid opponents
if not valid_opponents:
    st.warning(f"No valid opponents available for {selected_player} on the {selected_surface} surface.")
    st.stop()

# Select Opponent
selected_opponent = st.sidebar.selectbox("Select Opponent", options=valid_opponents)



# Simulation settings


# Define exponential increments
simulation_steps = [1, 10, 100, 1000]

# Slider for number of simulations
num_simulations = st.sidebar.select_slider(
    "Number of Simulations",
    options=simulation_steps,
    value=100
)

# Button to run simulation
if st.sidebar.button("Run Simulation"):
    # Initialize lists to store fantasy points
    player1_fantasy_points = []
    player2_fantasy_points = []

    # Initialize progress bar and status
    progress_bar = st.progress(0)
    status_text = st.empty()

    # Initialize histogram plot using Plotly
    histogram_placeholder = st.empty()

    # Total simulations
    total = num_simulations
    batch_size = 5  # Smaller batch size for smoother updates

    # Calculate number of batches
    num_batches = total // batch_size
    remainder = total % batch_size

    # Simulation Loop with smaller batches
    for batch in range(num_batches):
        for _ in range(batch_size):
            match_result = run_match_simulation(
                selected_player,
                selected_opponent,
                selected_surface,
                player_data,
                best_of=3
            )
            if match_result:
                player1_fantasy_points.append(match_result['player1_fantasy_points'])
                player2_fantasy_points.append(match_result['player2_fantasy_points'])
        # Update progress
        progress = (batch + 1) / num_batches
        progress_bar.progress(min(progress, 1.0))
        status_text.text(f"Simulating {min((batch + 1)*batch_size, total)} out of {total} matches...")

        # Update histogram using Plotly for better performance
        hist1 = go.Histogram(
            x=player1_fantasy_points,
            nbinsx=30,
            name=selected_player,
            opacity=0.6,
            marker_color='blue'
        )
        hist2 = go.Histogram(
            x=player2_fantasy_points,
            nbinsx=30,
            name=selected_opponent,
            opacity=0.6,
            marker_color='orange'
        )

        layout = go.Layout(
            title='Fantasy Points Distribution',
            xaxis_title='Fantasy Points',
            yaxis_title='Frequency',
            barmode='overlay',
            width=1600,   # Smaller width
            height=800   # Smaller height
        )

        fig = go.Figure(data=[hist1, hist2], layout=layout)
        histogram_placeholder.plotly_chart(fig, use_container_width=False)

        # Allow Streamlit to update
        time.sleep(0.001)  # Minimal sleep to ensure UI responsiveness

    # Handle remainder simulations
    if remainder > 0:
        for _ in range(remainder):
            match_result = run_match_simulation(
                selected_player,
                selected_opponent,
                selected_surface,
                player_data,
                best_of=3
            )
            if match_result:
                player1_fantasy_points.append(match_result['player1_fantasy_points'])
                player2_fantasy_points.append(match_result['player2_fantasy_points'])
        # Update progress to 100%
        progress_bar.progress(1.0)
        status_text.text(f"Simulating {total} out of {total} matches...")

        # Final histogram using Plotly
        hist1 = go.Histogram(
            x=player1_fantasy_points,
            nbinsx=30,
            name=selected_player,
            opacity=0.6,
            marker_color='blue'
        )
        hist2 = go.Histogram(
            x=player2_fantasy_points,
            nbinsx=30,
            name=selected_opponent,
            opacity=0.6,
            marker_color='orange'
        )

        layout = go.Layout(
            title='Fantasy Points Distribution',
            xaxis_title='Fantasy Points',
            yaxis_title='Frequency',
            barmode='overlay',
            width=1600,   # Smaller width
            height=800   # Smaller height
        )

        fig = go.Figure(data=[hist1, hist2], layout=layout)
        histogram_placeholder.plotly_chart(fig, use_container_width=False)

    # Display final results
    st.success(f"✅ Simulation completed: {total} matches simulated.")

    # Display statistics
    st.header("📊 Match Statistics")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader(f"{selected_player} Fantasy Points")
        st.write(f"**Mean:** {np.mean(player1_fantasy_points):.2f}")
        st.write(f"**Median:** {np.median(player1_fantasy_points):.2f}")
        st.write(f"**Std Dev:** {np.std(player1_fantasy_points):.2f}")
    with col2:
        st.subheader(f"{selected_opponent} Fantasy Points")
        st.write(f"**Mean:** {np.mean(player2_fantasy_points):.2f}")
        st.write(f"**Median:** {np.median(player2_fantasy_points):.2f}")
        st.write(f"**Std Dev:** {np.std(player2_fantasy_points):.2f}")
    
    
    # Optionally, provide more detailed statistics or plots