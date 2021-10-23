# Chess Bot
 
The latest iteration of a program that can analyze or play chess games on Chess.com

## How does it work?
It uses Selenium Webdriver to login to Chess.com, scrape the move list, and play moves.

The move list is parsed from the page's HTML into a list of move strings.
These move strings are parsed into proper format to be used by the `python-chess` library.
The moves are then sent to an external chess engine process, and a list of best moves for the current position is retrieved.

Depending on the configuration, the bot will either display arrows indicating the best moves, or it will automatically play the moves.
