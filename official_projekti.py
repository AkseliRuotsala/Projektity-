import random

import mysql.connector
from geopy.distance import distance

import blackjack
import poker

conn = mysql.connector.connect(
    host='localhost',
    port=3306,
    database='demoboy',
    user='demo',
    password='peli',
    autocommit=True
)

def get_airports():
    sql = """select iso_country, ident, name, latitude_deg, longitude_deg 
from airport
where type = 'balloonport'
group by RAND()
"""
    cursor = conn.cursor(dictionary=True)
    cursor.execute(sql)
    result = cursor.fetchall()
    return result


def get_goals():
    sql = "SELECT * FROM goals;"
    cursor = conn.cursor(dictionary=True)
    cursor.execute(sql)
    result = cursor.fetchall()
    return result


def create_game(start_money, cur_airport, p_name, a_ports):
    sql = "INSERT INTO game (money, location, screen_name) VALUES (%s, %s, %s);)"
    cursor = conn.cursor(dictionary=True)
    cursor.execute(sql, (start_money, cur_airport, p_name))
    g_id = cursor.lastrowidf

    goals = get_goals()
    goal_list = []
    for goal in goals:
        for i in range(0, goal['probability'], 1):
            goal_list.append(goal['id'])

    g_ports = a_ports[1:].copy()
    random.shuffle(g_ports)

    for i, goal_id in enumerate(goal_list):
        sql = "INSERT INTO ports (game, airport, goal) VALUES (%s, %s, %s);"
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, (g_id, g_ports[i]['ident'], goal_id))

    return g_id

def get_airport_info(icao):
    sql = f'''SELECT iso_country, ident, name, latitude_deg, longitude_deg
    FROM airport
    WHERE ident = %s'''
    cursor = conn.cursor(dictionary=True)
    cursor.execute(sql, (icao,))
    result = cursor.fetchone()
    return result


def check_goal(g_id, cur_airport):
    sql = f'''SELECT ports.id, goal, goal.id as goal_id, name, money 
    FROM ports 
    JOIN goal ON goal.id = ports.goal 
    WHERE game = %s 
    AND airport = %s'''
    cursor = conn.cursor(dictionary=True)
    cursor.execute(sql, (g_id, cur_airport))
    result = cursor.fetchone()
    return result


def calculate_distance(current, target):
    start = get_airport_info(current)
    end = get_airport_info(target)
    return distance.distance((start['latitude_deg'], start['longitude_deg']),
                             (end['latitude_deg'], end['longitude_deg'])).km


# keep track of total distance traveled
total_distance = 0
player_money = 500

def travel_to_airport(current_airport, next_airport):
    global total_distance, player_money
    # calculate distance between airports
    dist = calculate_distance(current_airport['ident'], next_airport['ident'])
    total_distance += dist
    player_money -= 50
    return dist

def robber_event(player_money):
    stolen = player_money // 2   # always steals half
    player_money -= stolen
    print(f"Oh no! You've been robber of {stolen} €. You now have {player_money} €.")
    return player_money

def set_stake(game_id, stake):
    cursor = conn.cursor()
    cursor.execute("UPDATE goal SET money = %s WHERE id = %s", (stake, game_id))
    conn.commit()

def start_poker_game(stake, player_money):
    print("Starting Poker...")
    player_money = poker.play(stake, player_money)
    return player_money

def start_blackjack_game(stake, player_money):
    print("Starting Blackjack...")
    player_money = blackjack.play(stake, player_money)
    return player_money


def play_game(goal_id, player_money):
    if goal_id == 1:  # Poker
        stake = int(input("Enter your poker bet: "))
        set_stake(1, stake)
        print(f"You set a bet of {stake} €.")
        player_money = poker.start_poker_game(stake, player_money)
        return player_money

    elif goal_id == 2:  # Blackjack
        stake = int(input("Enter your blackjack stake: "))
        set_stake(2, stake)
        print(f"You set a blackjack stake of {stake} €.")
        player_money = blackjack.start_blackjack_game(stake, player_money)
        return player_money

    elif goal_id == 3:  # Robber
        player_money = robber_event(player_money)
        set_stake(3, player_money)
        return player_money

    else:
        print("Unknown game/goal")
        return player_money

