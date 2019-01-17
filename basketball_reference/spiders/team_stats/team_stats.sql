CREATE TABLE team_stats(
    date ,
    team
    rank
    mp
    fg
    fga
    fg_pct
    fg3
    fg3a
    fg3_pct
    fg2
    fg2a
    fg2_pct
    ft
    fta
    ft_pct
    orb
    drb
    trb
    ast
    stl
    blk
    tov
    pf
    pts

    playerid TEXT NOT NULL,
    season INT NOT NULL,
    date TEXT,
    year INT,
    month INT,
    day INT,
    weekday TEXT,
    age_years INT,
    age_days INT,
    home BOOLEAN,
    team TEXT,
    opponent TEXT,
    game_started BOOLEAN,
    seconds_played INT,
    field_goals_made INT,
    field_goals_attempted INT,
    field_goals_percentage REAL,
    threes_made INT,
    threes_attempted INT,
    threes_percentage REAL,
    free_throws_made INT, 
    free_throws_attempted INT, 
    free_throws_percentage REAL,
    offensive_rebounds INT,
    defensive_rebounds INT,
    total_rebounds INT,
    assists INT,
    steals INT,
    blocks INT,
    turnovers INT, 
    personal_fouls INT,
    points INT,
    game_score REAL,
    plus_minus REAL
);