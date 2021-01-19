import aiohttp

from ...objects.message import Message


def setup(cliffs):
    @cliffs.command('dlist|dlist.top|dlista|votes|głosy', name='dlist', cooldown=5)
    async def command(m: Message):
        async with aiohttp.request(
                'GET', f'https://api.dlist.top/v1/servers/{m.guild.id}', timeout=aiohttp.ClientTimeout(total=20)
        ) as this_guild:
            if this_guild.status != 200:
                await m.error('Ten serwer nie został dodany na DList.top, lub nie udało się pobrać jego danych.')
                return
            else:
                this_guild = await this_guild.json()
                if this_guild.get('status') != 'success':
                    await m.error(
                        {
                            'not found': 'Ten serwer nie został dodany na DList.top.'
                        }.get(this_guild.get('error'), this_guild.get('error', 'DList.top nie zwróciła treści błędu.'))
                    )
                    return

        async with aiohttp.request(
                'GET', f'https://api.dlist.top/v1/servers/list/top/0?limit=1', timeout=aiohttp.ClientTimeout(total=20)
        ) as top_guild:
            if top_guild.status != 200:
                await m.error('Nie udało się pobrać danych pierwszego serwera.')
                return
            else:
                top_guild = await top_guild.json()
                if top_guild.get('status') != 'success':
                    await m.error('Podczas pobierania danych pierwszego serwera DList.top zwórciła błąd: ' +
                                  top_guild.get('error') + '.')
                    return

        this_votes = this_guild["data"].get("votes", "?")
        top_votes = top_guild["data"][0].get("votes", "?")
        if isinstance(this_votes, int) and isinstance(top_votes, int):
            percent = round((this_votes / top_votes) * 100, 1)
        else:
            percent = '?'

        await m.info(f'Głosy tego serwera: {this_votes}\n'
                     f'Głosy pierwszego serwera: {top_votes}\n'
                     f'Procent głosów pierwszego serwera: {percent}%'
        )