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
    player_id serial primary key,
    total_score integer
);

create table match (
     player_1_id integer,
     player_2_id integer,
     winner integer,
     round integer,
     match_id serial primary key
);

