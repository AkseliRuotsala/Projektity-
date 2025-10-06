import random
from collections import Counter

suits = ['♠', '♥', '♦', '♣']
ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
rank_values = {r: i for i, r in zip(range(2, 15), ranks)}

# Kertoimet
payouts = {
    "One pair": 3,
    "Two pair": 4,
    "Three of a kind": 5,
    "Straight": 10,
    "Flush": 12,
    "Full house": 20,
    "Four of a kind": 30,
    "Straight flush": 50,
}

def new_deck():
    deck = []
    for s in suits:
        for r in ranks:
            deck.append((r, s))
    random.shuffle(deck)
    return deck

def pretty(hand):
    s = ''
    for r, t in hand:
        s += r + t + ' '
    return s.strip()

def choose_card(options):
    print("Choose a card:")
    i = 1
    for c in options:
        print(str(i) + ": " + c[0] + c[1])
        i += 1
    while True:
        try:
            val = int(input("Options (1 or 2): "))
            if val == 1 or val == 2:
                return options[val-1]
            else:
                print("Give 1 or 2.")
        except ValueError:
            print("Give number 1 or 2.")

def hand_rank(cards):
    """Palauttaa (arvo, nimi)"""
    values = []
    suits_in_hand = []
    for r, s in cards:
        values.append(rank_values[r])
        suits_in_hand.append(s)
    values.sort(reverse=True)
    counts = Counter(values)
    # Tehdään lista (määrä, arvo) ja järjestetään laskevaan
    counts_items = []
    for v, c in counts.items():
        counts_items.append((c, v))
    counts_items.sort(reverse=True)
    is_flush = (len(set(suits_in_hand)) == 1)

    # Straight detection
    distinct_vals = sorted(list(set(values)), reverse=True)
    is_straight = False
    top_val = None
    if len(distinct_vals) == 5:
        if distinct_vals[0] - distinct_vals[4] == 4:
            is_straight = True
            top_val = distinct_vals[0]
        if distinct_vals == [14,5,4,3,2]:
            is_straight = True
            top_val = 5

    if is_straight and is_flush:
        return (9, top_val), "Straight flush"
    if counts_items[0][0] == 4:
        return (8, counts_items[0][1]), "Four of a kind"
    if counts_items[0][0] == 3 and counts_items[1][0] == 2:
        return (7, counts_items[0][1]), "Full house"
    if is_flush:
        return (6,) + tuple(values), "Flush"
    if is_straight:
        return (5, top_val), "Straight"
    if counts_items[0][0] == 3:
        return (4, counts_items[0][1]), "Three of a kind"
    if counts_items[0][0] == 2 and counts_items[1][0] == 2:
        return (3, counts_items[0][1], counts_items[1][1]), "Two pair"
    if counts_items[0][0] == 2:
        return (2, counts_items[0][1]), "One pair"
    return (1,) + tuple(values), "High card"

def main(saldo):
    kierros=0
    while kierros<5 and saldo>0:
        games_left=4-kierros
        print(f'Your balance: {saldo}€')
        print(f'Game {kierros+1}\nGames left: {games_left}')
        try:
            panos = int(input("Choose bet: "))
            if panos < 0 or panos > saldo:
                print("Incorrect input. Please try again.")
                continue
        except ValueError:
            print("Give a number.")
            continue

        deck = new_deck()
        saldo -= panos

        # Aloitus 2 kortilla
        hand = [deck.pop(), deck.pop()]
        print("Your starting hand:", pretty(hand))

        # Nostetaan 2 uutta, valitse toinen
        print("\nTwo new cards are drawn...")
        options = [deck.pop(), deck.pop()]
        chosen = choose_card(options)
        hand.append(chosen)
        print("You chose:", chosen[0]+chosen[1])
        print("Your hand now:", pretty(hand))

        # Lopuksi nostetaan 2 korttia automaattisesti
        print("\nYou will get two more cards automatically...")
        hand.append(deck.pop())
        hand.append(deck.pop())

        print("\n--- Your final hand ---")
        print(pretty(hand))

        # Arvostellaan käsi
        rank_tuple, name = hand_rank(hand)
        print("Hand's type:", name)

        if name in payouts:
            kerroin = payouts[name]
            voitto = panos * kerroin
            saldo += voitto
            print("You won {} (multiplier {}x)!".format(voitto, kerroin))
            kierros +=1
        else:
            print("No win this time.")
            kierros +=1
        if kierros > 0:
            again = input("\nPlay again? [Y/N] ")
            if again not in ['y', 'Y']:
                print("Thanks for playing.")
                break


    if saldo<1:
        print("Game over. Your balance is 0. Thanks for playing!")
    elif kierros==5 :
        print("Game over. You have reached the maximum amount of games. Thanks for playing!")
    return saldo

if __name__ == "__main__":
    saldo = 200
    main(saldo)

