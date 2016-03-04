Swiss Tournament Database
======================

This program tracks users and their wins in a swiss-style tournament.

INSTALL
-------------------------
To use, connect to psql and import the tournament.sql while using MYSQL by running

```sh
 \i tournament.sql
```

The "tournament" database will be created for you.


HOW TO USE
------------------------


* Register players by calling the registerPlayer function for each player. Pass in a player's first and last name, like
```sh
registerPlayer("Alex Antonov")
```



* Get pairings for each round by calling the swissPairings functions. It will return pairs of players for the next round.

* See the rankings of players and get their IDs (you'll need IDs to report wins & matches) by calling playerStandings(), and you'll get output that looks something like this:

```sh
 id | name              | wins |    matches
 11 | Twilight Sparkle  |    1 |       1
 12 | Applejack         |    1 |       1
 13 | Rarity            |    1 |       1
 14 | Princess Celestia |    1 |       1
 15 | Princess Luna     |      |       1
 16 | Fluttershy        |      |       1
 17 | Rainbow Dash      |      |       1
 19 | Pinkie Pie        |      |       1
```

* To enter a match, use the reportMatch() function, and pass in the ID of the winner first, and the loser second, like 

```sh
reportMatch(11,15)
```