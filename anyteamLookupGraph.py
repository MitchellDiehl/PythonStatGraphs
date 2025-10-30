import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from pybaseball import statcast
from pitchingStatsEnum import statcast_columns, mlb_teams_dict, best_match_mlb_team, calculate_statcast_era

# --- Date range ---
start_date = "2025-09-01"
end_date = "2025-09-30"

# --- Team selection ---
user_input = input("Enter team to lookup top starters: ")
team_abbr = best_match_mlb_team(user_input, mlb_teams_dict)

if not team_abbr:
    print("No close match found.")
    exit()

print(f"{team_abbr} Team Found")

# --- Fetch team Statcast data ---
league_df = statcast(start_dt=start_date, end_dt=end_date)
team_df = league_df

team_df = team_df[
    (team_df[statcast_columns.home_team] == team_abbr) |
    (team_df[statcast_columns.away_team] == team_abbr)
]
team_df = team_df[team_df[statcast_columns.release_speed] > 60]

# --- Identify starting pitchers ---
starter_flags = team_df[
    (team_df[statcast_columns.inning] == 1) &
    (team_df[statcast_columns.outs_when_up] == 0)
][[statcast_columns.pitcher, statcast_columns.player_name, statcast_columns.game_date]].drop_duplicates()

top_starters = starter_flags[statcast_columns.player_name].value_counts().head(5).index.tolist()
starter_ids = {
    name: int(team_df[team_df[statcast_columns.player_name] == name][statcast_columns.pitcher].iloc[0])
    for name in top_starters
}

# --- League average fastball velocity ---
fastball_types = ["FF", "FT", "FC", "SI", "FA"]
league_df = league_df[league_df[statcast_columns.release_speed] > 60]
league_df = league_df[league_df[statcast_columns.pitch_type].isin(fastball_types)]
league_avg = league_df[statcast_columns.release_speed].mean()

# --- PLOTTING SECTION ---
fig, ax1 = plt.subplots(figsize=(12,6))

ax1.axvline(league_avg, color='black', linestyle='--', label=f"League Avg: {league_avg:.1f} mph")

# Velocity histograms
for starter_name, starter_id in starter_ids.items():
    pdata = team_df[team_df[statcast_columns.pitcher] == starter_id]
    pdata = pdata[pdata[statcast_columns.pitch_type].isin(fastball_types)]

    if not pdata.empty:
        avg_v = pdata[statcast_columns.release_speed].mean()
        ax1.hist(
            pdata[statcast_columns.release_speed],
            bins=30,
            alpha=0.35,
            label=f"{starter_name} (avg: {avg_v:.1f} mph) (ERA: {calculate_statcast_era(starter_id, start_date, end_date):.2f})"
        )

ax1.set_xlabel("Fastball Velocity (mph)")
ax1.set_ylabel("Pitch Count")
ax1.set_title(f"{team_abbr} Starters — Fastball Velocity ({start_date} to {end_date})")
ax1.legend(loc="upper right")

plt.tight_layout()
plt.show()
