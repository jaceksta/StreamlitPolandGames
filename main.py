import streamlit as st
import pandas as pd
from statsbombpy import sb
from game_state import get_gamestate
from game_state import plot_game_state
import matplotlib.pyplot as plt
from set_piece import merge_shots_heights
from half_spaces import plot_half_space_passes
from mplsoccer import Pitch

def get_poland_games():
    comps = sb.competitions()

    comps = comps[(comps['competition_gender'] == 'male') & (comps['competition_international'] == True)
              & (comps['season_name'] > '2017') & (comps['country_name'] != 'Africa')]
    
    matches = pd.DataFrame()

    for index, row in comps.iterrows():
        temp = sb.matches(row['competition_id'], row['season_id'])
        matches = pd.concat([matches, temp])
        
    matches = matches[(matches['home_team'] == 'Poland') | (matches['away_team'] == 'Poland')]

    matches = matches[['match_id','home_team', 'away_team', 'home_score', 'away_score', 'match_date', 'competition', 'season']]
    matches['game_name'] = matches['home_team'] + ' vs ' + matches['away_team'] + ' ('+ matches['season'] + ')'
    return matches
    
games = get_poland_games()

st.title('Poland National Team Games')
game = st.selectbox('Select a game', games['game_name'].unique())
selected_game = games[games['game_name'] == game]

with st.expander('Game State xG Data'):
    
    match_id = selected_game['match_id'].values[0]
    home_team = selected_game['home_team'].values[0]
    away_team = selected_game['away_team'].values[0]

    df = sb.events(match_id)
    game_state = get_gamestate(df, home_team, away_team)
    on = st.toggle("xG per 90", True)
    fig = plt.figure(figsize=(10, 6))
    plot_game_state(game_state, home_team, away_team, on)
    st.pyplot(fig)


with st.expander('Smallest Header Shot from Set Piece'):
    st.caption("Please note that free version of StatsBomb data does not include player height. The height are generated randomly.")
    temp = merge_shots_heights(df, match_id, home_team, away_team)
    smallest_player = temp.sort_values(by='player_height', ascending=True).head(1)
    st.write(f"The smallest player to head at goal from set piece was {smallest_player['player_name'].values[0]} at {smallest_player['player_height'].values[0].round(2)} cm")
    
with st.expander('Half Space Passes'):
    set_piece = st.toggle("Include Set Piece Passes", True)
    fig2 = plot_half_space_passes(df, home_team, away_team, set_piece)
    st.pyplot(fig2)