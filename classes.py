from consts import *
from typing import Union


class User:
    """Класс пользователя"""

    def __init__(self, lang: int, state: int, tg_id: int, username: str):
        self.language = lang
        self.state = state
        self.id = tg_id
        self.username = username
        self.current_room = None
        self.is_alive = True
        self.is_healed = False
        self.role = None
        self.made_move = False

    def set_language(self, lang: int) -> None:
        self.language = lang

    def set_state(self, state: int):
        self.state = state


class Users:
    """Класс группы пользователей"""

    def __init__(self):
        self.users = {}

    def get_user(self, tg_id: int) -> Union[User, None]:
        if tg_id in self.users:
            return self.users[tg_id]
        return None

    def create_user(self, tg_id: int, lang: int, state: int, username: str) -> User:
        self.users[tg_id] = User(lang, state, tg_id, username)
        return self.users[tg_id]

    def __str__(self) -> str:
        return ' '.join(map(str, self.users.keys()))

    def __len__(self) -> int:
        return len(self.users)

    def __contains__(self, item: Union[int, User]):
        """Принимает класс пользователя или его tg_id"""
        if item.__class__ == int:
            if item in self.users:
                return True
            return False
        if item in self.users.values():
            return True
        return False

    def __getitem__(self, user_id: int) -> Union[User, None]:
        if user_id in self.users:
            return self.users[user_id]
        return None


class Room(Users):
    def __init__(self, owner: User, room_id: int, token: str):
        super().__init__()
        self.owner: User = owner
        self.day_state: int = DAY
        self.day = 0
        self.add_user(owner)
        self.id = room_id
        self.token = token
        self.settings = {'doReveal': True}
        self.available_roles = {Doctor: 0, Civilian: 0, Mafia: 0}
        self.is_active = False
        self.teams = {}
        self.teams_votes = {}
        self.users: dict[int, User]
        self.day_voting: dict[User, int] = {}

    def set_setting(self, setting, value):
        self.settings[setting] = value

    def add_user(self, user: User) -> None:
        self.users[user.id] = user
        user.current_room = self

    def kick(self, user: User):
        self.users.pop(user.id)
        user.current_room = None

    def destroy(self):
        for user in self.users.values():
            user.current_room = None
        self.users: dict[int, User] = {}


class Role:
    name = {RU: 'Роль', EN: "Role"}
    is_day = False
    is_night = False
    id = -1
    side = BAD
    is_team = False
    description = {RU: "Описание", EN: "Description"}

    def __init__(self, room: Room):
        self.room = room

    def night_action(self, victim_id: int):
        ...

    def day_action(self, victim_id: int):
        ...


class Mafia(Role):
    name = {RU: 'Мафия', EN: "Mafia"}
    is_day = False
    is_night = True
    id = 1
    side = BAD
    is_team = True
    description = {
        RU: "При игре за мафию вам нужно убить всех, кроме других мафий. Ночью вы голосуете и убиваете любого игрока",
        EN: "When playing the mafia role you need to kill everyone, except other mafias. At night you all vote and kill one player"}

    def __init__(self, room: Room):
        super().__init__(room)

    def night_action(self, victim_id: int):
        self.room.users[victim_id].is_shot = 1


class Doctor(Role):
    name = {RU: 'Доктор', EN: "Doctor"}
    is_day = False
    is_night = True
    id = 2
    side = GOOD
    is_team = False
    description = {RU: "При игре за доктора ваша задача помогать мирным, леча тех, кого попробует убить мафия. Ночью вы выбираете игрока, которого вы спасете от выстрела мафии",
                   EN: "When playing the doctor role your goal is to help civilians an heal players, whose gonna be killed by mafia. At night you choose one player and save him from mafias shot"}

    def __init__(self, room: Room):
        super().__init__(room)

    def night_action(self, victim_id: int):
        self.room.users[victim_id].is_shot = 0


class Civilian(Role):
    name = {RU: 'Мирный', EN: "Civilian"}
    is_day = False
    is_night = False
    id = 0
    side = GOOD
    is_team = False
    description = {RU: "При игре за мирного ваша задача вычислить и изгнать все отрицательные (мафия) и нейтральные (маньяк и т.п.) роли на дневных голосованиях",
                   EN: "When playing the civilian role your goal is to expose and kick all bad (mafia) and neutral (killer, etc.) roles at the day votings"}

    def __init__(self, room: Room):
        super().__init__(room)
