from time import perf_counter

import discord
from discord.ext import commands

from ..bot import Menel
from ..utils import embeds
from ..utils.context import Context
from ..utils.formatting import code


class Bot(commands.Cog):
    @commands.command()
    @commands.cooldown(2, 5, commands.BucketType.user)
    async def ping(self, ctx: Context):
        """Mierzy czas wysyłania wiadomości"""
        start = perf_counter()
        message = await ctx.send('Pong!')
        stop = perf_counter()

        embed = discord.Embed(
            description=f'Ogólne opóźnienie wiadomości: '
                        f'{(message.created_at.timestamp() - ctx.message.created_at.timestamp()) * 1000:,.0f} ms\n'
                        f'Czas wysyłania wiadomości: {(stop - start) * 1000:,.0f} ms\n'
                        f'Opóźnienie WebSocket: {ctx.bot.latency * 1000:,.0f} ms',
            color=discord.Color.green()
        )

        await message.edit(content=None, embed=embed)

    @commands.group(invoke_without_command=True)
    @commands.guild_only()
    async def prefix(self, ctx: Context):
        """Komendy służące do zarządzania prefixami"""
        await ctx.send(
            embed=embeds.with_author(
                ctx.author,
                title='Prefixy na tym serwerze',
                description=await ctx.get_prefixes_str(join='\n'),
                color=discord.Color.green()
            )
        )

    @prefix.command(name='set', aliases=['ser'])
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def prefix_set(self, ctx: Context, *prefixes: str):
        """Ustawia prefixy bota"""
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

        await ctx.db.set_prefixes(ctx.guild.id, prefixes)
        await ctx.embed(f"Ustawiono prefixy: {' '.join(map(code, prefixes))}")

    @prefix.command(name='reset')
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def prefix_reset(self, ctx: Context):
        """Resetuje prefixy bota"""
        await ctx.db.reset_prefixes(ctx.guild.id)
        await ctx.embed('Zresetowano prefixy')


def setup(bot: Menel):
    bot.add_cog(Bot())