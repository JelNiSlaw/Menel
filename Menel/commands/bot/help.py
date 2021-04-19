from collections import defaultdict

import discord

from ...functions import code
from ...objects import Category, Command, Message, commands


COMMAND = Command(
    'help',
    syntax=None,
    description='Wyświetla pomoc.',
    category=Category.BOT,
    cooldown=3,
)


def setup(cliffs):
    @cliffs.command('help', command=COMMAND)
    async def command(m: Message, prefix):
        categories = defaultdict(list)

        for c in commands.values():
            categories[c.category].append(c)

        embed = discord.Embed(
            title='Pomoc',
            description=f'Prefix: {code(prefix)}',
            colour=discord.Colour.blurple()
        )

        embed.set_thumbnail(url=m.bot.user.avatar.replace(256))

        for category, cmds in categories.items():
            if value := ' '.join(code(c.name) for c in cmds if not c.hidden):
                embed.add_field(
                    name=category.value,
                    value=value,
                    inline=False
                )

        await m.send(embed=embed)