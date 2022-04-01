#!/usr/bin/python3

import discord
from discord.ext import commands
from extra import DotDict
from dotenv import dotenv_values

config = DotDict({
	**dict(dotenv_values('example.env')),
	**dict(dotenv_values('.env')),
})

client = commands.Bot(command_prefix='s!',help_command=None)

# constants, probably should be loaded from a config file or made unconstant
STARBOARD_CHANNEL = 869052275816017952
PIN_EMOJIS = {"📌","⭐"} # pushpin emoji and star emoji

async def pin_message(message:discord.Message,starboard:discord.TextChannel,pin_author:discord.abc.User):
	embed = discord.Embed(
		title=f"#{message.channel}",
		description=message.content,
		url=f"https://discord.com/channels/{message.guild.id}/{message.channel.id}"
	)
	embed.set_author(name=message.author.display_name,icon_url=str(message.author.avatar))
	# embed.set_footer(text=f"[Jump]({message.jump_url})")
	embed.add_field(name="Original Message:",value=f"[Jump]({message.jump_url})")
	if len(message.attachments) > 0: embed.set_image(url=message.attachments[0].url)
	await starboard.send(embed=embed,content=f"pinned by <@{pin_author.id}>",allowed_mentions=discord.AllowedMentions.none())
	await message.channel.send(embed=discord.Embed(description=f"{pin_author.display_name} has pinned [a message]({message.jump_url}) to this channel. See all [pinned messages](https://discord.com/channels/{starboard.guild.id}/{STARBOARD_CHANNEL})."))

@client.event
async def on_ready():
	print(f"logged in as {client.user}")

@client.event
async def on_raw_reaction_add(payload:discord.RawReactionActionEvent):
	if payload.emoji.name not in PIN_EMOJIS: return
	message:discord.Message = await (client.get_channel(payload.channel_id).get_partial_message(payload.message_id)).fetch()
	starboard:discord.TextChannel = client.get_channel(STARBOARD_CHANNEL)
	for reaction in message.reactions:
		if reaction.count > 1:
			return
	pin_author = (await message.reactions[0].users(limit=1).flatten())[0]
	await pin_message(message,starboard,pin_author)

@client.event
async def on_raw_message_edit(payload:discord.RawMessageUpdateEvent):
	"""
	REQUIREMENTS:
	- Get message
	- Get starboard
	- pin_message(message,starboard)
	"""
	message:discord.Message = await (client.get_channel(payload.channel_id).get_partial_message(payload.message_id)).fetch()
	if not message.pinned: return
	starboard:discord.TextChannel = client.get_channel(STARBOARD_CHANNEL)
	async for entry in client.get_guild(payload.guild_id).audit_logs(limit=1,action=discord.AuditLogAction.message_pin):
		author = entry.user
	await message.unpin()
	await pin_message(message,starboard,author)

@client.event
async def on_message(message:discord.Message):
	if message.type == discord.MessageType.pins_add: await message.delete()

client.run(config.TOKEN)
