import pandas as pd
import numpy as np
from statsbombpy import sb

def get_set_piece_shots(df):
    #df['player_id'] = df['player_id'].astype('int64')
    shots_for_set_piece = df[(df['type'] == 'Shot') & (df['play_pattern'].str.contains('From')) & (df['shot_body_part'] == 'Head')][['type', 'team','player', 'play_pattern', 'shot_statsbomb_xg', 'shot_body_part']]

    #shots_for_set_piece['player_id'] = shots_for_set_piece['player_id'].astype('int64')

    return shots_for_set_piece

def generate_player_height(num_players=1):
    return np.random.normal(loc=180, scale=4, size=num_players).clip(172, 195)


def get_lineups(match_id, home_team, away_team):
    lineups = pd.concat([sb.lineups(match_id)[home_team], sb.lineups(match_id)[away_team]])
    lineups['player_height'] = generate_player_height(len(lineups))
    return lineups[['player_name', 'player_height']]

def merge_shots_heights(df, match_id, home_team, away_team):
    shots = get_set_piece_shots(df)
    if shots.empty:
        return shots
    else:
        lineups = get_lineups(match_id, home_team, away_team)
        return pd.merge(shots, lineups, left_on='player', right_on = 'player_name', how='left')