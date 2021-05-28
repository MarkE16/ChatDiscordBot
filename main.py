import discord
from discord.ext import commands
import asyncio
import datetime
import random
from secrets import bot_token
import json

def save(data):
	json.dump(data, open("main.py", "w"))

def load(data):
	data = json.load(open("main.py", "r"))

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
	load(filtered_words)
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
		"<.> .mute <@user>                 | Mutes a user.\n"
		"<.> .unmute <@user>               | Unmutes a user.\n"
		"<.> .tempmute <@user> <sec> <rsn> | Temporarily mutes a user.\n"
		"<.> .report <@user> <rsn>         | Reports a user.\n"
		"<.> .filterword <word>            | Adds a word to a list of words that you do not want allowed.\n"
		"<.> .ban <@user> <rsn>            | Bans a user.\n"
		"<.> .unban <@user>                | Unbans a user.\n"
		"<.> .remind <sec> <msg>           | Sends a DM to you when the given duration is up with your message that you assigned.```"
	)


# Responds to a user with "Pong!" when a user uses the command ".ping".
@client.command()
@commands.cooldown(1, 10, commands.BucketType.user)
async def ping(ctx):
	await ctx.channel.send("Pong!")


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
async def mute(ctx, member, *, reason="No reason specified"):
	# mutedRole = discord.Permissions()
	# mutedRole.update(send_messages=False)
	guild = ctx.guild
	user = ctx.message.mentions[0]

	# Checks if a user already has the role.
	for role in user.roles:
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
			await user.add_roles(role)
			await ctx.channel.send(f":white_check_mark: Successfully muted {user} for '{reason}'.")


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
async def unmute(ctx, member):
	guild = ctx.guild
	user = ctx.message.mentions[0]

	# Checks if the user doesn't have the required role.
	if "Muted" not in [role.name for role in user.roles]:
		await ctx.channel.send(":x: This user cannot be unmuted because they're not muted!")
		return

	# Removes the role.
	for role in guild.roles:
		if role.name == "Muted":
			await user.remove_roles(role)
			await ctx.channel.send(f":white_check_mark: Successfully unmuted {user}.")


# Sends an error if the user doesn't pass in a required argument.
@unmute.error
async def unmute_error(ctx, error):
	if isinstance(error, commands.MissingRequiredArgument):
		await ctx.channel.send(":warning: Missing required argument: `@user`. Syntax: `.unmute <@user/id>`.")
	elif isinstance(error, commands.MissingPermissions):
		await ctx.channel.send(":x: You do not have the `Manage Messages` permission.")


# Mutes a user temporarily.
@client.command()
@commands.cooldown(1, 10, commands.BucketType.user)
@commands.has_permissions(manage_messages=True)
async def tempmute(ctx, member, sec: int, *, reason="No reason specified"):
	guild = ctx.guild
	user = ctx.message.mentions[0]

	# Checks if a user already has the role.
	for role in user.roles:
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
			await user.add_roles(role)
			await ctx.channel.send(f":white_check_mark: Successfully muted {user} for {sec}s for the reason: '{reason}'.")
			await asyncio.sleep(sec)
			await user.remove_roles(role)

@tempmute.error
async def tempmute_error(ctx, error):
	if isinstance(error, commands.MissingRequiredArgument):
		await ctx.channel.send(":warning: Missing required argument(s) Syntax: `.tempmute <@user/id> <dur:sec> <reason>`")


# When used, this will send the report to the RECEIVER (aka me!).
@client.command()
@commands.cooldown(1, 10, commands.BucketType.user)
async def report(ctx, member, *, reason):
	receiver = await client.fetch_user(371802974470668321)
	user = ctx.message.mentions[0]
	reports = []
	if user == receiver:
		await ctx.channel.send(":x: This user cannot be reported. Try someone else.")
	else:
		reports.append(user)
		await discord.DMChannel.send(receiver, f"New Report!```\nUser: {user}\nReason: {reason}\nReport #{len(reports)}```")
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
	await ctx.channel.send(":white_check_mark: Word filtered. When a message has this word, the message will be deleted.")
	save(filtered_words)
	print(filtered_words)

@filterword.error
async def filterword_error(ctx, error):
	if isinstance(error, commands.MissingRequiredArgument):
		await ctx.channel.send(":warning: Missing required argument: `word`. Syntax: `.filterword <word>`")

# Bans a user.
@client.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member, *, reason=None):
	banned_users = await ctx.guild.bans()
	user = ctx.message.mentions[0]

	await user.ban(reason=reason)
	await ctx.channel.send(f":white_check_mark: Successfully banned {user} for {reason}.")
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
		await ctx.channel.send(":warning: Missing required argument: `@user/id`. Syntax: `.unban <@user/id>`")


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
		await ctx.channel.send(":warning: Missing required argument(s) Syntax: `.remind <dur:sec> <msg>")

# -----------------------------------------------------------------------

# Run the bot...
client.run(bot_token)