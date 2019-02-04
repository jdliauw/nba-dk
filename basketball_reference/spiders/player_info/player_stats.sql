CREATE TABLE college_stats
(
  pid TEXT NOT NULL,     /* PRIMARY */
  year INT,              /* PRIMARY */
  college TEXT NOT NULL, /* PRIMARY */
  age INT,
  g INT,
  mp INT,
  fg INT,
  fga INT,
  fg3 INT,
  fg3a INT,
  ft INT,
  fta INT,
  orb INT,
  trb INT,
  ast INT,
  stl INT,
  blk INT,
  tov INT,
  pf INT,
  pts INT,
  fg_pct REAL,
  fg3_pct REAL,
  ft_pct REAL,
  mp_per_g REAL,
  pts_per_g REAL,
  trb_per_g REAL,
  ast_per_g REAL,
  PRIMARY KEY (pid, year, college)
);

CREATE TABLE game_logs(
  pid TEXT NOT NULL,       /* PRIMARY */
  game_date DATE NOT NULL, /* PRIMARY */
  playoffs BOOLEAN NOT NULL,
  game_season INT NOT NULL,
  season INT NOT NULL,
  age_years INT,
  age_days INT,
  team_id TEXT NOT NULL,
  opp_id TEXT NOT NULL,
  won BOOLEAN,
  margin INT,
  starter BOOLEAN,
  minutes_played INT,
  seconds_played INT,
  fg INT,
  fga INT,
  fg_pct REAL,
  fg3 INT,
  fg3a INT,
  fg3_pct REAL,
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
  pts INT,
  game_score REAL,
  plus_minus INT,
  reason TEXT,
  PRIMARY KEY (pid, game_date)
);

CREATE TABLE player_info
(
  pid TEXT PRIMARY KEY NOT NULL, /* PRIMARY */
  first_name TEXT NOT NULL,
  last_name TEXT,
  feet INT,
  inches INT,
  lbs INT,
  birth_year INT,
  birth_month INT,
  birth_day INT,
  birth_city TEXT,
  birth_state TEXT,
  twitter TEXT,
  shoots TEXT,
  position INT,
  hs_city TEXT,
  hs_state TEXT,
  pick INT,
  draft_year INT
);

CREATE TABLE player_shooting_stats(
  season INT NOT NULL, /* PRIMARY KEY */
  pid TEXT NOT NULL,   /* PRIMARY KEY */
  age INT,
  team_id TEXT,
  lg_id TEXT,
  pos TEXT,
  g INT,
  mp INT,
  fg_pct REAL,
  avg_dist REAL,
  fg2a_pct_fga REAL,
  pct_fga_00_03 REAL,
  pct_fga_03_10 REAL,
  pct_fga_10_16 REAL,
  pct_fga_16_xx REAL,
  fg3a_pct_fga REAL,
  fg2_pct REAL,
  fg_pct_00_03 REAL,
  fg_pct_03_10 REAL,
  fg_pct_10_16 REAL,
  fg_pct_16_xx REAL,
  fg3_pct REAL,
  fg2_pct_ast REAL,
  pct_fg2_dunk REAL,
  fg2_dunk INT,
  fg3_pct_ast REAL,
  pct_fg3a_corner REAL,
  fg3_pct_corner REAL,
  fg3a_heave INT,
  fg3_heave INT,
  PRIMARY KEY(pid, game_date)
);