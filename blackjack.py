import random
import time



# Define card values
suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace']
values = {
    '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7,
    '8': 8, '9': 9, '10': 10,
    'Jack': 10, 'Queen': 10, 'King': 10, 'Ace': 11
}

# Create and shuffle deck
def create_deck():
    deck = [(rank, suit) for rank in ranks for suit in suits]
    random.shuffle(deck)
    return deck

# Calculate hand value
def calculate_hand_value(hand):
    value = sum(values[card[0]] for card in hand)
    # Adjust for Aces
    aces = sum(1 for card in hand if card[0] == 'Ace')
    while value > 21 and aces:
        value -= 10
        aces -= 1
    return value

# Display hand
def display_hand(hand, owner, hide_first_card=False):
    print(f"\n{owner}'s hand:")
    if hide_first_card:
        print("  <Hidden card>")
        for card in hand[1:]:
            print(f"  {card[0]} of {card[1]}")
    else:
        for card in hand:
            print(f"  {card[0]} of {card[1]}")
        print(f"Total value: {calculate_hand_value(hand)}")

# Game logic
def play_blackjack(balance):
    print("Welcome to Blackjack!\n")
    print(f"Your current balance: ${balance}")
# Asking bet
    while True:
        try:
            bet = int(input("Enter your bet: $"))
            if bet <= 0:
                print("Bet more than zero.")
            elif bet > balance:
                print("You don't have enough money.")
            else:
                break
        except ValueError:
            print("Invalid input.")

    deck = create_deck()
    player_hand = [deck.pop(), deck.pop()]
    dealer_hand = [deck.pop(), deck.pop()]

    # Show initial hands
    time.sleep(1)
    display_hand(dealer_hand, "Dealer", hide_first_card=True)
    display_hand(player_hand, "Player")

    player_blackjack = calculate_hand_value(player_hand) == 21

    # Player's turn
    while not player_blackjack:
        choice = input("\nDo you want to [H]it or [S]tand? ").strip().lower()
        if choice in ['h', 'hit']:
            print("You chose to hit...")
            time.sleep(1)
            player_hand.append(deck.pop())
            display_hand(player_hand, "Player")
            if calculate_hand_value(player_hand) > 21:
                print("You busted! Dealer wins.")
                return balance - bet
        elif choice in ['s', 'stand']:
            break
        else:
            print("Invalid input.")


    # Dealer's turn
    print("\nDealer reveals their hand:")
    time.sleep(1)
    display_hand(dealer_hand, "Dealer")
    while calculate_hand_value(dealer_hand) < 17:
        print("Dealer hits...")
        time.sleep(1)
        dealer_hand.append(deck.pop())
        display_hand(dealer_hand, "Dealer")
        time.sleep(1)

    dealer_total = calculate_hand_value(dealer_hand)
    player_total = calculate_hand_value(player_hand)

    # Determine winner
    print("\nFinal Result:")
    time.sleep(1)
    if player_blackjack:
        if dealer_total == 21 and len(dealer_hand) == 2:
            print("Both you and the dealer have Blackjack! Its a tie.")
            return balance
        else:
            winnings = int(bet * 1.5)
            print("Blackjack! You win 2.5x your bet!")
            return balance + winnings
    elif player_total > 21:
        print("You busted. You lose.")
        return balance - bet
    elif dealer_total > 21:
        print("Dealer busted. You win.")
        return balance + bet
    elif dealer_total > player_total:
        print("Dealer wins.")
        return balance - bet
    elif dealer_total < player_total:
        print("You win.")
        return balance + bet
    else:
        print("It's a tie.(push)")
        return balance

# Game loop + Play time
def main(balance):
    plays = 0

    while balance > 0 and plays < 5:
        games_left = 4 - plays
        print(f"\nGame {plays + 1} - {games_left} games left")

        balance = play_blackjack(balance)
        plays += 1

        print(f"\nYour new balance is ${balance}")

        if balance <= 0:
            print("You're out of money! Game over.")
            break

        if plays < 5:
            again = input("\nPlay again? [Y/N] ").strip().lower()
            if again not in ['y', 'Y']:
                print("Thanks for playing.")
                break
    else:
        print("\nYou've reached the maximum number of games. Thanks for playing.")



# Run the game
if __name__ == "__main__":
    balance = 1000
    main(balance)

