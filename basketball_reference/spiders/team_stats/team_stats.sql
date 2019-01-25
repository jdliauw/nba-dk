CREATE TABLE team_stats(
  collected_date DATE,
  team TEXT,
  rank INT,
  g INT,
  mp INT,
  fg INT,
  fga INT,
  fg_pct REAL,
  fg3 INT,
  fg3a INT,
  fg3_pct REAL,
  fg2 INT,
  fg2a INT,
  fg2_pct REAL,
  ft INT,
  fta INT,
  ft_pct REAL,
  orb INT,
  drb INT,
  trb INT,
  ast INT,
  stl INT,
  blk INT,
  tov INT,
  pf INT,
  pts INT
);

CREATE TABLE opp_stats(
  collected_date DATE,
  team TEXT,
  rank INT,
  g INT,
  mp INT,
  opp_fg INT,
  opp_fga INT,
  opp_fg_pct REAL,
  opp_fg3 INT,
  opp_fg3a INT,
  opp_fg3_pct REAL,
  opp_fg2 INT,
  opp_fg2a INT,
  opp_fg2_pct REAL,
  opp_ft INT,
  opp_fta INT,
  opp_ft_pct REAL,
  opp_orb INT,
  opp_drb INT,
  opp_trb INT,
  opp_ast INT,
  opp_stl INT,
  opp_blk INT,
  opp_tov INT,
  opp_pf INT,
  opp_pts INT
);

CREATE TABLE team_stats_per_possession(
  collected_date DATE,
  team TEXT,
  rank INT,
  g INT,
  mp INT,
  fg INT,
  fga INT,
  fg_pct REAL,
  fg3 INT,
  fg3a INT,
  fg3_pct REAL,
  fg2 INT,
  fg2a INT,
  fg2_pct REAL,
  ft INT,
  fta INT,
  ft_pct REAL,
  orb INT,
  drb INT,
  trb INT,
  ast INT,
  stl INT,
  blk INT,
  tov INT,
  pf INT,
  pts INT
);

CREATE TABLE opp_stats_per_possession(
  collected_date DATE,
  team TEXT,
  rank INT,
  g INT,
  mp INT,
  opp_fg INT,
  opp_fga INT,
  opp_fg_pct REAL,
  opp_fg3 INT,
  opp_fg3a INT,
  opp_fg3_pct REAL,
  opp_fg2 INT,
  opp_fg2a INT,
  opp_fg2_pct REAL,
  opp_ft INT,
  opp_fta INT,
  opp_ft_pct REAL,
  opp_orb INT,
  opp_drb INT,
  opp_trb INT,
  opp_ast INT,
  opp_stl INT,
  opp_blk INT,
  opp_tov INT,
  opp_pf INT,
  opp_pts INT
);