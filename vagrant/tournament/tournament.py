#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteMatches():
    """Remove all the match records from the database."""
    conn = connect()
    c = conn.cursor()
    c.execute("DELETE FROM match")
    conn.commit()
    conn.close()

def deletePlayers():
    """Remove all the player records from the database."""
    conn = connect()
    c = conn.cursor()
    c.execute("DELETE FROM player")
    conn.commit()
    conn.close()

def countPlayers():
    """Returns the number of players currently registered."""
    conn = connect()
    c = conn.cursor()
    c.execute("SELECT COUNT (*) as num FROM PLAYER")
    (count,) = c.fetchone()
    conn.commit()
    conn.close()

    return count


def registerPlayer(name):
    """Adds a player to the tournament database.
  
    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)
  
    Args:
      name: the player's full name (need not be unique).
    """
    conn = connect()
    c = conn.cursor()
    c.execute("INSERT into player (name) values (%s)", (name,))
    conn.commit()
    conn.close()

def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    conn = connect()
    c = conn.cursor()
    c.execute("UPDATE player SET total_score"
              " = (select count(*) from match where winner = player_id)")
    conn.commit()

    c.execute("select player_id as id, name, total_score as wins,"
              "count(match.player_1_id) as num from"
              " player left join match on player.player_id = player_1_id OR player_id = player_2_id"
              " group by name, player_id,total_score order by wins DESC")
    '''standings = ({'matches':str(row[3]),'wins':str(row[2]),'name': str(row[1]), 'id': str(row[0])}
      for row in c.fetchall())
    '''
    standings = c.fetchall()
    conn.commit()
    conn.close()
    return standings

    '''
    
tournament=> SELECT name, count (match.winner) as num from player left join match on player.player_id = match.winner group by name order by num DESC;
    
SELECT name, count(*) as match_times from match,player  where player.player_id = match.player_1_id OR player.player_id = match.player_2_id GROUP BY name;
    '''


def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
 
 
def swissPairings():
    """Returns a list of pairs of players for the next round of a match.
  
    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.
  
    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """


