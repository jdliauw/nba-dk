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

{
  "team-stats-base": [
    {
      "team": string,
      "rank": int,
      "g": int,
      "mp": int,
      "fg": int,
      "fga": int,
      "fg_pct": float,
      "fg3": int,
      "fg3a": int,
      "fg3_pct": float,
      "fg2": int,
      "fg2a": int,
      "fg2_pct": float,
      "ft": int,
      "fta": int,
      "ft_pct": float,
      "orb": int,
      "drb": int,
      "trb": int,
      "ast": int,
      "stl": int,
      "blk": int,
      "tov": int,
      "pf": int,
      "pts": int
    }
  ],
  "opponent-stats-base": [
    {
      "team": string,
      "rank": int,
      "g": int,
      "mp": int,
      "opp_fg": int,
      "opp_fga": int,
      "opp_fg_pct": float,
      "opp_fg3": int,
      "opp_fg3a": int,
      "opp_fg3_pct": float,
      "opp_fg2": int,
      "opp_fg2a": int,
      "opp_fg2_pct": float,
      "opp_ft": int,
      "opp_fta": int,
      "opp_ft_pct": float,
      "opp_orb": int,
      "opp_drb": int,
      "opp_trb": int,
      "opp_ast": int,
      "opp_stl": int,
      "opp_blk": int,
      "opp_tov": int,
      "opp_pf": int,
      "opp_pts": int
    }
  ],
  "team-stats-per_poss": [
    {
      "team": string,
      "rank" int,
      "g": int,
      "mp": int,
      "fg": float,
      "fga": float,
      "fg_pct": float,
      "fg3": float,
      "fg3a": float,
      "fg3_pct": float,
      "fg2": float,
      "fg2a": float,
      "fg2_pct": float,
      "ft": float,
      "fta": float,
      "ft_pct": float,
      "orb": float,
      "drb": float,
      "trb": float,
      "ast": float,
      "stl": float,
      "blk": float,
      "tov": float,
      "pf": float,
      "pts": float,
    }
  ],
  "opponent-stats-per_poss": [
    {
      "team": string,
      "rank": int,
      "g": int,
      "mp": int,
      "opp_fg": float,
      "opp_fga": float,
      "opp_fg_pct": float,
      "opp_fg3": float,
      "opp_fg3a": float,
      "opp_fg3_pct": float,
      "opp_fg2": float,
      "opp_fg2a": float,
      "opp_fg2_pct": float,
      "opp_ft": float,
      "opp_fta": float,
      "opp_ft_pct": float,
      "opp_orb": float,
      "opp_drb": float,
      "opp_trb": float,
      "opp_ast": float,
      "opp_stl": float,
      "opp_blk": float,
      "opp_tov": float,
      "opp_pf": float,
      "opp_pts": float,
    }
  ]
}