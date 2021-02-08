import random

from ..objects import cooldowns, Message


async def respond(m: Message):
    if 'wafelki' in m.content.split() and \
            random.random() < 0.5 and \
            not cooldowns.auto(None, '_autoresponders', 5, include_owner=True):
        await m.send(random.choice((
            '<:wafelki:808343862384787466>',
            '<a:wafelki_spin:808344860398583868>',
            '<a:wafelki_spin_2:808344872229535784>',
            '<a:wafelki_cube:808344894711398430>',
            '<a:wafelki_pyramid:808344907902746664>'
        )))