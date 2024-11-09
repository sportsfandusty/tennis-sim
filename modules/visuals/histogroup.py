import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import time

# Define player names
players = ['Player 1', 'Player 2', 'Player 3']
bins = np.linspace(0, 100, 20)
placeholders = {player: st.empty() for player in players}

# Initialize empty data storage for each player
data = {player: [] for player in players}

for i in range(100):  # Simulate 100 data points for each player
    for player in players:
        # Append new data
        new_data_point = np.random.normal(50, 10)
        data[player].append(new_data_point)
        
        # Plot each player's histogram with current data
        fig, ax = plt.subplots()
        ax.hist(data[player], bins=bins, color='blue', alpha=0.7)
        ax.set_xlim(0, 100)
        ax.set_ylim(0, 20)
        ax.set_xlabel('Fantasy Points')
        ax.set_ylabel('Frequency')
        ax.set_title(f"{player}'s Fantasy Points Distribution")
        
        # Update the placeholder with the new plot
        placeholders[player].pyplot(fig)
    
    # Pause for effect
    time.sleep(0.1)
