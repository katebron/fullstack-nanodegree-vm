-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.
CREATE DATABASE tournament;

create table player (
    name text,
    player_id serial primary key
);

create table match (
     player_1_id integer REFERENCES player (player_id),
     player_2_id integer REFERENCES player (player_id),
     winner integer REFERENCES player (player_id),
     round integer,
     match_id serial primary key
);

