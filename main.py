import discord
from discord.ext import commands
import asyncio
import datetime
import random
from secrets import bot_token
import json

# -----------------------------------------------------------------------

# The bot's command prefix to use commands.
client = commands.Bot(command_prefix=".")
client.remove_command("help")

# Prints in the console that shows that the bot is online and ready. It also changes the bot's online status and game.
@client.event
async def on_ready():
	print("Bot READY.")

filtered_words = []

try:
	filtered_words = json.load(open("words.py", "r"))
	print("<.> Filtered words successfully loaded.")
except:
	print("[!] Failed to load filtered words.")

@client.event
async def on_message(message):
	global filtered_words
	if message.author == client.user:
		return

	for w in filtered_words:
		if w in message.content:
			await message.delete()
	await client.process_commands(message)

# Responds to the user with an error if the command they entered does not currently exist or is on cooldown.
@client.event
async def on_command_error(ctx, error):
	if isinstance(error, commands.CommandNotFound):
		await ctx.channel.send(":x: This command does not exist. Can't find a command? Use `.help` to find a command.")
	elif isinstance(error, commands.CommandOnCooldown):
		await ctx.channel.send(":x: This command is on cooldown. Try again in {:.2f}s.".format(error.retry_after))
	print(error)


# Sends the list of commands.
@client.command()
@commands.cooldown(1, 10, commands.BucketType.user)
async def help(ctx):
	await ctx.channel.send(
		"```\nCOMMANDS\n-----------------------------\n"
		"<.> .help                         | Sends the list of commands.\n"
		"<.> .ping                         | 'Pong!'\n"
		"<.> .say <msg>                    | Repeats your message.\n"
		"<.> .mute <@user> <rsn>           | Mutes a user.\n"
		"<.> .unmute <@user>               | Unmutes a user.\n"
		"<.> .tempmute <@user> <sec> <rsn> | Temporarily mutes a user.\n"
		"<.> .report <@user> <rsn>         | Reports a user.\n"
		"<.> .filterword <word>            | Adds a word to a list of words that you do not want allowed.\n"
		"<.> .clearfilter                  | Will clear your list of filtered words.\n"
		"<.> .ban <@user> <rsn>            | Bans a user.\n"
		"<.> .unban <user#0000>            | Unbans a user.\n"
		"<.> .remind <sec> <msg>           | Sends a DM to you when the given duration is up with your message that you assigned.```"
	)


# Responds to a user with "Pong!" when a user uses the command ".ping".
@client.command()
@commands.cooldown(1, 10, commands.BucketType.user)
async def ping(ctx):
	await ctx.channel.send(f"Pong! {round(client.latency * 1000)}ms")


# Responds with the same message the user said.
@client.command()
@commands.cooldown(1, 10, commands.BucketType.user)
async def say(ctx, *, message):
	if message == 'C2C is cool':
		await ctx.channel.send("Yeah, I agree!")
	else:
		await ctx.channel.send(message)


# Sends an error if the user doesn't pass in a required argument.
@say.error
async def say_error(ctx, error):
	if isinstance(error, commands.MissingRequiredArgument):
		await ctx.channel.send(":warning: Missing required argument: `message`. Syntax: `.say <message>`")


# Mutes a specified user.
@client.command()
@commands.cooldown(1, 5, commands.BucketType.user)
@commands.has_permissions(manage_messages=True)
async def mute(ctx, member: discord.Member, *, reason="No reason specified"):
	# mutedRole = discord.Permissions()
	# mutedRole.update(send_messages=False)
	guild = ctx.guild

	# Checks if a user already has the role.
	for role in member.roles:
		if role.name == "Muted":
			await ctx.channel.send(":x: This user is already muted.")
			return

	# Checks if the role "Muted" exists. If it doesn't, it'll create one. If it does, nothing happens.
	if "Muted" not in [role.name for role in guild.roles]:
		await guild.create_role(name="Muted")
	else:
		pass

	# Checks to see if the role exists, and if it does, add the role.
	for role in guild.roles:
		if role.name == "Muted":
			await member.add_roles(role)
			await ctx.channel.send(f":white_check_mark: Successfully muted {member} for '{reason}'.")


# Sends an error if the user doesn't pass in a required argument or has missing permissions.
@mute.error
async def mute_error(ctx, error):
	if isinstance(error, commands.MissingRequiredArgument):
		await ctx.channel.send(":warning: Missing required argument(s). Syntax: `.mute <@user> <reason>`.")
	elif isinstance(error, commands.MissingPermissions):
		await ctx.channel.send(":x: You do not have the `Manage Messages` permission.")
	print(error)


# Unmute Command
@client.command()
@commands.cooldown(1, 5, commands.BucketType.user)
@commands.has_permissions(manage_messages=True)
async def unmute(ctx, member: discord.Member):
	guild = ctx.guild

	# Checks if the user doesn't have the required role.
	if "Muted" not in [role.name for role in member.roles]:
		await ctx.channel.send(":x: This user cannot be unmuted because they're not muted!")
		return

	# Removes the role.
	for role in guild.roles:
		if role.name == "Muted":
			await member.remove_roles(role)
			await ctx.channel.send(f":white_check_mark: Successfully unmuted {member}.")


# Sends an error if the user doesn't pass in a required argument.
@unmute.error
async def unmute_error(ctx, error):
	if isinstance(error, commands.MissingRequiredArgument):
		await ctx.channel.send(":warning: Missing required argument: `@user`. Syntax: `.unmute <@user>`.")
	elif isinstance(error, commands.MissingPermissions):
		await ctx.channel.send(":x: You do not have the `Manage Messages` permission.")


# Mutes a user temporarily.
@client.command()
@commands.cooldown(1, 10, commands.BucketType.user)
@commands.has_permissions(manage_messages=True)
async def tempmute(ctx, member: discord.Member, sec: int, *, reason="No reason specified"):
	guild = ctx.guild

	# Checks if a user already has the role.
	for role in member.roles:
		if role.name == "Muted":
			await ctx.channel.send(f":x: This user is already muted.")
			return

	# Checks if the role "Muted" exists. If it doesn't, it'll create one. If it does, nothing happens.
	if "Muted" not in [role.name for role in guild.roles]:
		await guild.create_role(name="Muted")
	else:
		pass

	# Checks to see if the role exists, and if it does, add the role, and removes it after the given time is up.
	for role in guild.roles:
		if role.name == "Muted":
			await member.add_roles(role)
			await ctx.channel.send(f":white_check_mark: Successfully muted {member} for {sec}s for the reason: '{reason}'.")
			await asyncio.sleep(sec)
			await member.remove_roles(role)

@tempmute.error
async def tempmute_error(ctx, error):
	if isinstance(error, commands.MissingRequiredArgument):
		await ctx.channel.send(":warning: Missing required argument(s) Syntax: `.tempmute <@user> <dur:sec> <reason>`")


# When used, this will send the report to the RECEIVER (aka me!).
@client.command()
@commands.cooldown(1, 10, commands.BucketType.user)
async def report(ctx, member: discord.Member, *, reason):
	receiver = await client.fetch_user(371802974470668321)
	#user = ctx.message.mentions[0]
	reports = []
	if member == receiver:
		await ctx.channel.send(":x: This user cannot be reported. Try someone else.")
	else:
		reports.append(member)
		await discord.DMChannel.send(receiver, f"New Report!```\nUser: {member}\nReason: {reason}\nReport #{len(reports)}```")
		await ctx.channel.send(":white_check_mark: Report sent!")


@report.error
async def report_error(ctx, error):
	if isinstance(error, commands.MissingRequiredArgument):
		await ctx.channel.send(":warning: Missing required argument(s) Syntax: `.report <@user> <reason>`")


# Filters a word. Adds the word to a list which in a event will remove the message if it has the word.
@client.command()
@commands.cooldown(1, 5, commands.BucketType.user)
@commands.has_permissions(manage_messages=True)
async def filterword(ctx, word):

	for w in filtered_words:
		if w == word:
			await ctx.channel.send(":x: This word is already filtered.")
			return
	filtered_words.append(word)
	json.dump(filtered_words, open("words.py", "w"))
	await ctx.channel.send(":white_check_mark: Word filtered. When a message has this word, the message will be deleted.")
	print(filtered_words)

@filterword.error
async def filterword_error(ctx, error):
	if isinstance(error, commands.MissingRequiredArgument):
		await ctx.channel.send(":warning: Missing required argument: `word`. Syntax: `.filterword <word>`")

@client.command()
@commands.cooldown(1, 20, commands.BucketType.user)
@commands.has_permissions(manage_messages=True)
async def clearfilter(ctx):
	await ctx.channel.send(f"List of filtered words: {filtered_words}\nAre you sure you want to clear your word list? (y/n/yes/no)")
	def check(m):
		return m.author.id == ctx.author.id
	message = await client.wait_for("message", check=check)
	if message.content.lower() == "y" or message.content.lower() == "yes":
		filtered_words.clear()
		json.dump(filtered_words, open("words.py", "w"))
		await ctx.channel.send(":white_check_mark: Clear successful.")
	else:
		await ctx.channel.send(":x: Did not clear.")
		return

# Bans a user.
@client.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
	banned_users = await ctx.guild.bans()

	await member.ban(reason=reason)
	await ctx.channel.send(f":white_check_mark: Successfully banned {member} for {reason}.")
	print(banned_users)

@ban.error
async def ban_error(ctx, error):
	if isinstance(error, commands.MissingRequiredArgument):
		await ctx.channel.send(":warning: Missing required argument(s) Syntax: `.ban <@user> <reason>`")


# Unbans a user.
@client.command()
@commands.has_permissions(ban_members=True)
async def unban(ctx, *, member):
	banned_users = await ctx.guild.bans()
	member_name, member_discriminator = member.split('#')

	for ban_entry in banned_users:
		user = ban_entry.user

		if(user.name, user.discriminator) == (member_name, member_discriminator):
			await ctx.guild.unban(user)
			await ctx.channel.send(f":white_check_mark: Successfully unbanned {user.name}.")

@unban.error
async def unban_error(ctx, error):
	if isinstance(error, commands.MissingRequiredArgument):
		await ctx.channel.send(":warning: Missing required argument: `user#0000`. Syntax: `.unban <user#0000>`")


@client.command()
@commands.cooldown(1, 10, commands.BucketType.user)
async def remind(ctx, s: int, *, msg):
	user = ctx.message.author.id
	sender = await client.fetch_user(user)

	await ctx.channel.send(":white_check_mark: Reminder set.")
	await asyncio.sleep(s)
	await discord.DMChannel.send(sender, f":exclamation: {ctx.author.name}, you have an incoming reminder: {msg}")


@remind.error
async def remind_error(ctx, error):
	if isinstance(error, commands.MissingRequiredArgument):
		await ctx.channel.send(":warning: Missing required argument(s) Syntax: `.remind <dur:sec> <msg>`")

# -----------------------------------------------------------------------

# Run the bot...
client.run(bot_token)