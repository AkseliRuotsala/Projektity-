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
def play_blackjack():
    print("Welcome to Blackjack!\n")

    deck = create_deck()
    player_hand = [deck.pop(), deck.pop()]
    dealer_hand = [deck.pop(), deck.pop()]

    # Show initial hands
    display_hand(dealer_hand, "Dealer", hide_first_card=True)
    display_hand(player_hand, "Player")

    # Player's turn
    while True:
        if calculate_hand_value(player_hand) == 21:
            print("Blackjack! Let's see what the dealer has...")
            break

        choice = input("\nDo you want to [H]it or [S]tand? ").strip().lower()
        if choice == 'h':
            player_hand.append(deck.pop())
            display_hand(player_hand, "Player")
            if calculate_hand_value(player_hand) > 21:
                print("You busted! Dealer wins.")
                return
        elif choice == 's':
            break
        else:
            print("Invalid choice. Please enter H or S.")

    # Dealer's turn
    display_hand(dealer_hand, "Dealer")
    while calculate_hand_value(dealer_hand) < 17:
        print("Dealer hits...")
        dealer_hand.append(deck.pop())
        display_hand(dealer_hand, "Dealer")

    dealer_total = calculate_hand_value(dealer_hand)
    player_total = calculate_hand_value(player_hand)

    # Determine winner
    if dealer_total > 21:
        print("Dealer busts! You win!")
    elif dealer_total > player_total:
        print("Dealer wins!")
    elif dealer_total < player_total:
        print("You win!")
    else:
        print("It's a tie (push)!")

# Run the game
if __name__ == "__main__":
    play_blackjack()
