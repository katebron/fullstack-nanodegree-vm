#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2
import db



'''def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    conn = db.DB()
    return conn
'''
def deleteMatches():
    """Remove all the match records from the database."""
    db.DB().execute("DELETE FROM match", True)

def deletePlayers():
    """Remove all the player records from the database."""
    db.DB().execute("DELETE FROM player", True)

def countPlayers():
    """Returns the number of players currently registered."""
    conn = db.DB().execute("SELECT count(*) FROM player")
    cursor = conn["cursor"].fetchone()
    conn['conn'].close()
    return cursor[0]


def registerPlayer(name):
    """Adds a player to the tournament database.
  
    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)
  
    Args:
      name: the player's full name (need not be unique).
      Using $$ to escape single-quote error 
      http://stackoverflow.com/questions/12316953/insert-varchar-with-single-quotes-in-postgresql
    """
    query = "INSERT into player (name) values ($$%s$$)" % (name,)
    #db.DB().execute(query, True)
    db.DB().execute(query, True)


def updateStandings():
    '''Creates a view of player standings that can be referred to 
       throughout the match.'''

    query = ("CREATE OR REPLACE VIEW standings as SELECT "
    " player.player_id as id, player.name, wins.wins, "
    "matches.matches FROM player LEFT JOIN matches on "
    "player.player_id = matches.player_id LEFT JOIN wins ON "
    "matches.player_id = wins.player_id ORDER BY wins.wins")
    db.DB().execute(query, True)     


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
    """Create a view that shows player_id and wins"""
    db.DB().execute("CREATE or REPLACE VIEW wins AS select player_id,"
                    "COUNT(player_id = winner) as wins FROM"
                    " player JOIN match on player_id = winner"
                    " GROUP BY player_id", True)

    """Create a view that shows player_id and matches"""
    db.DB().execute("CREATE or REPLACE VIEW matches as select player_id,"
                    " COUNT(player_id = player_1_id OR player_id = player_2_id)"
                    " as matches FROM player JOIN match on "
                    "player_id = player_1_id OR player_id = player_2_id"
                    " GROUP BY player_id", True)


    """Retrieve player name and matches and wins from a left joining player to matches and matches to wins"""
 
    updateStandings()

    conn = db.DB().execute("SELECT * from standings")

    #standings = c.fetchall()
    cursor = conn["cursor"].fetchall()
    conn['conn'].close()
    return cursor
    #return standings

def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    query = "INSERT into match (player_1_id, player_2_id, winner) values (%s, %s, %s)" % (winner, loser, winner,)
    db.DB().execute(query, True)
    
 
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
    
    '''Update the view standings'''
    updateStandings()

    '''Make a new view to put a rank on each player
       based on their current standing
    '''
    db.DB().execute("CREATE OR REPLACE VIEW rank as SELECT *,"
               "row_number() OVER(ORDER BY wins ASC)"
               "as row FROM standings", True)  

    '''Join the view to itself and select out even and 
       odd standing winners to get them in pairs
    '''
    conn = db.DB().execute("select o.id as id1, o.name as name1,"
              " e.id as id2, e.name as name2 from"
              " rank e JOIN"
              " (select * from rank WHERE MOD(row,2) = 1) o ON"
              " e.row = o.row + 1")
    
    cursor = conn["cursor"].fetchall()
    conn['conn'].close()
    return cursor
