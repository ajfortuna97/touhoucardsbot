# role management for Misty Lake

async def toggleMeToRole(message, roleExceptions, client): # same command to turn it off and on
	author = message.author
	messageServer = message.server
	allRoles = messageServer.roles
	brokenDown = message.content.split(" ", 1)
	# now we can keep going
	roleToToggle = brokenDown[1]

	# generate all strings
	found = False
	roleObject = None
	for x in allRoles:
		if x.name == roleToToggle:
			found = True
			roleObject = x # save this for later

	if found and roleToToggle not in roleExceptions:
		# success
		if roleObject in author.roles:
			# remove it
			await client.remove_roles(author, roleObject)
			#print("Removed the %s role." % roleToToggle)
			await client.send_message(message.channel, "Removed the %s role." % roleToToggle)
		else:
			# add it
			await client.add_roles(author, roleObject)
			#print("Added the %s role." % roleToToggle)
			await client.send_message(message.channel, "Added the %s role." % roleToToggle)
	elif not found:
		# handle failure cases
		await client.send_message(message.channel, "That isn't a role.")
	elif found and roleToToggle in roleExceptions:
		await client.send_message(message.channel, "You can't get that role.")

async def artRoleList(message, roleExceptions, client):
	author = message.author
	messageServer = message.server
	allRoles = messageServer.roles

	stringToDisplay = "The following roles are available:\n"

	validRoleCount = len(allRoles) - len(roleExceptions)
	print(validRoleCount)

	rolesToDisplay = []

	for x in allRoles:
		if x.name not in roleExceptions and x.name != "@everyone":
			#stringToDisplay = stringToDisplay + x.name + ", "
			rolesToDisplay.append(x.name)

	rolesToDisplay.sort()

	for x in rolesToDisplay:
		stringToDisplay = stringToDisplay + x + ", "


	stringToDisplay = stringToDisplay[:-2]


	await client.send_message(message.channel, stringToDisplay)