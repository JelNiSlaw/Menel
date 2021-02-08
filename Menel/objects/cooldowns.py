from collections import defaultdict
from datetime import datetime, timedelta
from typing import Optional

from ..objects import bot


class Cooldowns:
    def __init__(self):
        self.cooldowns = defaultdict(dict)


    def get(self, user_id: int, command: str, include_owner: bool = False) -> Optional[float]:
        if user_id not in self.cooldowns or command not in self.cooldowns[user_id]:
            return None

        if user_id == bot.owner and not include_owner:
            return None

        if self.cooldowns[user_id][command] <= datetime.utcnow().timestamp():
            return None
        else:
            return self.cooldowns[user_id][command] - datetime.utcnow().timestamp()


    def set(self, user_id: int, command: str, time: Optional[int]) -> None:
        if time:
            self.cooldowns[user_id][command] = (datetime.utcnow() + timedelta(seconds=time)).timestamp()


    def auto(self, user_id: Optional[int], command: str, time: int, *, include_owner: bool = False) -> Optional[float]:
        cooldown = self.get(user_id, command, include_owner=include_owner)

        if not cooldown:
            self.set(user_id, command, time)

        return cooldown


cooldowns = Cooldowns()