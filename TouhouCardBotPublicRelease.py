# here we go, bot time
import discord
import asyncio
import random
import ctypes
import io
#from discord import opus
#import time
from time import gmtime, strftime
import time
from datetime import datetime

import mysql
import mysql.connector

client = discord.Client()

db = mysql.connector.connect(user='[user]', password='[database password]', host='localhost', database = 'touhoucards')

@client.event
@asyncio.coroutine
def on_message(message):
	author = message.author
	messageServer = message.server
	if messageServer.id == '[serverID]':  # this is to limit where the bot can go, you put your own server ID here
		# 1/1000 chance to get a card
		queryString = "SELECT * FROM userlist WHERE user = " + author.id
		print(queryString + "\n")
		cursor = db.cursor()
		cursor.execute(queryString)
		curUser = cursor.fetchone()
		#opLeaderName = str(topLeader[0])
		print("Checking to see if you are in the database.\n")
		if(curUser == None): # need to insert
			now = datetime.now()
			#timeToList = time.strftime("%Y-%m-%d %H:%M:%S")
			timeToList = now.strftime("%Y-%m-%d %H:%M:%S")
			#timeToList = datetime.now()
			queryString = "INSERT INTO userlist VALUES(\'%s\', 500, \'%s\')" % (author.id, timeToList)
			print(queryString + '\n')
			cursor = db.cursor()
			cursor.execute(queryString)
			#curUser = cursor.fetchone()
			print("Added user.\n")
			db.commit()
		# if not there, then do nothing

		print("You are now in or were already in the database.\n")
		# now we do the check
		# nope no timing's yet
		# because have to do research into converting between datetime
		queryString = "SELECT lastrolled FROM userlist WHERE user = %s" % (author.id)
		cursor = db.cursor() # yeah I can probably get away without doing this but copy paste
		cursor.execute(queryString)
		lastTimeRolled = cursor.fetchone() # so it will have been made by now
		# we have the mython date time object now
		#curTime = time.strftime("%Y-%m-%d %H:%M:%S")
		#lastTimeRolledConverted = datetime.strptime(lastTimeRolled[0], "%Y-%m-%d %H:%M:%S")
		lastTimeRolledConverted = lastTimeRolled[0]
		rightNow = datetime.now()
		print("Last rolled date: %s\n" % (lastTimeRolledConverted))
		print("Now: %s\n" % (rightNow))
		difference = abs((rightNow - lastTimeRolledConverted))
		print("Difference in Seconds: %s" % (difference.total_seconds()))

		if(difference.total_seconds() >= 120):
			print("I can roll.\n")
			print("Updating time.\n")
			timeToList = rightNow.strftime("%Y-%m-%d %H:%M:%S")
			queryString = "UPDATE userlist SET lastrolled = \'%s\' WHERE user = %s" % (timeToList, author.id)
			cursor = db.cursor()
			cursor.execute(queryString)
			#lastTimeRolled = cursor.fetchone()
			db.commit()


			getCard = random.randint(1, 1000)

			if(getCard==1000): # you get a random card
				getCardNamesCount = "SELECT COUNT(*) FROM (SELECT name FROM cardcatalogue)"
				cursor = db.cursor()
				cursor.execute(getCardNamesCount)
				cardTypesResult = cursor.fetchone()
				totalCardTypes = cardTypesResult[0]

				cardNameRolled = random.randint(1, totalCardTypes)

				if(cardNameRolled==1): # Alice
					# NOW YOU GACHA AGAIN FOR RARITY
					rarityGet = random.randint(1,5)
					getTotalOfNamed = "SELECT COUNT(*) FROM cardcatalogue WHERE rarity = %s AND name = 'Alice'" % (rarityGet)
					cursor = db.cursor()
					cursor.execute(getTotalOfNamed)
					getTotalOfNamedResult = cursor.fetchone()
					maxNumberOfType = getTotalOfNamedResult[0] # so if 1*s have 5 cards, this will give you five
					numCardGet = random.randint(1,maxNumberOfType) # okay so now we have which card you get
					# okay so now we have to assign it
					# so first we have to get its ID and stuff
					getReceivedCard = "SELECT * FROM cardcatalogue WHERE rarity = %s AND name = 'Alice' AND ROWNUM = %s" % (rarityGet, numCardGet)
					cursor = db.cursor()
					cursor.execute(getReceivedCard)
					cardYouJustGot = cursor.fetchone()
					personCardNum = cardYouJustGot[3]
					# okay so now we have whether it's Alice2, Alice3, etc.
					# now we have to go to alice table
					checkIfInPersonTable = "SELECT * FROM Alice WHERE user = \'%s\'" % (author.id)
					cursor = db.cursor()
					cursor.execute(checkIfInPersonTable)
					inPersonTableResults = cursor.fetchone()

					if(inPersonTableResults == None):
						# need to add them into the table
						hasCardString = "hasCard%s" % (personCardNum) # so hasCard3
						updaterString = "INSERT INTO Alice (user, %s) VALUES (%s, 1)" % (hasCardString, author.id)
						cursor = db.cursor()
						cursor.execute(updaterString)
						db.commit()
						# there we go, added them in
					else:
						# this means they are already in there
						# so first let's check if they already have it
						checkerString = "SELECT user, %s FROM Alice WHERE user=\'%s\'" % (author.id)
						cursor = db.cursor()
						cursor.execute(checkerString)
						checkerResult = cursor.fetchone()
						alreadyHas = checkerResult[1]

						if(alreadyHas==1): # that is to say, already has the card, refund some points
							print("User already has this card, refund points")
							# NOW I GOTTA WRITE A QUERY TO GET YOUR FRIGGING POITNS
							getPointsQuery = "SELECT points FROM userlist where user=\'%s\'" % (author.id)
							cursor = db.cursor()
							cursor.execute(getPointsQuery)
							userPointsResult =  cursor.fetchone()
							userPoints = userPointsResult[0]

							# okay so now we need the rarity of the card
							if rarityGet == 1:
								userPoints = userPoints + 10
							elif rarityGet == 2:
								userPoints = userPoints + 20
							elif rarityGet == 3:
								userPoints = userPoints + 30
							elif rarityGet == 4:
								userPoints = userPoints + 40
							elif rarityGet == 5:
								userPoints = userPoints + 50

							addPointsBackQuery = "UPDATE points FROM userlist where user=\'%s\'" % (author.id)
							cursor = db.cursor()
							cursor.execute(addPointsBackQuery)
							# points added in

						else:
							print("User does not have this card, let's add it to their list.")
							# so we have to define hasCardString here
							hasCardString = "hasCard%s" % (personCardNum)
							# well actually looking back on it this code is redundant lmao
							# will fix in the optimization patch
							addNewCardString = "INSERT INTO Alice (user, %s) VALUES (%s, 1)" % (hasCardString, author.id)
							cursor = db.cursor()
							cursor.execute(addNewCardString)
							db.commit()







		else:
			print("Can't roll yet.\n")









#client.login('[login email]', '[bot password]')
#client.run('[DISCORD BOT TOKEN')
db.commit()
db.close()
print("Bot offline.\n")

#
#@client.event