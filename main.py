import streamlit as st
import pandas as pd
from statsbombpy import sb
from game_state import get_gamestate
from game_state import plot_game_state
import matplotlib.pyplot as plt
from set_piece import merge_shots_heights
from half_spaces import plot_half_space_passes, filter_half_space_passes_to_penalty


def get_comp_games():
    comps = sb.competitions()

    comps = comps[(comps['competition_gender'] == 'male') & (comps['competition_international'] == True)
              & (comps['season_name'] > '2017') & (comps['country_name'] != 'Africa')]
    
    matches = pd.DataFrame()

    for index, row in comps.iterrows():
        temp = sb.matches(row['competition_id'], row['season_id'])
        matches = pd.concat([matches, temp])
        
    return matches

def get_team_games(matches, team_name):
    matches = matches[(matches['home_team'] == team_name) | (matches['away_team'] == team_name)]

    matches = matches[['match_id','home_team', 'away_team', 'home_score', 'away_score', 'match_date', 'competition', 'season']]
    matches['game_name'] = matches['home_team'] + ' vs ' + matches['away_team'] + ' ('+ matches['season'] + ')'
    return matches
    
games = get_comp_games()
team_name = st.selectbox('Select a team', sorted(games['home_team'].unique()))

st.title(f'{team_name} National Team Games')
team_games = get_team_games(games, team_name)
game = st.selectbox('Select a game', team_games['game_name'].unique())
selected_game = team_games[team_games['game_name'] == game]
match_id = selected_game['match_id'].values[0]
home_team = selected_game['home_team'].values[0]
away_team = selected_game['away_team'].values[0]
df = sb.events(match_id)

with st.expander('Game State xG Data'):      
    game_state = get_gamestate(df, home_team, away_team)
    st.write(game_state)
    on = st.toggle("xG per 90", False)
    fig = plt.figure(figsize=(10, 6))
    plot_game_state(game_state, home_team, away_team, on)
    st.pyplot(fig)


with st.expander('Smallest Header Shot from Set Piece'):
    st.caption("Please note that free version of StatsBomb data does not include player height. The height is generated randomly.")
    temp = merge_shots_heights(df, match_id, home_team, away_team)
    if temp.empty:
        st.write("No set piece shots in this game")
    else:        
        smallest_player = temp.sort_values(by='player_height', ascending=True).head(1)
        st.write(f"The smallest player to head at goal from set piece was {smallest_player['player_name'].values[0]} at {smallest_player['player_height'].values[0].round(2)} cm")
        st.write(temp)
    
with st.expander('Half Space Passes'):
    set_piece = st.toggle("Include Set Piece Passes", True)
    hs_passes = filter_half_space_passes_to_penalty(df, set_piece)
    st.write(f"There were {len(hs_passes)} passes from the half space to the penalty area in this game. {len(hs_passes[hs_passes['team'] == home_team])} by {home_team} and {len(hs_passes[hs_passes['team'] == away_team])} by {away_team}. {'Including set pieces' if set_piece else 'Excluding set pieces'}")
    fig2 = plot_half_space_passes(df, home_team, away_team, set_piece)
    st.pyplot(fig2)