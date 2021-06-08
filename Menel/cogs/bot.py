from time import perf_counter

import discord
from discord.ext import commands

from ..objects.context import Context
from ..utils import embeds
from ..utils.formatting import code


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

    @commands.group(invoke_without_command=True)
    async def prefix(self, ctx: Context):
        prefixes = await ctx.db.get_prefixes(ctx.guild)
        description = '\n'.join([code('@' + ctx.bot.user.name)] + list(map(code, prefixes)))
        await ctx.send(
            embed=embeds.with_author(
                ctx.author,
                title='Prefixy na tym serwerze',
                description=description,
                colour=discord.Colour.blue()
            )
        )

    @prefix.command(name='set', aliases=['ser'])
    @commands.has_permissions(manage_guild=True)
    async def prefix_set(self, ctx: Context, *prefixes: str):
        prefixes = list(set(prefixes))

        if len(prefixes) > 50:
            await ctx.error('Możesz ustawić maksymalnie 50 prefixów (po co ci tyle?)')
            return

        for prefix in prefixes:
            if len(prefix) > 20:
                await ctx.error('Prefix nie może być dłuższy niż 20 znaków')
                return

            if '`' in prefix:
                await ctx.error('Prefix nie może zawierać znaku **`**')
                return

            if prefix.endswith('\\'):
                await ctx.error('Prefix nie może kończyć się znakiem **\\**')
                return

        await ctx.db.set_prefixes(ctx.guild, prefixes)
        await ctx.success(f"Ustawiono prefixy {' '.join(map(code, prefixes))}")

    @prefix.command(name='reset')
    @commands.has_permissions(manage_guild=True)
    async def prefix_reset(self, ctx: Context):
        await ctx.db.reset_prefixes(ctx.guild)
        await ctx.success('Zresetowano prefixy')


def setup(bot):
    bot.add_cog(Bot())