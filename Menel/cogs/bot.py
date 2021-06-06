from time import perf_counter

import discord
from discord.ext import commands

from ..objects.context import Context


class Bot(commands.Cog):
    @commands.command()
    async def ping(self, ctx: Context):
        start = perf_counter()
        message = await ctx.send('Pong!')
        stop = perf_counter()

        embed = discord.Embed(
            description=f'Ogólne opóźnienie wiadomości: '
                        f'{round((message.created_at.timestamp() - ctx.message.created_at.timestamp()) * 1000)} ms\n'
                        f'Czas wysyłania wiadomości: {round((stop - start) * 1000)} ms\n'
                        f'Opóźnienie WebSocket: {round(ctx.bot.latency * 1000)} ms',
            colour=discord.Colour.blurple()
        )

        await message.edit(content=None, embed=embed)


def setup(bot):
    bot.add_cog(Bot())