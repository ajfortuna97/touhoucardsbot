# here we go, bot time
import discord
import asyncio
import random
import ctypes
import io
import os
#from discord import opus
#import time
from time import gmtime, strftime
import time
from datetime import datetime
import sys

import mysql
import mysql.connector

client = discord.Client()

configReader = open("bot.config", "r")

dbUser = configReader.readline()
dbPass = configReader.readline()
dbAddress = configReader.readline()
dbPort = configReader.readline()
dbDB = configReader.readline()
botToken = configReader.readline()

configReader.close()
dbPass = dbPass.rstrip()

db = mysql.connector.connect(user=dbUser, password=dbPass, host=dbAddress, port = dbPort, database = dbDB)


# let's define the big list of people
touhouCharList = ['alice', 'aya', 'byakuren', 'chen', 'cirno', 'clownpiece', 'daiyousei', 'eirin', 'flandre', 'hina', 'junko', 'kaguya', 'kanako', 'keine', 'koakuma', 'kogasa', 'koishi', 'kokoro', 'komachi', 'letty', 'marisa', 'meiling', 'mima', 'mokou', 'momiji', 'mystia', 'nitori', 'nue', 'parsee', 'patchy', 'ran', 'reimu', 'reisen', 'remilia', 'rinnosuke', 'rumia', 'sakuya', 'sanae', 'satori', 'shiki', 'shin', 'suwako', 'tancirno', 'tewi', 'utsuho', 'wriggle', 'youki', 'youmu', 'yukari', 'yuuka', 'yuyuko', 'zun']

async def rollCard(rightNow, author, message):
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

		cardNameRolled = random.randint(0, len(touhouCharList) -1) # due to 0 indexing
		#cardNameRolled = 1 # debugging line
		print("You rolled card type %d" % cardNameRolled)


		# BIG DECIDING PORTION ON WHO YOU GET HERE
		touhouYouGet = ""
		#if(cardNameRolled==1): # Alice
		#	touhouYouGet = "Alice"
		#if(cardNameRolled==2): # Aya
		#	touhouYouGet = "Aya"
		#if(cardNameRolled==3): # Byakuren
		#	touhouYouGet = "Byakuren"
			# NOW YOU GACHA AGAIN FOR RARITY
		# or you could not be a scrub and realize that it's a big array
		# so you can literally just do
		touhouYouGet = touhouCharList[cardNameRolled-1]

		# handles rarity and the rest of the card business

		#rarityGet = random.randint(1,5)
		rarityRoll = random.randint(1, 100)
		rarityGet = 1

		if(rarityRoll < 4): # i.e. 1-3, 3% UR rate
			rarityGet = 5
		elif (rarityRoll > 3 and rarityRoll < 15): # i.e. 4 through 14, 10% SSR rate
			rarityGet = 4
		elif (rarityRoll > 14 and rarityRoll < 36): # 15 to 35, 20% SR rate 
			rarityGet = 3
		elif (rarityRoll > 35 and rarityRoll < 66): # 36 to 65, 30% R rate
			rarityGet = 2
		else: # leaves you with 47% chance to get a rare on message
			rarityGet = 1



		print("You rolled a(n) %s card of rarity %d" % (touhouYouGet, rarityGet))
		#getTotalOfNamed = "SELECT COUNT(*) FROM cardcatalogue WHERE rarity = %s AND name = \'%s\'" % (rarityGet, touhouYouGet)
		getTotalOfNamed = "SELECT count FROM cardcounts WHERE personName = \'%s\' AND rarity = %s" % (touhouYouGet, rarityGet)
		print(getTotalOfNamed)
		cursor = db.cursor(buffered=True)
		cursor.execute(getTotalOfNamed)
		getTotalOfNamedResult = cursor.fetchone()

		while(getTotalOfNamedResult == None):
			print("Hold up, there's no cards of that rarity. We have to try again.\n");
			# if there are no cards of the type you rolled
			# keep rarity, roll a different person
			cardNameRolled = random.randint(1, len(touhouCharList) -1)
			touhouYouGet = touhouCharList[cardNameRolled-1] # get new person
			#getTotalOfNamed = "SELECT COUNT(*) FROM cardcatalogue WHERE rarity = %s AND name = \'%s\'" % (rarityGet, touhouYouGet)
			getTotalOfNamed = "SELECT count FROM cardcounts WHERE personName = \'%s\' AND rarity = %s" % (touhouYouGet, rarityGet)
			cursor = db.cursor(buffered=True)
			cursor.execute(getTotalOfNamed)
			getTotalOfNamedResult = cursor.fetchone()
			print("You rolled card type %d, which is %s\n" % (cardNameRolled, touhouYouGet))

		# okay so this guarantees that you have a card

		maxNumberOfType = getTotalOfNamedResult[0] # so if 1*s have 5 cards, this will give you five
		print("There are %d cards of this type." % maxNumberOfType)
		numCardGet = random.randint(1,maxNumberOfType) # okay so now we have which card you get
		#cursor.fetchall() # more dumb workarounds

		# how it SHOULD BE
		# we have the number of cards of a type and rarity
		# now we just need to randomly select one
		# i.e. what we should do is
		# roll a dice between 1 and whatever number there are
		# and then just iterate down the table until we get there
		# so if 1-5, roll 3, go to the third card

		numCardGetCounter = 0
		getReceivedCard = "SELECT * FROM cardcatalogue WHERE rarity = %s AND name = \'%s\'" % (rarityGet, touhouYouGet)
		cursor = db.cursor(buffered=True)
		cursor.execute(getReceivedCard)
		db.commit()

		while(numCardGetCounter != numCardGet): # so if you had card 1, it loops once, 2, loops twice, etc.
			cardYouJustGot = cursor.fetchone()
			numCardGetCounter = numCardGetCounter + 1

		# from here, you just need to get the cardID, and then you can add it to the card catalogue
		cardIDYouGet = cardYouJustGot[2] # field 3
		# we should have everything now
		# first we'll check if they actually already have this card
		alreadyHasCard = "SELECT * FROM hascard WHERE userID = \'%s\' AND cardID = %s" % (author.id, cardIDYouGet)
		cursor = db.cursor(buffered=True)
		cursor.execute(alreadyHasCard)
		inPersonTableResults = cursor.fetchone()
		db.commit()

		if(inPersonTableResults == None):
			# you got a new card
			print("Adding you to the table to get the card\n")
			#hasCardString = "hasCard%s" % (personCardNum) # so hasCard3
			#updaterString = "INSERT INTO %s (user, %s) VALUES (%s, 1)" % (touhouYouGet, hasCardString, author.id)

			updaterString = "INSERT INTO hascard VALUES (\'%s\', %s)" % (author.id, cardIDYouGet)
			cursor = db.cursor(buffered=True)
			cursor.execute(updaterString)
			db.commit()
			# there we go, added them in
			newCardString = "You got the %s%s card!" % (touhouYouGet, cardIDYouGet)
			# yield from client.send_message(message.channel, '%s' % newCardString)
			await client.send_message(message.channel, '%s' % newCardString)
		else:
			# means they already have this card
			# so refund points

			print("You already have a card of this type.\n")

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

			refundString = "You already have the card %s%d, refunding you %d points." % (touhouYouGet, personCardNum, userPoints) 

			# yield from client.send_message(message.channel, '%s' % refundString)
			await client.send_message(message.channel, '%s' % refundString)

@client.event
@asyncio.coroutine

async def on_message(message):
	print("Got message.")

	if(message.content.startswith("quit")):
		# trying to figure out how to gracefully exit but
		# for now this'll have to do
		# if I use close() or logout() it throws a Task was destroyed but it is pending
		db.commit()
		sys.exit()	
		
	elif(message.content.startswith("!listcards")):
		cardListString = "You have these cards:\n"
		amountOfCardsYouHave = 0
		author = message.author

			# new easy way!
			# select all for yourself in hascard
			# and then also join to cardcatalogue
			# to easily get names

		getAllYourCards = "SELECT cardcatalogue.name, cardcatalogue.idNum FROM hascard JOIN cardcatalogue ON hascard.cardID = cardcatalogue.idNum WHERE userID = \'%s\'" % author.id
		cursor = db.cursor(buffered=True)
		cursor.execute(getAllYourCards)
		getAllYourCardsResult = cursor.fetchone()

		print(cardListString)

		while(getAllYourCardsResult != None):
			# get the name and card ID num
			nameOfCard = getAllYourCardsResult[0]
			idOfCard = getAllYourCardsResult[1]

			if amountOfCardsYouHave == 0:
				cardListString = cardListString + "%s%d" % (nameOfCard, idOfCard)
				amountOfCardsYouHave = amountOfCardsYouHave + 1
			else:
				cardListString = cardListString + ", %s%d" % (nameOfCard, idOfCard)
				amountOfCardsYouHave = amountOfCardsYouHave + 1
			getAllYourCardsResult = cursor.fetchone()

		#print(cardListString)

		print(cardListString)
		await client.send_message(message.channel, '%s' % cardListString)
		#yield from client.send_message(message.channel, '%s' % cardListString)
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
				
				checkIfHasCardQuery = "SELECT * FROM hascard WHERE userID = \'%s\' AND cardID = %s" % (author.id, charNum)
				cursor = db.cursor(buffered=True)
				cursor.execute(checkIfHasCardQuery)

				checkCard = cursor.fetchone()

				if(checkCard==None): # they don't have the card at all
					print("You don't have this card.")
				else:
					# they do have the card here, so go and get it
					#cardID = checkCard[0]
					imageFileName = "%s %s.png" % (charName, charNum)
					print(imageFileName)

					os.chdir("pictures")
					os.chdir("%s" % (charName))
					#yield from client.send_file(message.channel, "%s" % imageFileName)
					await client.send_file(message.channel, "%s" % imageFileName)
					os.chdir("..")
					os.chdir("..")
	elif(message.content.startswith("!daily")): # adds your daily points, we'll say like, 25 per day (?)
		# eh screw it we'll just have a constant 25 per day
		# so you can either burn the roll every other day or you can save a little bit more
		# first let's get your points
		author = message.author
		getPointsQuery = "SELECT * FROM userlist WHERE user = \'%s\'" % (author.id)
		cursor = db.cursor(buffered=True)
		cursor.execute(getPointsQuery)
		getPointsResults = cursor.fetchone()

		if(getPointsResults==None):
			print("User not in the table") 
			# TODO - make user creation method
		else:
			getLastDailyUsage = getPointsResults[3] # is a datetime object
			if(getLastDailyUsage == None):
				print("hi null")
				rightNow = datetime.now()
				lastDailyTime = rightNow.strftime("%Y-%m-%d %H:%M:%S")
				getPoints = getPointsResults[1]
				getPoints = getPoints + 25
				updateLastDaily = "UPDATE userlist SET lastdaily = \'%s\', points = \'%s\' WHERE user = \'%s\'" % (lastDailyTime, getPoints, author.id)
				cursor = db.cursor(buffered=True)
				cursor.execute(updateLastDaily)
				db.commit()
			else:
				rightNow = datetime.now()
				difference = abs(rightNow - getLastDailyUsage)
				print("Difference in days: %s" % (difference.days))
				# DEBUGGING LINES
				#DEBUGGING_difference_days = 1
				#if(DEBUGGING_difference_days >= 1):
				# END DEBUGGING LINES
				if(difference.days >= 1):
					lastDailyTime = rightNow.strftime("%Y-%m-%d %H:%M:%S")
					getPoints = getPointsResults[1]
					print("You have %s points" % getPoints)
					getPoints = getPoints + 25
					updateLastDaily = "UPDATE userlist SET lastdaily = \'%s\', points = \'%s\' WHERE user = \'%s\'" % (lastDailyTime, getPoints, author.id)
					cursor = db.cursor(buffered=True)
					cursor.execute(updateLastDaily)
					db.commit()	
				else:
					print("Already rolled for the day!")
	elif(message.content.startswith("!roll")):
		pass
	elif(message.content.startswith("!10roll")):
		pass
	else: # BIG MASSIVE LOOP ON ROLLING NEW CARDS RANDOMLY
		author = message.author
		if author.id == '218794301893771264': # prevents bot from hitting its own messages
			pass
		else:
			messageServer = message.server
			if messageServer.id == '[server ID]':  # this is to limit where the bot can go, you put your own server ID here
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
					queryString = "INSERT INTO userlist VALUES(\'%s\', 500, \'%s\', NULL)" % (author.id, timeToList)
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
					#task = loop.create_task(rollCard(rightNow))
					#loop.run_until_complete(task)
					await rollCard(rightNow, author, message)
					print("called rollcard")
				else:
					print("Can't roll yet.\n")





def main():
	print("Executing main method.")
	client.run(botToken)
	db.commit()
	db.close()
	print("Bot offline.\n")
	

main()

#
#@client.event