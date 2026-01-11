from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from consts import *
from callbacks import *
from classes import *


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
                                 callback_data=RoomActionsCb(action='leave', room_id=room_id).pack()),
            InlineKeyboardButton(text='Начать игру',
                                 callback_data=RoomActionsCb(action='start', room_id=room_id).pack())

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
                                 callback_data=RoomActionsCb(action='leave', room_id=room_id).pack()),
            InlineKeyboardButton(text='Start the game',
                                 callback_data=RoomActionsCb(action='start', room_id=room_id).pack())
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
    keyboard.inline_keyboard[0].append(InlineKeyboardButton(text='Назад',
                                                            callback_data=RoomSettingsCb(setting='cancel',
                                                                                         room_id=room.id).pack()))
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


async def generate_night_action_kb(room: Room, player: User):
    inline_keyboard = []
    for target in room.users.values():
        cb = NightActionCb(target_id=target.id, player_id=player.id).pack()
        button = InlineKeyboardButton(text=target.username, callback_data=cb)
        inline_keyboard.append(button)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[inline_keyboard])
    return keyboard

async def generate_day_voting_kb(room: Room, player: User, victims: [User]=None):
    inline_keyboard = []
    if victims is not None:
        for victim in victims:
            cb = DayVotingCb(target_id=victim.id, player_id=player.id).pack()
            button = InlineKeyboardButton(text=victim.username, callback_data=cb)
            inline_keyboard.append(button)
        keyboard = InlineKeyboardMarkup(inline_keyboard=[inline_keyboard])
    else:
        for victim in room.users.values():
            cb = DayVotingCb(target_id=victim.id, player_id=player.id).pack()
            button = InlineKeyboardButton(text=victim.username, callback_data=cb)
            inline_keyboard.append(button)
        keyboard = InlineKeyboardMarkup(inline_keyboard=[inline_keyboard])
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
                            EN: "Choose setting"},
    'too_many_roles': {RU: "У вас добавлено слишком много ролей, уменьшите их количество или пригласите еще людей",
                       EN: "You've got too many roles added, remove some or invite more players"},
    'too_many_players': {RU: 'У вас слишком много игроков, увеличьте количество ролей',
                         EN: "You've got too many players, increase roles amount"},
    'your_role_is': {RU: 'Ваша роль: {0}, {1}',
                     EN: "Your role is: {0}, {1}"},
    'your_teammates_are': {RU: "С вами в команде: {0}",
                           EN: "You are playing with: 0{}"},
    'choose_target': {RU: "Выберите, на кого применить свое действие",
                      EN: "Choose target for your action"},
    'choose_voting': {RU: "Выберите, игрока, которого вы хотите исключить",
                      EN: "Vote for the player to kick"},
    're_vote': {RU: "Несколько человек с равным количеством голосов, выберите из них того, кого вы хотели бы исключить",
                EN: 'Several people with the same number of votes, choose from them the one you would like to kick'},
    'action_done': {RU: "Ваше действие засчитано, ожидайте остальных игроков",
                    EN: "Your action was accepted, wait for the other players"},
    'voting_done': {RU: "Ваш голос засчитан, ожидайте остальных игроков",
                    EN: "Your vote is accepted, wait for the other players"},
    'day_voting_kicked': {RU: "Голосованием выгнан игрок {0}",
                          EN: "{0} was kicked by the voting"},
    MAFIA_WON: {RU: "Мафия получила большинство среди игроков. Победа мафии",
                EN: "mafia gained a majority among the players. Mafia won"},
    CIVILIANS_WON: {RU: "Мирные изгнали все отрицательные и нейтральные роли. Победа мирных",
                    EN: "civilians have driven out all the negative and neutral roles. Civilians won"}
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
