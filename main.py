import discord
from discord.ext import commands
from extra import DotDict
from dotenv import dotenv_values

config = DotDict({
	**dict(dotenv_values('example.env')),
	**dict(dotenv_values('.env')),
})

client = commands.Bot(command_prefix='s!')

# constants, probably should be loaded from a config file or made unconstant
STARBOARD_CHANNEL = 869052275816017952
PIN_EMOJIS = {"📌","⭐"} # pushpin emoji and star emoji

async def pin_message(message:discord.Message,starboard:discord.TextChannel):
	embed = discord.Embed(
		title=f"#{message.channel}",
		description=message.content,
		url=f"https://discord.com/channels/{message.guild.id}/{message.channel.id}"
	)
	embed.set_author(name=message.author.display_name,icon_url=message.author.avatar_url)
	# embed.set_footer(text=f"[Jump]({message.jump_url})")
	embed.add_field(name="Original Message:",value=f"[Jump]({message.jump_url})")
	if len(message.attachments) > 0: embed.set_image(url=message.attachments[0].url)
	await starboard.send(embed=embed,content=f"pinned by <@{(await message.reactions[0].users().flatten())[0].id}>",allowed_mentions=discord.AllowedMentions.none())
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
	await pin_message(message,starboard)
	# embed = discord.Embed(
	# 	title=f"#{message.channel}",
	# 	description=message.content,
	# 	url=f"https://discord.com/channels/{message.guild.id}/{message.channel.id}"
	# )
	# embed.set_author(name=message.author.display_name,icon_url=message.author.avatar_url)
	# # embed.set_footer(text=f"[Jump]({message.jump_url})")
	# embed.add_field(name="Original Message:",value=f"[Jump]({message.jump_url})")
	# if len(message.attachments) > 0: embed.set_image(url=message.attachments[0].url)
	# await starboard.send(embed=embed,content=f"pinned by <@{(await message.reactions[0].users().flatten())[0].id}>",allowed_mentions=discord.AllowedMentions.none())

@client.event
async def on_message(message:discord.Message):
	if message.type != discord.MessageType.pins_add: return
	print(message.content)

client.run(config.TOKEN,bot=config.BOT)