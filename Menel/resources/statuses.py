import random

import discord


STATUSES = [
    lambda bot: f'{sum(g.member_count for g in bot.guilds):,} użytkowników',
    lambda bot: f'{len(bot.guilds):,} serwerów',
    lambda bot: f'{sum(len(g.channels) for g in bot.guilds):,} kanałów',
    lambda bot: f'WebSocket: {round(bot.latency * 1000):,}ms'
]


def random_status(bot: discord.Client) -> str:
    return random.choice(STATUSES)(bot)