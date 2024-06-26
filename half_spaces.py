from turtle import st
import pandas as pd
from mplsoccer import Pitch

def extract_coordinates(row):
    return pd.Series({'x': row[0], 'y': row[1]})

def filter_half_space_passes(df, x_range, y_range):
    return df[
        ((df['x'].between(*x_range)) & (df['y'].between(*y_range))) |
        ((df['x'].between(*x_range)) & (df['y'].between(80 - y_range[1], 80 - y_range[0])))
    ]
    
def filter_half_space_passes_to_penalty(df, set_piece = False):
    passes = df[df['type'] == 'Pass'][['team', 'location', 'pass_end_location', 'pass_outcome', 'pass_type']]
    passes['pass_outcome'].fillna('Complete', inplace=True)

    passes[['x', 'y']] = passes['location'].apply(extract_coordinates)
    passes[['end_x', 'end_y']] = passes['pass_end_location'].apply(extract_coordinates)

    half_space_penalty = filter_half_space_passes(passes, (81, 101), (18, 30))
    half_space_penalty = half_space_penalty[
        (half_space_penalty['end_x'] >= 102) &
        (half_space_penalty['end_y'].between(18, 62))]
    
    half_space_penalty['pass_type'] = half_space_penalty['pass_type'].fillna('Open Play')
    if set_piece:
        return half_space_penalty
    else:
        return half_space_penalty[half_space_penalty['pass_type'] == 'Open Play']

def plot_half_space_passes(df, home_team, away_team):   
    pitch = Pitch(pitch_type = 'statsbomb', positional=True, shade_middle=True,
              positional_color='#eadddd', shade_color='#f2f2f2')

    fig, ax = pitch.draw()

    for x in df.to_dict(orient = 'records'):
        if x['team'] == home_team:
            pitch.lines(xstart=120-x['x'], ystart=80-x['y'], xend=120-x['end_x'], yend=80-x['end_y'], lw = 5,
                        transparent = True, ax = ax, color = 'g' if x['pass_outcome'] == 'Complete' else 'r')
        else:
            pitch.lines(x['x'], x['y'], x['end_x'], x['end_y'], lw=5,
                        transparent=True, ax=ax, color = 'g' if x['pass_outcome'] == 'Complete' else 'r')
            
    ax.text(30,86, home_team, ha='center', fontsize = 16, fontfamily = 'monospace')
    ax.text(90, 86, away_team, ha='center', fontsize=16, fontfamily='monospace')
    
    return fig

    