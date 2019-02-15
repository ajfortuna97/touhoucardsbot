# here we go, bot time
import discord
import asyncio
import random
import ctypes
import io
import os
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

db = mysql.connector.connect(user=dbUser, password=dbPass, host=dbAddress, port = dbPort, database = dbDB, auth_plugin='mysql_native_password')

# let's define the big list of people
touhouCharList = ['alice', 'aya', 'byakuren', 'chen', 'cirno', 'clownpiece', 'daiyousei', 'eirin', 'flandre', 'hina', 'junko', 'kaguya', 'kanako', 'keine', 'koakuma', 'kogasa', 'koishi', 'kokoro', 'komachi', 'letty', 'marisa', 'meiling', 'mima', 'mokou', 'momiji', 'mystia', 'nitori', 'nue', 'parsee', 'patchy', 'ran', 'reimu', 'reisen', 'remilia', 'rinnosuke', 'rumia', 'sakuya', 'sanae', 'satori', 'shiki', 'shin', 'suwako', 'tancirno', 'tewi', 'utsuho', 'wriggle', 'youki', 'youmu', 'yukari', 'yuuka', 'yuyuko', 'zun']

async def rollCard(rightNow, author, message, isGuaranteed, isGacha):
	if(isGacha is False):
		print("Updating time.\n")
		timeToList = rightNow.strftime("%Y-%m-%d %H:%M:%S")
		queryString = "UPDATE userlist SET lastrolled = \'%s\' WHERE user = %s" % (timeToList, author.id)
		cursor = db.cursor(buffered=True)
		cursor.execute(queryString)
		db.commit()

	cardNameRolled = random.randint(0, len(touhouCharList) -1) # due to 0 indexing
	#cardNameRolled = 1 # debugging line
	#print("You rolled card type %d" % cardNameRolled)

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

	if(isGuaranteed and rarityGet < 4): # just change it to 4, since you didn't roll an SSR
		rarityGet = 4

	#print("You rolled a(n) %s card of rarity %d" % (touhouYouGet, rarityGet))
	getTotalOfNamed = "SELECT count FROM cardcounts WHERE personName = \'%s\' AND rarity = %s" % (touhouYouGet, rarityGet)
	#print(getTotalOfNamed)
	cursor = db.cursor(buffered=True)
	cursor.execute(getTotalOfNamed)
	getTotalOfNamedResult = cursor.fetchone()

	while(getTotalOfNamedResult == None):
		#print("Hold up, there's no cards of that rarity. We have to try again.\n");
		# if there are no cards of the type you rolled
		# keep rarity, roll a different person
		cardNameRolled = random.randint(1, len(touhouCharList) -1)
		touhouYouGet = touhouCharList[cardNameRolled-1] # get new person
		getTotalOfNamed = "SELECT count FROM cardcounts WHERE personName = \'%s\' AND rarity = %s" % (touhouYouGet, rarityGet)
		cursor = db.cursor(buffered=True)
		cursor.execute(getTotalOfNamed)
		getTotalOfNamedResult = cursor.fetchone()
		#print("You rolled card type %d, which is %s\n" % (cardNameRolled, touhouYouGet))

	# okay so this guarantees that you have a card

	maxNumberOfType = getTotalOfNamedResult[0] # so if 1*s have 5 cards, this will give you five
	#print("There are %d cards of this type." % maxNumberOfType)
	numCardGet = random.randint(1,maxNumberOfType) # okay so now we have which card you get

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
		#print("Adding you to the table to get the card\n")
		updaterString = "INSERT INTO hascard VALUES (\'%s\', %s)" % (author.id, cardIDYouGet)
		cursor = db.cursor(buffered=True)
		cursor.execute(updaterString)
		db.commit()
		returnString = '%s%s' % (touhouYouGet, cardIDYouGet)
		return [returnString, 0] 
	else:
		# means they already have this card
		# so refund points
		#print("User already has this card, refund points\n")
		# NOW I GOTTA WRITE A QUERY TO GET YOUR FRIGGING POITNS
		getPointsQuery = "SELECT points FROM userlist where user=\'%s\'" % (author.id)
		cursor = db.cursor(buffered=True)
		cursor.execute(getPointsQuery)
		userPointsResult =  cursor.fetchone()
		userPoints = userPointsResult[0]

		# okay so now we need the rarity of the card
		pointsGivenBack = 10
		if rarityGet == 1:
			userPoints = userPoints + 10
		elif rarityGet == 2:
			userPoints = userPoints + 20
			pointsGivenBack = 20
		elif rarityGet == 3:
			userPoints = userPoints + 30
			pointsGivenBack = 30
		elif rarityGet == 4:
			userPoints = userPoints + 40
			pointsGivenBack = 40
		elif rarityGet == 5:
			userPoints = userPoints + 50
			pointsGivenBack = 50

		addPointsBackQuery = "UPDATE userlist SET points = %d WHERE user = \'%s\'" % (userPoints, author.id)
		cursor = db.cursor(buffered=True)
		cursor.execute(addPointsBackQuery)
		# points added in
		db.commit()

		#refundString = "You already have the card %s%d, refunding you %d points." % (touhouYouGet, cardIDYouGet, pointsGivenBack) 

		returnString = '%s%s' % (touhouYouGet, cardIDYouGet)
		return [returnString, pointsGivenBack]

async def check_cost(author, message, cost):
	getUserPointsString = "SELECT points FROM userlist WHERE user = '%s'" % author.id
	cursor = db.cursor(buffered=True)
	cursor.execute(getUserPointsString)
	getUserPointsResult = cursor.fetchone()

	if(getUserPointsResult != None):
		if(getUserPointsResult[0] >= cost):
			# we have enough
			subtractPointsQuery = "UPDATE userlist SET points = %d WHERE user = \'%s\'" % (getUserPointsResult[0] - cost, author.id)
			cursor = db.cursor(buffered=True)
			cursor.execute(subtractPointsQuery)
			db.commit()
			spentPointsString = "You spent %d points out of your %d to roll. You now have %d points." % (cost, getUserPointsResult[0], getUserPointsResult[0] - cost)
			await client.send_message(message.channel, '%s' % spentPointsString)
			return True
		else:
			print("You don't have enough points to roll.")
			await client.send_message(message.channel, "You don't have enough points for that command.")
			return False
	else:
		print("User not in the database, need to make them.")
		await create_user(author)
		await client.send_message(message.channel, "You did not have user entry until now. Please call the command again.")
		return False

async def create_user(author):
	now = datetime.now()
	timeToList = now.strftime("%Y-%m-%d %H:%M:%S")
	queryString = "INSERT INTO userlist VALUES(\'%s\', 500, \'%s\', NULL)" % (author.id, timeToList)
	#print(queryString + '\n')
	cursor = db.cursor(buffered=True)
	cursor.execute(queryString)
	#curUser = cursor.fetchone()
	print("Added user.\n")
	db.commit()


@client.event
@asyncio.coroutine

async def on_message(message):
	global db
	print("Got message.")
	# TODO: Add code to reconnect if bot goes too long without hitting server
	if not(db.is_connected()):
		db = mysql.connector.connect(user=dbUser, password=dbPass, host=dbAddress, port = dbPort, database = dbDB, auth_plugin='mysql_native_password')

	if(message.content.startswith("quit")):
		# trying to figure out how to gracefully exit but
		# for now this'll have to do
		# if I use close() or logout() it throws a Task was destroyed but it is pending
		if(message.author.id == '156819006395908096'):
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

		getAllYourCards = "SELECT cardcatalogue.name, cardcatalogue.idNum FROM hascard JOIN cardcatalogue ON hascard.cardID = cardcatalogue.idNum WHERE userID = \'%s\' ORDER BY cardcatalogue.name, cardcatalogue.idNum" % author.id
		cursor = db.cursor(buffered=True)
		cursor.execute(getAllYourCards)
		getAllYourCardsResult = cursor.fetchone()

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

		await client.send_message(message.channel, '%s' % cardListString)

	elif(message.content.startswith("!showcard")):
		author = message.author
		stringProcessing = message.content
		brokenDown = stringProcessing.split()
		if(len(brokenDown) != 2):
			await client.send_message(message.channel, "Error in processing command. Please use the proper syntax: !showcard [card you would like to display]")
		else:
			print(brokenDown[0])
			print("\n")
			print(brokenDown[1])

			# okay so now we have to actually parse between the name and the number
			# first let's check that it's in there
			nameSearchingFor = brokenDown[1]

			charName = ""
			charNum = ""
			try: # error handling sucks
				for c in nameSearchingFor:
					if ord(c) in range(65, 91) or ord(c) in range(97, 123):
						# this designates an alphabetical character
						charName = charName + c
					elif c in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
						charNum = charNum + c
					else:
						raise Exception("Invalid character detected.")
			except:
				# some kind of invalid character, like if you try to put in weird unicode characters
				await client.send_message(message.channel, "Invalid input detected, please make sure you use only alpha-numeric characters.")

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
			await create_user(author)
			rightNow = datetime.now()
			lastDailyTime = rightNow.strftime("%Y-%m-%d %H:%M:%S")
			getPoints = 525 # easy to fix a constant for new user
			updateLastDaily = "UPDATE userlist SET lastdaily = \'%s\', points = \'%s\' WHERE user = \'%s\'" % (lastDailyTime, getPoints, author.id)
			cursor = db.cursor(buffered=True)
			cursor.execute(updateLastDaily)
			db.commit()	
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
		if(await check_cost(message.author, message, 50)):
			print("You have enough to roll once!")
			rightNow = datetime.now()
			returnArray = await rollCard(rightNow, message.author, message, False, True)
			replyMessage = ""
			if(returnArray[1] == 0):
				# new card
				replyMessage = "You got the %s card!" % returnArray[0]
			else:
				# card you got before
				replyMessage = "You already have the %s card, refunding you %d points." % (returnArray[0], returnArray[1])
			await client.send_message(message.channel, '%s' % replyMessage)

	elif(message.content.startswith("!10roll")):
		if(await check_cost(message.author, message, 500)):
			print("You have enough to roll once!")
			rightNow = datetime.now()
			tenRollArray = []
			for x in range(9): # does rolls 1 through 9
				tenRollArray.append(await rollCard(rightNow, message.author, message, False, True))
			tenRollArray.append(await rollCard(rightNow, message.author, message, True, True))
			replyMessageStart = "You got the following cards:"
			replyMessageNew = "**New Cards:** "
			replyMessageAlreadyHave = "**Duplicate Cards:** "
			newCards = 0
			dupeCards = 0
			totalPoints = 0

			for entry in tenRollArray:
				if(entry[1] == 0):
					# new card
					if newCards == 0:
						replyMessageNew = replyMessageNew + entry[0]
						newCards = newCards + 1
					else:
						replyMessageNew = replyMessageNew + ", %s" % entry[0]
						newCards = newCards + 1

				else:
					# card you got before
					if dupeCards == 0:
						replyMessageAlreadyHave = replyMessageAlreadyHave + entry[0]
						dupeCards = dupeCards + 1
					else:
						replyMessageAlreadyHave = replyMessageAlreadyHave + ", %s" % entry[0]
						dupeCards = dupeCards + 1
						totalPoints = totalPoints + entry[1]
			# end for loop
			finalMessage = replyMessageStart + "\n" + replyMessageNew
			if(dupeCards != 0): # meaning we got at least one dupe card
				finalMessage = finalMessage + "\n" + replyMessageAlreadyHave + "\nYou received %d points back." % totalPoints


			await client.send_message(message.channel, '%s' % finalMessage)
		
	else: # BIG MASSIVE LOOP ON ROLLING NEW CARDS RANDOMLY
		author = message.author
		if author.id == '218794301893771264': # prevents bot from hitting its own messages
			pass
		else:
			messageServer = message.server
			if messageServer.id == '211120484731977728':  # this is to limit where the bot can go, you put your own server ID here 
				# 1/1000 chance to get a card
				queryString = "SELECT * FROM userlist WHERE user = " + author.id
				#print(queryString + "\n")
				cursor = db.cursor(buffered=True)
				cursor.execute(queryString)
				curUser = cursor.fetchone()
				#opLeaderName = str(topLeader[0])
				#print("Checking to see if you are in the database.\n")
				if(curUser == None): # need to insert
					create_user(author.id)
				# if not there, then do nothing

				#print("You are now in or were already in the database.\n")
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
				difference = abs((rightNow - lastTimeRolledConverted))
				#if(difference.total_seconds() >= 120):
				if(difference.total_seconds() >= 0): # debugging line
					#task = loop.create_task(rollCard(rightNow))
					#loop.run_until_complete(task)
					getCard = random.randint(1, 1000)
					#if(getCard==1000):
					if True: # debug line atm
						returnArray = await rollCard(rightNow, author, message, False, False)
						replyMessage = ""
						if(returnArray[1] == 0):
							# new card
							replyMessage = "You got the %s card!" % returnArray[0]
						else:
							# card you got before
							replyMessage = "You already have the %s card, refunding you %d points." % (returnArray[0], returnArray[1])

						await client.send_message(message.channel, '%s' % replyMessage)

def main():
	print("Executing main method.")
	client.run(botToken)
	db.commit()
	db.close()
	print("Bot offline.\n")

main()