import textwrap

story = '''
You have always dreamed of becoming rich, and finally you have found a way to achieve your dream.

Your journeys purpose is to reach Las Vegas, every gamblers dream, the Heaven on earth.

With only 500 bucks in your pocket, you  heat to the nearest airport.

Your strengths lie in just two games, blackjack and poker, and those are the only tables you’ll ever play. 

At each stop you can test your luck in up to five rounds before flying onward, but beware… 


...not every risk lies in the card…
'''

# Set column width to 80 characters
wrapper = textwrap.TextWrapper(width=3000, break_long_words=False, replace_whitespace=False)
# Wrap text
word_list = wrapper.wrap(text=story)


def getStory():
    return word_list
