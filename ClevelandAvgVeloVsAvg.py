from pybaseball import statcast, statcast_pitcher
import matplotlib.pyplot as plt
import pandas as pd
from pitchingStatsEnum import statcastColumns

start_date = "2025-09-01"
end_date   = "2025-09-14"

# --- Mariners starters ---
mariner_ids = {
    "Tanner Bibee": 676440,  
    "Gavin Williams": 668909, 
    "Slade Cecconi ": 677944,
    "Logan Allen": 671106,
    "Parker Messick": 800048    
}

# Define which pitch types count as fastballs by mlbstatcast
# note: the abbreviations are mostly "backwards"
# FF = Four Seam
# FT = Two-Seam Fastball
# FC = Cutter (Cut Fastball)
# SI = Sinker
# FA = Generic Fastball
fastball_types = ["FF", "FT", "FC", "SI", "FA"]

starter_dataframes = {}
for player_name, player_id in mariner_ids.items():
    dataframe = statcast_pitcher(start_date, end_date, player_id)
    dataframe = dataframe[dataframe[statcastColumns.release_speed] > 60]  # remove junk data
    dataframe = dataframe[dataframe[statcastColumns.pitch_type].isin(fastball_types)]  # only fastballs
    starter_dataframes[player_name] = dataframe

# --- League-wide data ---
print("Fetching league-wide data (this may take a few minutes)...")
league_dataframe = statcast(start_dt=start_date, end_dt=end_date)
league_dataframe = league_dataframe[league_dataframe[statcastColumns.release_speed] > 60]
league_dataframe = league_dataframe[league_dataframe[statcastColumns.pitch_type].isin(fastball_types)]

# --- Compute average league velocity ---
league_average = league_dataframe[statcastColumns.release_speed].mean()
print(f"League average fastball velocity: {league_average:.2f} mph")

# --- Plotting ---
plt.figure(figsize=(10, 6))
plt.axvline(league_average, color='black', linestyle='--', label=f"League average: {league_average:.1f} mph")

# alpha is transparency
# bins is how many sections of velocity there are 
for player_name, dataframe in starter_dataframes.items():
    plt.hist(
        dataframe[statcastColumns.release_speed], 
        bins=35, alpha=0.35, 
        label=f"{player_name} (mean: {dataframe[statcastColumns.release_speed].mean():.2f} mph)"
    )

plt.title("Cleveland Guardians Top 5 Starters — Fastball Velocity vs League Average (2025)")
plt.xlabel("Fastball Velocity (mph)")
plt.ylabel("Number of Pitches")
plt.legend()
plt.tight_layout()
plt.show()
