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
    database="",
    user="",
    password="",
    autocommit=True
)

def delayed_print(text, delay=0.5):
    print(text)
    time.sleep(delay)

def get_airports():
    sql = """SELECT iso_country, ident, name, type, latitude_deg, longitude_deg
FROM airport
WHERE type='balloonport'
ORDER BY RAND();"""
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

def create_game(start_money, p_range, cur_airport, p_name, a_ports):
    sql = 'INSERT INTO game (money, player_range, location, screen_name) VALUES (%s, %s, %s, %s);'
    cursor = conn.cursor(dictionary=True)
    cursor.execute(sql, (start_money, p_range, cur_airport, p_name))
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

    # Add end airport
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

def airports_in_range(icao, a_ports, p_range):
    in_range = []
    for a_port in a_ports:
        dist = calculate_distance(icao, a_port['ident'])
        if dist <= p_range and not dist == 0:
            in_range.append(a_port)
    return in_range

def update_location(icao, p_range, u_money, g_id):
    sql = f'''UPDATE game SET location = %s, player_range = %s, money = %s WHERE id = %s'''
    cursor = conn.cursor(dictionary=True)
    cursor.execute(sql, (icao, p_range, u_money, g_id))

def robber_event(player_money):
    stolen = player_money // 2
    player_money -= stolen
    delayed_print(f"Oh no! You've been robbed of {stolen}$."
          f" but luckily you stashed half of your money ({player_money}$) in your shoe.", 2)
    return player_money

def vegas_airport():
    sql = """SELECT iso_country, ident, name, type, latitude_deg, longitude_deg
FROM airport
where ident = 'KLAS';"""
    cursor = conn.cursor(dictionary=True)
    cursor.execute(sql)
    result = cursor.fetchall()
    return result

def update_player_range(money):
    return int(money * 5)


# Game starts
storyDialog = input('Do you want to read the background story? (Y/N): ').upper()
if storyDialog == 'Y':
    for line in story.getStory():
        print(line)

delayed_print('\nWhen you are ready to start, ', 1)
player = input('type player name: ')
game_over = False

money = 500
end_money_goal = 500
player_range = update_player_range(money)

GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"

all_airports = get_airports() + vegas_airport()
start_airport = all_airports[0]['ident']

current_airport = start_airport
end_airport = 'KLAS'

game_id = create_game(money, player_range, start_airport, player, all_airports)


while not game_over:
    # Check losing condition first
    if money < 100:
        print("It seems that you don't have enough money to travel anymore 😫")
        print("Use the remainder of your money to book a hotel room and sleep your sorrow away.")
        break

    # Print current location
    airport = get_airport_info(current_airport)
    delayed_print(f'You are at {airport["name"]},', 1.5)

    # Play minigame at current airport
    goal = check_goal(game_id, current_airport)
    if goal:
        if goal['goal_id'] == 1:
            print("Welcome to the poker table")
            money = poker.main(money)
        elif goal['goal_id'] == 2:
            print("Welcome to the blackjack table")
            money = blackjack.main(money)
        else:
            money = robber_event(money)
        money = round(money, 2)  # <-- keep money to 2 decimals
        player_range = update_player_range(money)

    # List airports in range
    airports = airports_in_range(current_airport, all_airports, player_range)
    print(f'\nChoose one of {len(airports)} airports:\n')
    if len(airports) == 0:
        print("No airports in range! You are stranded 😢")
        break

    delayed_print('For every 5km it costs 1$ to travel\n', 1)
    print('Airports:')
    for airport in airports:  # Only show in-range airports
        ap_distance = calculate_distance(current_airport, airport['ident'])
        delayed_print(f"{GREEN}{airport['name']} (ICAO: {airport['ident']}) — {ap_distance:.0f} km — in range{RESET}", 0.2)

    dest = input('Enter destination ICAO: ').strip().upper()
    if not any(a['ident'] == dest for a in airports):  # Validate range
        print("Invalid or out-of-range ICAO code. Try again.")
        continue

    selected_distance = calculate_distance(current_airport, dest)
    trip_cost = round(selected_distance * 0.2, 2)  # 20 cents per km
    if money >= trip_cost:
        money -= trip_cost
        money = round(money, 2)  # <-- round after subtraction
        player_range = update_player_range(money)
        delayed_print(f"You spent ${trip_cost} on travel. Remaining money: ${money}", 1)
        update_location(dest, player_range, money, game_id)
        current_airport = dest
    else:
        print("You don't have enough money to pay for the trip! Choose another airport.")
        continue

    # Check win/loss after moving
    if current_airport == end_airport:
        if money >= end_money_goal:
            print(story.getStory2())
        else:
            print("You arrived at McCarran (KLAS) but didn't reach your money goal 😢")
            print("Better luck next time!")
        game_over = True
