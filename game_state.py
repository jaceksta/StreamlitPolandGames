import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

def add_missing_game_states(merged_df, home_team, away_team):
    for team in [away_team, home_team]:
        if not merged_df['game_state'].str.contains(team).any():
            new_rows = [{'team': t, 'game_state': f"{team} Lead", 'shot_statsbomb_xg': np.nan, 'duration': 0} for t in [away_team, home_team]]
            merged_df = pd.concat([merged_df, pd.DataFrame(new_rows)])
    merged_df['xg_per_90']= merged_df['shot_statsbomb_xg'] / (merged_df['duration'] / 5400)
    return merged_df

def get_gamestate(df, home_team, away_team):
    df['newsecond'] = df['minute'] * 60 + df['second']
    goals = df[(df['shot_outcome'] == 'Goal') | (df['type'] == 'Own Goal For')].sort_values('newsecond')
    max_second = df['newsecond'].max()
    if goals.empty:
        
        merged_df = process_shots(df[df['type'] == 'Shot'], home_team, away_team)
        merged_df['duration'] = max_second
        return add_missing_game_states(merged_df, home_team,away_team)
                
    else:    
         
        game_states = calculate_game_states(goals, home_team, away_team, max_second)
        merged_df = pd.merge(df, game_states, on='newsecond', how='outer').sort_values('newsecond')
        merged_df['game_state'] = merged_df['game_state'].ffill()
        durations = game_states.groupby('game_state')['duration'].sum().reset_index()
        shots = merged_df[merged_df['type'] == 'Shot']
        shots = process_shots(shots, home_team, away_team)
        merged_df = pd.merge(shots, durations, on='game_state', how='left')
    
    return add_missing_game_states(merged_df, home_team, away_team)

def calculate_game_states(goals, home_team, away_team, last_second):
    state = 'Draw'
    game_states = [{'newsecond': 0, 'game_state': state, 'duration': 0}]
    home_score, away_score = 0, 0
    
    for i, goal in goals.iterrows():
        if goal['team'] == home_team:
            home_score += 1
        else:
            away_score += 1
        
        game_states.append({'newsecond': goal['newsecond'], 'game_state': state, 'duration': goal['newsecond'] - game_states[-1]['newsecond']})        
        state = 'Draw' if home_score == away_score else (f"{home_team} Lead" if home_score > away_score else f"{away_team} Lead")
        game_states.append({'newsecond': goal['newsecond']+1, 'game_state': state, 'duration': goal['newsecond']+1 - game_states[-1]['newsecond']})
    game_states.append({'newsecond': last_second, 'game_state': state, 'duration': last_second - game_states[-1]['newsecond']})
    
    return pd.DataFrame(game_states)

def process_shots(shots, home_team, away_team):
    shots['team_defending'] = shots['team'].map({home_team: away_team, away_team: home_team})
    shots['game_state'] = shots.get('game_state', 'Draw')
    
    shooting = shots.groupby(['team', 'game_state'])['shot_statsbomb_xg'].sum().reset_index()
    defending = shots.groupby(['team_defending', 'game_state'])['shot_statsbomb_xg'].sum().reset_index()
    defending = defending.rename(columns={'team_defending': 'team'})
    defending['shot_statsbomb_xg'] *= -1
    
    return pd.concat([shooting, defending]).groupby(['team', 'game_state'])['shot_statsbomb_xg'].sum().reset_index()

def plot_game_state(data, home_team, away_team, per_90=True):
    order = [f"{home_team} Lead", 'Draw', f"{away_team} Lead"]
    if per_90:
        heatmap_data = data.set_index(['team', 'game_state'])['xg_per_90'].unstack()[order]
    else:
        heatmap_data = data.set_index(['team', 'game_state'])['shot_statsbomb_xg'].unstack()[order]


    sns.heatmap(heatmap_data, 
                annot=np.where(np.isnan(heatmap_data), 'N/A', heatmap_data.round(2).astype(str)),
                fmt='', cmap='bwr', center=0)
    plt.title('Shot Statsbomb xG by Team and Game State')
    plt.show()
    return plt
