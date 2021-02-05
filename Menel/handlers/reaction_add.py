import discord

from ..objects import Menel


def setup(bot: Menel):
    @bot.event
    async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
        if payload.user_id == bot.owner and payload.emoji.name == '🗑️':
            try:
                message = await (await bot.fetch_channel(payload.channel_id)).fetch_message(payload.message_id)
                if message.author == bot.user:
                    await message.delete()
            except discord.HTTPException as e:
                print(e)