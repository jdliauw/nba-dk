CREATE TABLE games(
  season INT,
  game_date DATE NOT NULL,
  pid TEXT NOT NULL,
  starter BOOLEAN,
  team TEXT,
  home TEXT,
  opp TEXT,
  home_score INT,
  away_score INT,
  play_time_raw TEXT,
  mp INT,
  sp INT,
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
  plus_minus INT,
  ts_pct REAL,
  efg_pct REAL,
  fg3a_per_fga_pct REAL,
  fta_per_fga_pct REAL,
  orb_pct REAL,
  drb_pct REAL,
  trb_pct REAL,
  ast_pct REAL,
  stl_pct REAL,
  blk_pct REAL,
  tov_pct REAL,
  usg_pct REAL,
  off_rtg INT,
  def_rtg INT,
  reason TEXT,
  PRIMARY KEY (game_date, pid),
  FOREIGN KEY (pid) REFERENCES player_info (pid)
);

CREATE TABLE pbp
(
  id SERIAL NOT NULL,
  season INT,
  game_date DATE NOT NULL,
  home TEXT,
  away TEXT,
  assister TEXT,
  away_score INT,
  blocker TEXT,
  drebounder TEXT,
  distance INT,
  ejected TEXT,
  fg_type INT,
  foul_drawer TEXT,
  foul_type TEXT,
  fouler TEXT,
  full_timeout TEXT,
  home_score INT,
  make bool,
  orebounder TEXT,
  play TEXT,
  play_time REAL NOT NULL,
  play_time_raw TEXT NOT NULL,
  quarter INT,
  shooter TEXT,
  steal TEXT,
  sub_in TEXT,
  sub_out TEXT,
  team_violation TEXT,
  tech_type TEXT,
  ts_timeout TEXT,
  turnover TEXT,
  turnover_type TEXT,
  violation TEXT,
  PRIMARY KEY (id, game_date),
  FOREIGN KEY (assister) REFERENCES player_info (pid),
  FOREIGN KEY (blocker) REFERENCES player_info (pid),
  FOREIGN KEY (shooter) REFERENCES player_info (pid),
  FOREIGN KEY (sub_in) REFERENCES player_info (pid),
  FOREIGN KEY (sub_out) REFERENCES player_info (pid)
);

CREATE TABLE college_stats
(
  pid TEXT NOT NULL,
  season INT,
  college TEXT NOT NULL,
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
  PRIMARY KEY (pid, season, college),
  FOREIGN KEY (pid) REFERENCES player_info (pid)
);

CREATE TABLE player_info
(
  pid TEXT PRIMARY KEY NOT NULL,
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
  position TEXT,
  hs_city TEXT,
  hs_state TEXT,
  pick INT,
  draft_year INT
);

CREATE TABLE player_shooting_stats
(
  season INT NOT NULL,
  pid TEXT NOT NULL,
  collected_date DATE NOT NULL,
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
  PRIMARY KEY(pid, season, collected_date),
  FOREIGN KEY (pid) REFERENCES player_info (pid)
);

CREATE TABLE contracts
(
  pid TEXT NOT NULL,
  team TEXT NOT NULL,
  contracts TEXT NOT NULL,
  collected_date DATE NOT NULL,
  PRIMARY KEY(pid, team, collected_date),
  FOREIGN KEY (pid) REFERENCES player_info (pid)
);

/* salaries may include team/player options so they are not guaranteed */
CREATE TABLE salaries
(
  pid TEXT NOT NULL,
  season INT NOT NULL,
  team TEXT NOT NULL,
  salary INT,
  collected_date DATE NOT NULL,
  PRIMARY KEY(pid, season, team),
  FOREIGN KEY (pid) REFERENCES player_info (pid)
);

CREATE TABLE misc_stats
(
  collected_date DATE NOT NULL,
  season INT,
  team TEXT NOT NULL,
  age REAL,
  wins INT,
  losses INT,
  wins_pyth INT,
  losses_pyth INT,
  mov REAL,
  sos REAL,
  srs REAL,
  off_rtg REAL,
  def_rtg REAL,
  net_rtg REAL,
  pace REAL,
  fta_per_fga_pct REAL,
  fg3a_per_fga_pct REAL,
  ts_pct REAL,
  efg_pct REAL,
  tov_pct REAL,
  orb_pct REAL,
  ft_rate REAL,
  opp_efg_pct REAL,
  opp_tov_pct REAL,
  drb_pct REAL,
  opp_ft_rate REAL,
  arena_name TEXT,
  attendance INT,
  attendance_per_g INT,
  PRIMARY KEY (collected_date, team, season),
  FOREIGN KEY (pid) REFERENCES player_info (pid)
);

CREATE TABLE team_shooting_stats
(
  collected_date DATE NOT NULL,
  season INT,
  team TEXT NOT NULL,
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
  pct_fg2_layup REAL,
  fg2_layup INT,
  fg3_pct_ast REAL,
  pct_fg3a_corner REAL,
  fg3_pct_corner REAL,
  fg3a_heave INT,
  fg3_heave INT,
  opp_mp INT,
  opp_fg_pct REAL,
  opp_avg_dist REAL,
  opp_fg2a_pct_fga REAL,
  opp_pct_fga_00_03 REAL,
  opp_pct_fga_03_10 REAL,
  opp_pct_fga_10_16 REAL,
  opp_pct_fga_16_xx REAL,
  opp_fg3a_pct_fga REAL,
  opp_fg2_pct REAL,
  opp_fg_pct_00_03 REAL,
  opp_fg_pct_03_10 REAL,
  opp_fg_pct_10_16 REAL,
  opp_fg_pct_16_xx REAL,
  opp_fg3_pct REAL,
  opp_fg2_pct_ast REAL,
  opp_pct_fg2_dunk REAL,
  opp_fg2_dunk INT,
  opp_pct_fg2_layup REAL,
  opp_fg2_layup INT,
  opp_fg3_pct_ast REAL,
  opp_pct_fg3a_corner REAL,
  opp_fg3_pct_corner REAL,
  PRIMARY KEY (collected_date, team, season)
);

CREATE TABLE standings
(
  collected_date DATE NOT NULL,
  season INT,
  team TEXT,
  conference TEXT,
  seed INT,
  wins INT,
  losses INT,
  win_loss_pct REAL,
  gb INT,
  pts_per_g REAL,
  opp_pts_per_g REAL,
  srs REAL,
  PRIMARY KEY (collected_date, team, season)
);

CREATE TABLE team_stats
(
  collected_date DATE NOT NULL,
  team TEXT NOT NULL,
  season INT,
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
  pts INT,
  opp_rank INT,
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
  opp_pts INT,
  PRIMARY KEY (collected_date, team, season)
);

CREATE TABLE team_stats_per_100
(
  collected_date DATE NOT NULL,
  team TEXT NOT NULL,
  season INT,
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
  pts INT,
  opp_rank INT,
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
  opp_pts INT,
  PRIMARY KEY (collected_date, team, season)
);

create or replace function espn() returns trigger as
$func$
begin
 new.espn = new.pts + new.trb + (1.4*new.ast) + new.stl + (1.4*new.blk) - (.7*new.tov) + new.fg + (.5*new.fg) - (.8*(new.fga-new.fg)) + (.25*new.ft) - (.8*(new.fta-new.ft));
 return new;
end;
$func$ language plpgsql;

create trigger espn before insert or update on games 
for each row execute procedure espn();