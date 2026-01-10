from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from aiogram.filters.callback_data import CallbackData, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder, KeyboardButton
from typing import Union

RU = 0
EN = 1
DAY = 0
NIGHT = 1
DEFAULT_STATE = 0
JOINING_ROOM_STATE = 1


class RolesAddingCb(CallbackData, prefix='RoleAdding'):
    role_id: int
    room_id: int


class RoleAddCb(CallbackData, prefix='RoleAdd'):
    role_id: int
    room_id: int
    value: int


class LangCb(CallbackData, prefix='lang'):
    language: int


class JoinRoomCb(CallbackData, prefix='JoinRoom'):
    ...


class RoomCreationCb(CallbackData, prefix='RoomCreation'):
    ...


class RoomActionsCb(CallbackData, prefix='RoomActions'):
    action: str
    room_id: int


class RoomSettingsCb(CallbackData, prefix='RoomSettings'):
    setting: str
    room_id: int


class RoomSettingCb(CallbackData, prefix="RoomSetting"):
    setting: str
    value: int
    room_id: int


class UserSettingsCb(CallbackData, prefix='UserSettings'):
    ...


class UserSettingCb(CallbackData, prefix='UserSettings'):
    setting: str


async def generate_room_actions_cb(room_id: int, language: int):
    if language == RU:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text='Пригласить пользователей',
                                 callback_data=RoomActionsCb(action='invite', room_id=room_id).pack()),
            InlineKeyboardButton(text='Редактировать роли',
                                 callback_data=RoomActionsCb(action='roles', room_id=room_id).pack()),
            InlineKeyboardButton(text='Настройки комнаты',
                                 callback_data=RoomActionsCb(action='settings', room_id=room_id).pack()),
            InlineKeyboardButton(text='Выйти из комнаты',
                                 callback_data=RoomActionsCb(action='leave', room_id=room_id).pack())
        ]])
    else:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text='Invite users',
                                 callback_data=RoomActionsCb(action='invite', room_id=room_id).pack()),
            InlineKeyboardButton(text='Edit roles',
                                 callback_data=RoomActionsCb(action='roles', room_id=room_id).pack()),
            InlineKeyboardButton(text='Room settings',
                                 callback_data=RoomActionsCb(action='settings', room_id=room_id).pack()),
            InlineKeyboardButton(text='Leave the room',
                                 callback_data=RoomActionsCb(action='leave', room_id=room_id).pack())
        ]])
    return keyboard


async def generate_room_settings_kb(room_id: int, language: int):
    if language == RU:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text='Раскрытие ролей при смерти',
                                 callback_data=RoomSettingsCb(setting='doReveal', room_id=room_id).pack()),
            InlineKeyboardButton(text='Назад', callback_data=RoomSettingsCb(setting='cancel', room_id=room_id).pack())
        ]])
    else:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text='Roles revealing after death',
                                 callback_data=RoomSettingsCb(setting='doReveal', room_id=room_id).pack()),
            InlineKeyboardButton(text='Go back', callback_data=RoomSettingsCb(setting='cancel', room_id=room_id).pack())

        ]])
    return keyboard


async def roles_choose_generator_kb(room, language):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[]])
    for role in room.available_roles:
        keyboard.inline_keyboard[0].append(
            InlineKeyboardButton(text=role.name[language],
                                 callback_data=RolesAddingCb(room_id=room.id, role_id=role.id).pack()))
    return keyboard

async def generate_role_adding_kb(role_id, room_id, language):
    if language == RU:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text='Добавить',
                                 callback_data=RoleAddCb(role_id=role_id, value=1, room_id=room_id).pack()),
            InlineKeyboardButton(text='Убрать',
                                 callback_data=RoleAddCb(role_id=role_id, value=-1, room_id=room_id).pack()),

            InlineKeyboardButton(text='Назад',
                                 callback_data=RoomActionsCb(action='roles', room_id=room_id).pack()),

        ]])
    else:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text='Add', callback_data=RoleAddCb(role_id=role_id, value=1, room_id=room_id).pack()),
            InlineKeyboardButton(text='Remove',
                                 callback_data=RoleAddCb(role_id=role_id, value=-1, room_id=room_id).pack()),
            InlineKeyboardButton(text='Go back',
                                 callback_data=RoomActionsCb(action='roles', room_id=room_id).pack()),

        ]])
    return keyboard

async def generate_room_setting_kb(room_id: int, setting: str, language: int):
    if setting == 'doReveal':
        if language == RU:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(text='Раскрывать',
                                     callback_data=RoomSettingCb(setting='doReveal', value=1, room_id=room_id).pack()),
                InlineKeyboardButton(text='НЕ Раскрывать',
                                     callback_data=RoomSettingCb(setting='doReveal', value=0, room_id=room_id).pack()),
                InlineKeyboardButton(text='Назад',
                                     callback_data=RoomSettingsCb(setting='cancel', room_id=room_id).pack())

            ]])
        else:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(text='Reveal',
                                     callback_data=RoomSettingCb(setting='doReveal', value=1, room_id=room_id).pack()),
                InlineKeyboardButton(text='DO NOT Reveal',
                                     callback_data=RoomSettingCb(setting='doReveal', value=0, room_id=room_id).pack()),
                InlineKeyboardButton(text='Go back',
                                     callback_data=RoomSettingsCb(setting='cancel', room_id=room_id).pack())

            ]])
    elif setting == 'cancel':
        return InlineKeyboardMarkup(inline_keyboard=[[]])
    else:
        raise NotImplementedError
    return keyboard


class User:
    """Класс пользователя"""

    def __init__(self, lang: int, state: int, tg_id: int):
        self.language = lang
        self.state = state
        self.id = tg_id
        self.current_room = None
        self.isShot = False
        self.isAlive = True

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

    def create_user(self, tg_id: int, lang: int, state: int) -> User:
        self.users[tg_id] = User(lang, state, tg_id)
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
        self.add_user(owner)
        self.id = room_id
        self.token = token
        self.settings = {'doReveal': True}
        self.available_roles = {Doctor: 0, Civilian: 0, Mafia: 0}

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
        self.users = {}


class Role:
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

    def __init__(self, room: Room):
        super().__init__(room)

    def night_action(self, victim_id: int):
        self.room.users[victim_id].isShot = 1


class Doctor(Role):
    name = {RU: 'Доктор', EN: "Doctor"}
    is_day = False
    is_night = True
    id = 2

    def __init__(self, room: Room):
        super().__init__(room)

    def night_action(self, victim_id: int):
        self.room.users[victim_id].isShot = 0


class Civilian(Role):
    name = {RU: 'Мирный', EN: "Civilian"}
    is_day = False
    is_night = False
    id = 0

    def __init__(self, room: Room):
        super().__init__(room)


TEXTS = {
    'choose_language': "Выберите язык/Choose language",
    'language_changed': {RU: 'Язык успешно изменен',
                         EN: 'Language Successfully changed'},
    'startup': {RU: "Выберите действие",
                EN: "Choose action"},
    'already_joined': {RU: 'Вы уже присоединились к другой комнате',
                       EN: "You've already joined another room"},
    'change_role_amount': {RU: "Сейчас в комнате {0} {1}",
                           EN: "Currently there are {0} {1}"},
    'choose_role': {RU: "Выберите роль для изменения количества",
                    EN: "Choose role to change amount"},

    'room_actions': {RU: "Действия комнаты",
                     EN: "Room actions"},
    'enter_token': {RU: 'Введите токен для присоединения к комнате или "отмена", чтобы вернуться в меню',
                    EN: 'Enter the token to join the room, or type "cancel" to go back to the menu'},
    'room_invite': {
        RU: "Для приглашения пользователя, зарегистрированного в боте, отправьте ему ссылку https://t.me/MyMafioziBot?start={0} или ключ {1}",
        EN: "To invite user, who is already registered in the bot, send him this link: https://t.me/MyMafioziBot?start={0}, or use the key: {1}"},
    'forbidden_action': {RU: 'У вас нет прав на это действие',
                         EN: "You dont have rights for this action"},
    'room_left': {RU: 'Вы покинули комнату',
                  EN: "You've left the room"},
    'room_deleted': {RU: "Вы уже вышли из комнаты или она удалена",
                     EN: "You've already left the room or it is deleted"},
    'setting_change': {RU: "Выберите значение настройки",
                       EN: "Choose the setting value"},
    'setting_changed': {RU: "Настройка успешно изменена",
                        EN: "Setting has been successfully changed"},
    'room_settings': {RU: 'Выберите настройку для изменения',
                      EN: "Choose setting to edit"},
    'room_join_owner': {RU: 'К комнате присоединяется пользователь {0}',
                        EN: '{0} joins the room'},
    'room_join': {RU: 'Вы присоединились к комнате',
                  EN: "You've joined the room"},
    'wrong_token': {RU: "Неверный токен/ссылка для подключения, или комната удалена",
                    EN: "Wrong token/link for connection, or the room is deleted"},
    'choose_user_setting': {RU: 'Выберите настройку',
                            EN: "Choose setting"}
}
KEYBOARDS = {
    'choose_language': InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text='🇷🇺Русский', callback_data=LangCb(language=RU).pack()),
        InlineKeyboardButton(text='🇺🇸English', callback_data=LangCb(language=EN).pack())]]),
    'startup': {
        RU: InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text='Создать комнату', callback_data=RoomCreationCb().pack()),
            InlineKeyboardButton(text='Присоединиться к комнате', callback_data=JoinRoomCb().pack()),
            InlineKeyboardButton(text='Настройки', callback_data=UserSettingsCb().pack())
        ]]),
        EN: InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text='Create room', callback_data=RoomCreationCb().pack()),
            InlineKeyboardButton(text='Join room', callback_data=JoinRoomCb().pack()),
            InlineKeyboardButton(text='Settings', callback_data=UserSettingsCb().pack())
        ]])
    },
    'choose_user_setting': {
        RU: InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text='Язык', callback_data=UserSettingCb(setting='language').pack())
        ]]),
        EN: InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text='Language', callback_data=UserSettingCb(setting='language').pack())
        ]])

    },

}
