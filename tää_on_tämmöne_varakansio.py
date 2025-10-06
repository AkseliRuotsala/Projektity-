import random
from geopy import distance
import story

import blackjack
import poker
import time


import mysql.connector


conn = mysql.connector.connect(
    host="localhost",
    port=3306,
    database="demoboy",
    user="demo",
    password="peli",
    autocommit=True
)


def delayed_print(text, delay = 0.5):
    print(text)
    time.sleep(delay)



def get_airports():
    sql = """SELECT iso_country, ident, name, type, latitude_deg, longitude_deg
FROM airport
WHERE type='balloonport'
ORDER BY RAND();"""
# UNION SELECT iso_country, ident, name, type, latitude_deg, longitude_deg
# FROM airport
# WHERE name = "McCarran International Airport"
    cursor = conn.cursor(dictionary=True)
    cursor.execute(sql)
    result = cursor.fetchall()
    return result


def vegas_airport():
    sql = """SELECT iso_country, ident, name, type, latitude_deg, longitude_deg
FROM airport
where ident = 'KLAS';"""
    cursor = conn.cursor(dictionary=True)
    cursor.execute(sql)
    result = cursor.fetchall()
    return result


def get_goals():
    sql = 'SELECT * FROM goal;'
    cursor = conn.cursor(dictionary=True)
    cursor.execute(sql)
    result = cursor.fetchall()
    return result


def create_game(start_money, cur_airport, p_name, a_ports):
    sql = 'INSERT INTO game (money, location, screen_name) VALUES (%s, %s, %s);'
    cursor = conn.cursor(dictionary=True)
    cursor.execute(sql, (start_money, cur_airport, p_name))
    g_id = cursor.lastrowid

    goals = get_goals()
    goal_list = []
    for goal in goals:
        for i in range(0, goal['probability'], 1):
            goal_list.append(goal['id'])

    g_ports = a_ports[0:].copy()
    random.shuffle(g_ports)

    for i, goal_id in enumerate(goal_list):
        sql = 'INSERT INTO ports (game, airport, goal) VALUES (%s, %s, %s);'
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, (g_id, g_ports[i]['ident'], goal_id))

    # lisätään pelin päätepysäkki
    sql = 'INSERT INTO ports (game, airport, goal) VALUES (%s, %s, %s);'
    cursor = conn.cursor(dictionary=True)
    cursor.execute(sql, (g_id, 'KLAS', 0))

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
    sql = f'''SELECT ports.id, goal, goal.id as goal_id, name 
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


def airports_in_range(icao, a_ports):
    in_range = []
    for a_port in a_ports:
        dist = calculate_distance(icao, a_port['ident'])
        if not dist == 0:
            in_range.append(a_port)
    return in_range


def update_location(icao, u_money, g_id):
    sql = f'''UPDATE game SET location = %s, money = %s WHERE id = %s'''
    cursor = conn.cursor(dictionary=True)
    cursor.execute(sql, (icao, u_money, g_id))


def robber_event(player_money):
    stolen = player_money // 2
    player_money -= stolen
    delayed_print(f"Oh no! You've been robber of {stolen}$."
          f" but luckily you stashed half of your money ({player_money}$) in your shoe.", 2)
    return player_money


#game starts
storyDialog = input('Do you want to read the background story? (Y/N): ').upper()
if storyDialog == 'Y':
    for line in story.getStory():
        delayed_print(line, 1.5)


delayed_print('\nWhen you are ready to start, ', 1)
player = input('type player name: ')
# boolean for game over and win
game_over = False
win = False

money = 500
end_money_goal = 100000

all_airports = get_airports()
start_airport = all_airports[0]['ident']

current_airport = start_airport
print(current_airport)
end_airport = 'KLAS'

game_id = create_game(money, start_airport, player, all_airports)


while not game_over:
    airport = get_airport_info(current_airport)
    delayed_print(f'''you are at {airport['name']},''', 1.5)

    goal = check_goal(game_id, current_airport)
    if goal:
        if goal['goal_id'] == 1:
            money = poker.main(money)
        elif goal['goal_id'] == 2:
            money = blackjack.main(money)
        else:
            money = robber_event(money)

    if money < 100:
        print("It seems that you don't have enough money to travel anymore😫 use the remainder of "
              "our money\n to book a hotel room where you can sleep your sorrow away. Better luck next time")
        break
    airports = airports_in_range(current_airport, all_airports)
    delayed_print(f'choose one of {len(airports)} airports:', 1)
    if len(airports) > 0:
        print(f'''airports''')
        for airport in airports:
            ap_distance = calculate_distance(current_airport, airport['ident'])
            delayed_print(f'''{airport['name']}, icao: {airport['ident']}, distance: {ap_distance:.0f}km''', 0.5)

        dest = input('enter destination icao: ')
        selected_distance = calculate_distance(current_airport, dest)
        update_location(dest, money, game_id)
        current_airport = dest
    # if destination airport is McCarran airport and desired goal is reached, game is won
    if end_money_goal and current_airport == end_airport:
        game_over = True
        print(story.getStory2())
