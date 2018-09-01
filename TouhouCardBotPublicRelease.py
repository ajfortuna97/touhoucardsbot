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
import sys

import mysql
import mysql.connector

client = discord.Client()

db = mysql.connector.connect(user='[user]', password='[database password]', host='localhost', database = 'touhoucards')

# let's define the big list of people
touhouCharList = ['alice', 'aya', 'byakuren', 'chen', 'cirno', 'clownpiece', 'daiyousei', 'eirin', 'flandre', 'hina', 'junko', 'kaguya', 'kanako', 'keine', 'koakuma', 'kogasa', 'koishi', 'kokoro', 'komachi', 'letty', 'marisa', 'meiling', 'mima', 'mokou', 'momiji', 'mystia', 'nitori', 'nue', 'parsee', 'patchy', 'ran', 'reimu', 'reisen', 'remilia', 'rinnosuke', 'rumia', 'sakuya', 'sanae', 'satori', 'shiki', 'shin', 'suwako', 'tancirno', 'tewi', 'utsuho', 'wriggle', 'youki', 'youmu', 'yukari', 'yuuka', 'yuyuko', 'zun']

@client.event
@asyncio.coroutine
def on_message(message):
	print("Got message.")

	if(message.content.startswith("quit")):
		sys.exit()
	elif(message.content.startswith("!listcards")):
		cardListString = "You have these cards:\n"
		amountOfCardsYouHave = 0
		author = message.author


		for name in touhouCharList:
			getAmountOfCardsQuery = "SELECT COUNT(*) FROM cardcatalogue WHERE name = \'%s\'" % (name)
			cursor = db.cursor(buffered=True)
			cursor.execute(getAmountOfCardsQuery)
			getAmountOfCardsResult = cursor.fetchone()

			if(getAmountOfCardsResult == None):
				pass # just do nothing
			else:
				amountOfCardsForName = getAmountOfCardsResult[0] # gives us the amount of cards for us

				# so now we need to go check each table
				getUserCardsForName = "SELECT * FROM %s WHERE user = \'%s\'" % (name, author.id)
				cursor = db.cursor(buffered=True)
				cursor.execute(getUserCardsForName)
				getUserCardsForNameResult = cursor.fetchone()

				if(getUserCardsForNameResult == None):
					pass
				else:
					# okay this means that we have at least one card of this type
					for x in range(1, amountOfCardsForName):
						if getUserCardsForNameResult[x] == 1:
							print("You have card %s%d" % (name, x))

							if amountOfCardsYouHave == 0:
								cardListString = cardListString + "%s%d" % (name, x)
								amountOfCardsYouHave = amountOfCardsYouHave + 1
							else:
								cardListString = cardListString + ", %s%d" % (name, x)
								amountOfCardsYouHave = amountOfCardsYouHave + 1

		print(cardListString)
		#await client.send_message(message.channel, '%s' % cardListString)
		yield from client.send_message(message.channel, '%s' % cardListString)
	elif(message.content.startswith("!showcard")):
		author = message.author
		stringProcessing = message.content
		brokenDown = stringProcessing.split()
		if(len(brokenDown) != 2):
			print("Error in processing command. Please use the proper syntax: !showcard [card you would like to display]")
		else:
			print(brokenDown[0])
			print("\n")
			print(brokenDown[1])

			# okay so now we have to actually parse between the name and the number
			# first let's check that it's in there
			nameSearchingFor = brokenDown[1]

			charName = ""
			charNum = ""
			for c in nameSearchingFor:
				if c not in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
					# this designates an alphabetical character
					charName = charName + c
				else:
					charNum = charNum + c

			print(charName)
			print("\n")
			print(charNum)

			charName = charName.lower()

			if(charName not in touhouCharList):
				print("Not a character, don't search.")
			else:
				# valid character, begin parsing
				# essentially we want to get it that we have
				# [name] [number]
				# this lets us check that the user actually has the card in question
				# so, we can probably start from the end of the string and work backwards
				# or we can just step through it
				
				checkIfHasCardQuery = "SELECT * FROM %s WHERE user = \'%s\'" % (charName, author.id)
				cursor = db.cursor(buffered=True)
				cursor.execute(checkIfHasCardQuery)

				checkCard = cursor.fetchone()

				if(checkCard==None): # they don't have the card at all
					print("You don't have this card.")
				else:
					# so they have a card of this type
					# now we need to check if they have it
					charNumInt = int(charNum)
					if(checkCard[charNumInt]==0):
						print("You don't have that card.")
					else:
						print("You do have that card!")
						# so now we have to go to the cardcatalogue to get its ID number
						getCardIDQuery = "SELECT idNum FROM cardcatalogue WHERE name=\'%s\' AND personCardNum=%d" % (charName, charNumInt)
						cursor = db.cursor(buffered=True)
						cursor.execute(getCardIDQuery)
						checkCard = cursor.fetchone()
						# don't have to do a none check because we KNOW this card exists at this point
						cardID = checkCard[0]
						imageFileName = "%s %d.png" % (charName, cardID)
						print(imageFileName)

						os.chdir("pictures")
						os.chdir("%s" % (charName))
						yield from client.send_file(message.channel, "%s" % imageFileName)
						os.chdir("..")
						os.chdir("..")

	else:
		author = message.author
		if author.id == '218794301893771264': # prevents bot from hitting its own messages
			pass
		else:
			messageServer = message.server
			if messageServer.id == '211120484731977728':  # this is to limit where the bot can go, you put your own server ID here
				# 1/1000 chance to get a card
				queryString = "SELECT * FROM userlist WHERE user = " + author.id
				print(queryString + "\n")
				cursor = db.cursor(buffered=True)
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
					cursor = db.cursor(buffered=True)
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
				cursor = db.cursor(buffered=True) # yeah I can probably get away without doing this but copy paste
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

				#if(difference.total_seconds() >= 120):
				if(difference.total_seconds() >= 0): # debugging line
					print("I can roll.\n")
					print("Updating time.\n")
					timeToList = rightNow.strftime("%Y-%m-%d %H:%M:%S")
					queryString = "UPDATE userlist SET lastrolled = \'%s\' WHERE user = %s" % (timeToList, author.id)
					cursor = db.cursor(buffered=True)
					cursor.execute(queryString)
					#lastTimeRolled = cursor.fetchone()
					db.commit()


					getCard = random.randint(1, 1000)

					#if(getCard==1000): # you get a random card
					if True is True: # this is for debugging
						getCardNamesCount = "SELECT COUNT(*) FROM (SELECT name FROM cardcatalogue) AS getName"
						cursor = db.cursor(buffered=True)
						cursor.execute(getCardNamesCount)
						cardTypesResult = cursor.fetchone()
						totalCardTypes = cardTypesResult[0]

						cardNameRolled = random.randint(1, totalCardTypes)
						cardNameRolled = 1 # debugging line
						print("You rolled card type %d" % cardNameRolled)


						# BIG DECIDING PORTION ON WHO YOU GET HERE
						touhouYouGet = ""
						if(cardNameRolled==1): # Alice
							touhouYouGet = "Alice"
							# NOW YOU GACHA AGAIN FOR RARITY



						# handles rarity and the rest of the card business

						rarityGet = random.randint(1,5)
						print("You rolled rarity %d" % rarityGet)
						getTotalOfNamed = "SELECT COUNT(*) FROM cardcatalogue WHERE rarity = %s AND name = \'%s\'" % (rarityGet, touhouYouGet)
						cursor = db.cursor(buffered=True)
						cursor.execute(getTotalOfNamed)
						getTotalOfNamedResult = cursor.fetchone()
						maxNumberOfType = getTotalOfNamedResult[0] # so if 1*s have 5 cards, this will give you five
						numCardGet = random.randint(1,maxNumberOfType) # okay so now we have which card you get
						#cursor.fetchall() # more dumb workarounds
						# okay so now we have to assign it
						# so first we have to get its ID and stuff
						#getReceivedCard = "SELECT * FROM cardcatalogue WHERE rarity = %s AND name = \'%s\' AND ROWNUM = %s" % (rarityGet, numCardGet, touhouYouGet)

						getReceivedCard = "SELECT * FROM cardcatalogue WHERE rarity = %s AND name = \'%s\'" % (rarityGet, touhouYouGet)
						
						numCardGetCounter = 0
						cursor = db.cursor(buffered=True)
						cursor.execute(getReceivedCard)
						db.commit()

						while(numCardGetCounter != numCardGet): # so if you had card 1, it loops once, 2, loops twice, etc.
							cardYouJustGot = cursor.fetchone()
							numCardGetCounter = numCardGetCounter + 1

						# okay so this is a dumb workaround due to mySQL "unread results"
						#cursor.fetchall() # done lol

						personCardNum = cardYouJustGot[3]
						# okay so now we have whether it's Alice2, Alice3, etc.
						print("You got card %s%d" % (touhouYouGet, personCardNum)) 
						# now we have to go to alice table
						checkIfInPersonTable = "SELECT * FROM %s WHERE user = \'%s\'" % (touhouYouGet, author.id)
						cursor = db.cursor(buffered=True)
						cursor.execute(checkIfInPersonTable)
						inPersonTableResults = cursor.fetchone()
						db.commit()

						if(inPersonTableResults == None):
							# need to add them into the table
							print("Adding you to the table to get the card\n")
							hasCardString = "hasCard%s" % (personCardNum) # so hasCard3
							updaterString = "INSERT INTO %s (user, %s) VALUES (%s, 1)" % (touhouYouGet, hasCardString, author.id)
							cursor = db.cursor(buffered=True)
							cursor.execute(updaterString)
							db.commit()
							# there we go, added them in
						else:
							# this means they are already in there
							# so first let's check if they already have it
							hasCardString = "hasCard%s" % (personCardNum) # so hasCard3
							print("You already have a card of this type.\n")
							checkerString = "SELECT user, %s FROM %s WHERE user=\'%s\'" % (hasCardString, touhouYouGet, author.id)
							cursor = db.cursor(buffered=True)
							cursor.execute(checkerString)
							checkerResult = cursor.fetchone()
							alreadyHas = checkerResult[1]
							db.commit()

							if(alreadyHas==1): # that is to say, already has the card, refund some points
								print("User already has this card, refund points\n")
								# NOW I GOTTA WRITE A QUERY TO GET YOUR FRIGGING POITNS
								getPointsQuery = "SELECT points FROM userlist where user=\'%s\'" % (author.id)
								cursor = db.cursor(buffered=True)
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

								addPointsBackQuery = "UPDATE userlist SET points = %d WHERE user = \'%s\'" % (userPoints, author.id)
								cursor = db.cursor(buffered=True)
								cursor.execute(addPointsBackQuery)
								# points added in
								db.commit()

							else:
								print("User does not have this card, let's add it to their list.\n")
								# so we have to define hasCardString here
								hasCardString = "hasCard%s" % (personCardNum)
								# well actually looking back on it this code is redundant lmao
								# will fix in the optimization patch
								addNewCardString = "UPDATE %s SET %s = 1 WHERE user = \'%s\'" % (touhouYouGet, hasCardString, author.id) #(user, %s) VALUES (%s, 1)" % (hasCardString, author.id)"
								cursor = db.cursor(buffered=True)
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