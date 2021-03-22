import asyncio

from ..objects import Message


EMOJIS = ('👍', '👎')


async def ask_for_confirmation(m: Message, text: str) -> bool:
    msg = Message(await m.info(text))

    m.bot.loop.create_task(msg.add_reactions(EMOJIS))

    result = False

    try:
        reaction = await m.bot.wait_for(
            'raw_reaction_add',
            check=lambda r: r.event_type == 'REACTION_ADD' and
                            r.user_id == m.author.id and
                            r.message_id == msg.id and
                            r.channel_id == msg.channel.id and
                            r.emoji.name in EMOJIS,
            timeout=30
        )
    except asyncio.TimeoutError:
        pass

    else:
        if reaction.emoji.name == EMOJIS[0]:
            result = True

    m.bot.loop.create_task(msg.delete())

    return result