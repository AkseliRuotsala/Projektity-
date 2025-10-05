import random
from geopy import distance
import story

import blackjack
import poker

import mysql.connector


conn = mysql.connector.connect(
    host="localhost",
    port=3306,
    database="",
    user="",
    password="",
    autocommit=True
)


def get_airports():
    sql = """SELECT iso_country, ident, name, type, latitude_deg, longitude_deg
FROM airport
WHERE type='balloonport'
UNION SELECT iso_country, ident, name, type, latitude_deg, longitude_deg
FROM airport
WHERE name = "McCarran International Airport"
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

    g_ports = a_ports[1:].copy()
    random.shuffle(g_ports)

    for i, goal_id in enumerate(goal_list):
        sql = 'INSERT INTO ports (game, airport, goal) VALUES (%s, %s, %s);'
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
    print(f"Oh no! You've been robber of {stolen} €. You now have {player_money} €.")
    return player_money


def vegas_airport():
    sql = """SELECT iso_country, ident, name, type, latitude_deg, longitude_deg
FROM airport
where ident = 'KLAS';"""
    cursor = conn.cursor(dictionary=True)
    cursor.execute(sql)
    result = cursor.fetchall()
    return result


#game starts
storyDialog = input('Do you want to read the background story? (Y/N): ').upper()
if storyDialog == 'Y':
    for line in story.getStory():
        print(line)


print('When you are ready to start, ')
player = input('type player name: ')
# boolean for game over and win
game_over = False
win = False

money = 500
end_money_goal = 500000
score = 0

all_airports = get_airports()
start_airport = all_airports[0]['ident']

current_airport = start_airport

game_id = create_game(money, start_airport, player, all_airports)


while not game_over:
    airport = get_airport_info(current_airport)
    print(f'''you are at {airport['name']},''')
    print(f'''you have {money:.0f}€''')

    goal = check_goal(game_id, current_airport)
    if goal:
        if goal['goal_id'] == 1:
            poker.main(money)
        elif goal['goal_id'] == 2:
            blackjack.main(money)
        else:
            robber_event(money)

    airports = airports_in_range(current_airport, all_airports)
    print(f'choose on of {len(airports)} airports:')
    if len(airports) > 0:
        print(f'''airports''')
        for airport in airports:
            ap_distance = calculate_distance(current_airport, airport['ident'])
            print(f'''{airport['name']}, icao: {airport['ident']}, distance: {ap_distance:.0f}km''')

        dest = input('enter destination icao: ')
        selected_distance = calculate_distance(current_airport, dest)
        update_location(dest, money, game_id)
        current_airport = dest
    # if destination airport is McCarran airport and desired goal is reached, game is won
    if end_money_goal and current_airport == vegas_airport():
        game_over = True

print(f'''You have arrived at the Vegas strip with {money}€, go spend your money wisely''')
print(f'''{'end text here' if win else 'looser text'}''')

