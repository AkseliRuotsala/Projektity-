import textwrap

story = '''
You have always dreamed of becoming rich, and finally you have found a way to achieve your dream.

Your journeys purpose is to reach Las Vegas (ICAO = KLAS), every gamblers dream, the Heaven on earth.

With only 500 bucks in your pocket, you head to the nearest airport with a goal of 100,000$.

Your strengths lie in just two games, blackjack and poker, and those are the only tables you’ll ever play. 

At each stop you can test your luck in up to five rounds before flying onward, but beware… 


...not every risk lies in the card…
'''

story2= '''
Finally! You have reached your goal, Las Vegas! 
With the 100 thousand dollars you could do anything here, buy a cool car, eat well, invest the money, or gamble more.
The choice is yours, only the sky is the limit at this point. 
'''


# Set column width to 80 characters
wrapper = textwrap.TextWrapper(width=150, break_long_words=False, replace_whitespace=False)
# Wrap text
word_list = wrapper.wrap(text=story)


def getStory():
    return word_list

# Set column width to 80 characters
wrapper = textwrap.TextWrapper(width=150, break_long_words=False, replace_whitespace=False)
# Wrap text
word_list2 = wrapper.wrap(text=story2)


def getStory2():
    return "\n".join(word_list2)