from pybaseball import statcast, team_pitching, playerid_lookup
import pandas as pd
import matplotlib.pyplot as plt
from pitchingStatsEnum import statcastColumns

start_date = "2025-09-01"
end_date   = "2025-09-14"
team_abbr = str.capitalize(input("Enter team abbreviation to lookup top starters: "))
# team_abbr  = "CHC" 
fastball_types = ["FF", "FT", "FC", "SI", "FA"]

# --- Pull Statcast data for the team within the range ---
print(f"Fetching Statcast data for {team_abbr} from {start_date} to {end_date}...")
team_df = statcast(start_dt=start_date, end_dt=end_date)
team_df = team_df[
    (team_df[statcastColumns.home_team] == team_abbr) |
    (team_df[statcastColumns.away_team] == team_abbr)
]
team_df = team_df[team_df[statcastColumns.release_speed] > 60]

# --- flag pitchers who started games ---
# "inning" == 1 and "outs_when_up" == 0 generally means they started that game.
starter_flags = team_df[
    (team_df[statcastColumns.inning] == 1) &
    (team_df[statcastColumns.outs_when_up] == 0)
][[statcastColumns.pitcher, statcastColumns.player_name, statcastColumns.game_date]].drop_duplicates()

# Count how many starts each pitcher made in that time frame
starter_counts = starter_flags[statcastColumns.player_name].value_counts().head(5)

print("\nTop 5 starters in this period:")
print(starter_counts)

# --- Build dict of player IDs and names ---
starter_ids = {
    name: int(team_df[team_df[statcastColumns.player_name] == name][statcastColumns.pitcher].iloc[0])
    for name in starter_counts.index
}


# (same section as previous loookups)
# --- Compute League average fastball velocity ---
print("\nFetching league-wide data (this may take a few minutes)...")
league_df = statcast(start_dt=start_date, end_dt=end_date)
league_df = league_df[league_df[statcastColumns.release_speed] > 60]
league_df = league_df[league_df[statcastColumns.pitch_type].isin(fastball_types)]
league_avg = league_df[statcastColumns.release_speed].mean()

print(f"League average fastball velocity: {league_avg:.2f} mph")

# --- Plot per-starter velocity distributions ---
plt.figure(figsize=(10,6))
plt.axvline(league_avg, color='black', linestyle='--', label=f"League avg: {league_avg:.1f} mph")

for name, pid in starter_ids.items():
    pdata = team_df[team_df['pitcher'] == pid]
    pdata = pdata[pdata[statcastColumns.pitch_type].isin(fastball_types)]
    if not pdata.empty:
        plt.hist(pdata[statcastColumns.release_speed], bins=30, alpha=0.35,
                 label=f"{name} (mean: {pdata[statcastColumns.release_speed].mean():.1f} mph)")

plt.title(f"{team_abbr} Starters — Fastball Velocity vs League Avg ({start_date[:4]})")
plt.xlabel("Fastball Velocity (mph)")
plt.ylabel("Pitch Count")
plt.legend()
plt.tight_layout()
plt.show()
