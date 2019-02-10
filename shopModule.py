# shop module for TouhouCardBot.py

# TODO : Write all functions
async def refreshShop:
	# when calling a shop function, checks for if the day has changed
	# if so, refresh the shop
	# shop stock lasts for seventy two hours
	# TODO : Modify config file to add last time the shop was refreshed

async def displayShop:
	# displays all cards in the shop
	# we'll just use a simple array that stores the cards for this
	# no need to update the database - ideally we want to minimize calls to the DB

async def buyCardFromShop:
	# buys a card from the shop for a certain amount of points
	# first checks if the shop needs to be refreshed
	# if it is refreshed, then alert the user that the card shop has changed
	# if it hasn't, allow the them to buy the card if they have enough credits

	# so, from parent file:
	# run it against hasCost
	# if true, then call refreshShop
	# if refreshShop returns false, call buyShop