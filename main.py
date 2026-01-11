from aiogram import Bot, Dispatcher
from aiogram.types import Message, CallbackQuery
import dotenv
import os
import asyncio
import psycopg2
import secrets

from adds import *
from callbacks import *
from classes import *
import random

dotenv.load_dotenv('.env')
TOKEN = os.getenv('TOKEN', '')
dp = Dispatcher()
bot = Bot(TOKEN)
users = Users()
rooms = {}
ROLES = {0: Civilian, 1: Mafia, 2: Doctor}


# conn = psycopg2.connect(
#     host=os.getenv('DB_HOST'),
#     database=os.getenv('DB_NAME'),
#     user=os.getenv('DB_USER'),
#     password=os.getenv('DB_PASSWORD'),
#     port=os.getenv('DB_PORT')
# )


@dp.callback_query(LangCb.filter())
async def choose_language_handler(callback: CallbackQuery, callback_data: CallbackData):
    """Изменение языка"""
    await callback.answer()
    language = callback_data.language
    user_id = callback.message.chat.id
    if user_id in users:
        users[user_id].set_language(language)
    else:
        username = callback.message.chat.username
        users.create_user(user_id, language, DEFAULT_STATE, username)
    await callback.message.edit_text(TEXTS['language_changed'][language])
    user = users[user_id]
    if user.current_room is None:
        return await callback.message.answer(TEXTS['startup'][language], reply_markup=KEYBOARDS['startup'][language])

    keyboard = await generate_room_actions_cb(user.current_room, user.language, user)
    await callback.message.answer(TEXTS['room_actions'][user.language].format(', '.join("@" + x.username for x in user.current_room.users.values())), reply_markup=keyboard)

@dp.callback_query(JoinRoomCb.filter())
async def join_room_handler(callback: CallbackQuery, callback_data: CallbackData):
    """Вход нового пользователя в комнату"""
    await callback.answer()
    user = users[callback.message.chat.id]
    if user.current_room is not None:
        keyboard = await generate_room_actions_cb(user.current_room, user.language, user)
        return await callback.message.answer(TEXTS['already_joined'][user.language], reply_markup=keyboard)
    user.set_state(JOINING_ROOM_STATE)
    await callback.message.edit_text(TEXTS['enter_token'][user.language])


@dp.callback_query(RoomCreationCb.filter())
async def room_creation_handler(callback: CallbackQuery, callback_data: CallbackData):
    """Создание комнаты"""
    await callback.answer()
    user = users[callback.message.chat.id]
    if user.current_room is not None:
        keyboard = await generate_room_actions_cb(user.current_room, user.language, user)
        return await callback.message.answer(TEXTS['already_joined'][user.language], reply_markup=keyboard)
    room_id = len(rooms)
    token = secrets.token_urlsafe(16)
    room = Room(owner=user, room_id=room_id, token=token)
    rooms[room_id] = room
    keyboard = await generate_room_actions_cb(room, user.language, user)
    await callback.message.answer(TEXTS['room_actions'][user.language].format(', '.join("@" + x.username for x in user.current_room.users.values())), reply_markup=keyboard)


@dp.callback_query(RoomActionsCb.filter())
async def room_actions_handler(callback: CallbackQuery, callback_data: CallbackData):
    """Все действия в комнате для всех пользователей"""
    await callback.answer()
    action = callback_data.action
    user = users[callback.message.chat.id]
    try:
        room: Room = rooms[callback_data.room_id]
    except KeyError:
        await callback.message.edit_text(TEXTS['room_deleted'][user.language])
        await callback.message.answer(TEXTS['startup'][user.language], reply_markup=KEYBOARDS['startup'][user.language])
        return

    if action == 'invite':
        await callback.message.edit_text(TEXTS['room_invite'][user.language].format(room.token, room.token))

        keyboard = await generate_room_actions_cb(room, user.language, user)
        await callback.message.answer(TEXTS['room_actions'][user.language].format(', '.join("@" + x.username for x in user.current_room.users.values())), reply_markup=keyboard)

    elif action == 'start':
        roles_amount = sum(room.available_roles.values())
        players_amount = len(room.users)
        if roles_amount > players_amount:
            keyboard = await generate_room_actions_cb(room, user.language, user)
            text = TEXTS['too_many_roles'][user.language].format(roles_amount, roles_amount - players_amount)
            return await callback.message.edit_text(text, reply_markup=keyboard)
        if roles_amount < players_amount:
            keyboard = await generate_room_actions_cb(room, user.language, user)
            text = TEXTS['too_many_players'][user.language].format(players_amount, players_amount - roles_amount)
            return await callback.message.edit_text(text, reply_markup=keyboard)

        await room_preparation(room)  # Всё готово, начинаем игру

    elif action == 'settings':
        if room.owner == user:
            keyboard = await generate_room_settings_kb(room.id, user.language)
            await callback.message.edit_text(TEXTS['room_settings'][user.language], reply_markup=keyboard)
        else:
            await callback.message.edit_text(TEXTS['forbidden_action'][user.language])

            keyboard = await generate_room_actions_cb(room, user.language, user)
            await callback.message.answer(TEXTS['room_actions'][user.language].format(', '.join("@" + x.username for x in user.current_room.users.values())), reply_markup=keyboard)

    elif action == 'roles':
        if room.owner == user:
            keyboard = await roles_choose_generator_kb(room, user.language)
            await callback.message.edit_text(TEXTS['choose_role'][user.language], reply_markup=keyboard)

    elif action == 'leave':
        if room.owner == user:
            room.destroy()
            rooms.pop(room.id)
        else:
            room.kick(user)
        await callback.message.edit_text(TEXTS['room_left'][user.language])
        await callback.message.answer(TEXTS['startup'][user.language], reply_markup=KEYBOARDS['startup'][user.language])


async def room_preparation(room: Room):
    room.teams = {}
    available_roles = room.available_roles.copy()
    for player in room.users.values():
        player.is_alive = True
        player.role = None
        player.made_move = False
        while player.role is None:
            role = random.choice(tuple(room.available_roles.keys()))
            amount = room.available_roles[role]
            if amount > 0:
                player.role = role
                room.available_roles[role] -= 1

                if role.is_team:
                    if role in room.teams:
                        room.teams[role].append([player.username, player.id])
                    else:
                        room.teams[role] = [[player.username, player.id]]

        print(player.id, player.role)
    #  Роли распределены, готовы к игре
    room.available_roles = available_roles.copy()
    room.is_active = True
    """Уведомляем игроков об их ролях и сокомандниках"""
    for player in room.users.values():
        language = player.language
        role: Role = player.role
        text = TEXTS['your_role_is'][language].format(role.name[language], role.description[language])
        await bot.send_message(player.id, text)

        if role.is_team:
            teammates = ', '.join("@" + x[0] for x in room.teams[role])  # teammates usernames
            await bot.send_message(player.id, TEXTS['your_teammates_are'][language].format(teammates))
    await start_night(room)


async def start_night(room: Room):
    room.day_state = NIGHT
    for player in room.users.values():
        if player.role.is_night and player.is_alive:
            player.made_move = False
            keyboard = await generate_night_action_kb(room, player)
            await bot.send_message(player.id, TEXTS['choose_target'][player.language], reply_markup=keyboard)


@dp.callback_query(NightActionCb.filter())
async def night_actions_handler(callback: CallbackQuery, callback_data: CallbackData):
    player = users[callback_data.player_id]
    target = users[callback_data.target_id]

    role = player.role
    room: Room = player.current_room
    if role == Doctor:
        target.is_healed = True
    elif role == Mafia:
        if Mafia in room.teams_votes:
            room.teams_votes[Mafia].append(target.id)
        else:
            room.teams_votes[Mafia] = [target.id]
    await callback.message.edit_text(TEXTS['action_done'][player.language])

    player.made_move = True
    night_is_over = True
    for player in room.users.values():
        if not player.made_move and player.role.is_night:
            night_is_over = False
            break
    if night_is_over:
        await night_actions_processor(room)


async def night_actions_processor(room: Room):
    victim_id = random.choice(room.teams_votes[Mafia])
    victim = users[victim_id]
    if not victim.is_healed:
        victim.is_alive = False
        for player in room.users.values():
            await bot.send_message(player.id, TEXTS['player_killed'][player.language].format(victim.username))
            if room.settings['do_reveal']:
                text = TEXTS['role_reveal'][player.language].format(victim.role.name[player.language])
                await bot.send_message(player.id, text)

        await bot.send_message(victim.id, TEXTS['you_died'][victim.language])

    await game_ended_checker(room)
    if room.is_active:
        await day_voting_creator(room)


async def day_voting_creator(room: Room):
    room.day_state = DAY
    room.day += 1
    room.day_voting = {}
    for player in room.users.values():
        player.is_healed = False

        if player.is_alive:
            player.made_move = False
            keyboard = await generate_day_voting_kb(room, player)
            await bot.send_message(player.id, TEXTS['choose_voting'][player.language], reply_markup=keyboard)


@dp.callback_query(DayVotingCb.filter())
async def day_voting_handler(callback: CallbackQuery, callback_data: CallbackData):
    player = users[callback_data.player_id]
    target = users[callback_data.target_id]

    room: Room = player.current_room

    await callback.message.edit_text(TEXTS['voting_done'][player.language])
    if target in room.day_voting:
        room.day_voting[target] += 1
    else:
        room.day_voting[target] = 1
    player.made_move = True
    day_is_over = True
    for player in room.users.values():
        if not player.made_move:
            day_is_over = False
            break
    if day_is_over:
        await day_voting_processor(room)


async def day_voting_processor(room: Room):
    max_votes = max(room.day_voting.values())

    victims = [user for user, votes in room.day_voting.items() if votes == max_votes]
    if len(victims) == 1:
        victim = victims[0]
        victim.is_alive = False
        for player in room.users.values():
            await bot.send_message(player.id, TEXTS['day_voting_kicked'][player.language].format(victim.username))
    elif len(victims) > 1:
        for player in room.users.values():
            if player.is_alive:
                player.made_move = False
                keyboard = await generate_day_voting_kb(room, player, victims)
                await bot.send_message(player.id, TEXTS['re_vote'][player.language], reply_markup=keyboard)
        return
    await game_ended_checker(room)
    if room.is_active:
        await start_night(room)


async def game_ended_checker(room: Room):
    mafia_amount = 0
    civilians_amount = 0
    for player in room.users.values():
        if player.role == Mafia and player.is_alive:
            mafia_amount += 1
        elif player.role in (Doctor, Civilian) and player.is_alive:
            civilians_amount += 1
    if mafia_amount >= civilians_amount:
        return await game_end_proceed(room, MAFIA_WON)
    if mafia_amount == 0:
        return await game_end_proceed(room, CIVILIANS_WON)


async def game_end_proceed(room: Room, code: int):
    for player in room.users.values():
        await bot.send_message(player.id, TEXTS[code][player.language])
    room.is_active = False
    for player in room.users.values():
        player.reset()
    keyboard = await generate_room_actions_cb(room, room.owner.language, room.owner)
    await bot.send_message(room.owner.id, TEXTS['room_actions'][room.owner.language].format(', '.join("@" + x.username for x in room.users.values())), reply_markup=keyboard)


@dp.callback_query(RolesAddingCb.filter())
async def roles_adding_handler(callback: CallbackQuery, callback_data: CallbackData):
    """Выбор роли для изменения ее количества в комнате"""
    await callback.answer()
    role_id = callback_data.role_id
    room_id = callback_data.room_id
    user = users[callback.message.chat.id]
    room = rooms[room_id]
    role = ROLES[role_id]
    amount = room.available_roles[role]
    name = role.name[user.language]

    keyboard = await generate_role_adding_kb(role_id, room_id, user.language)
    if user.language == RU:
        name = ru_name_fixer(name, amount)
        await callback.message.edit_text(TEXTS['change_role_amount'][user.language].format(amount, name),
                                         reply_markup=keyboard)
    elif user.language == EN:
        name, to_be = en_name_fixer(name, amount)
        await callback.message.edit_text(TEXTS['change_role_amount'][user.language].format(amount, name, to_be),
                                         reply_markup=keyboard)


@dp.callback_query(RoleAddCb.filter())
async def role_add_handler(callback: CallbackQuery, callback_data: CallbackData):
    """Изменение количества выбранной роли в комнате"""
    await callback.answer()
    role_id = callback_data.role_id
    room_id = callback_data.room_id
    value = callback_data.value
    user = users[callback.message.chat.id]
    room = rooms[room_id]
    role = ROLES[role_id]

    room.available_roles[role] += value
    if room.available_roles[role] < 0:
        room.available_roles[role] = 0

    amount = room.available_roles[role]
    name = role.name[user.language]

    keyboard = await generate_role_adding_kb(role_id, room_id, user.language)
    if user.language == RU:
        name = ru_name_fixer(name, amount)
        await callback.message.edit_text(TEXTS['change_role_amount'][user.language].format(amount, name),
                                         reply_markup=keyboard)
    elif user.language == EN:
        name, to_be = en_name_fixer(name, amount)
        await callback.message.edit_text(TEXTS['change_role_amount'][user.language].format(amount, name, to_be),
                                         reply_markup=keyboard)


@dp.callback_query(UserSettingsCb.filter())
async def user_settings_handler(callback: CallbackQuery, callback_data: CallbackData):
    """Выбор настройки аккаунта пользователя для изменения"""
    await callback.answer()
    user = users[callback.message.chat.id]
    await callback.message.edit_text(TEXTS['choose_user_setting'][user.language],
                                     reply_markup=KEYBOARDS['choose_user_setting'][user.language])


@dp.callback_query(UserSettingCb.filter())
async def user_setting_handler(callback: CallbackQuery, callback_data: CallbackData):
    """Изменение выбранной настройки аккаунта"""
    await callback.answer()
    user = users[callback.message.chat.id]
    setting = callback_data.setting
    if setting == 'language':
        await callback.message.edit_text(TEXTS['choose_language'], reply_markup=KEYBOARDS['choose_language'])
    else:
        raise NotImplementedError


@dp.callback_query(RoomSettingsCb.filter())
async def room_settings_handler(callback: CallbackQuery, callback_data: CallbackData):
    """Выбор настройки для изменения в комнате"""
    await callback.answer()
    room_id = callback_data.room_id
    setting = callback_data.setting
    user = users[callback.message.chat.id]
    keyboard = await generate_room_setting_kb(room_id, setting, user.language)
    if setting == 'do_reveal':
        await callback.message.edit_text(TEXTS['setting_change'][user.language], reply_markup=keyboard)
    elif setting == 'cancel':
        keyboard = await generate_room_actions_cb(user.current_room, user.language, user)
        await callback.message.edit_text(TEXTS['room_actions'][user.language].format(', '.join("@" + x.username for x in user.current_room.users.values())), reply_markup=keyboard)


@dp.callback_query(RoomSettingCb.filter())
async def room_settings_handler(callback: CallbackQuery, callback_data: CallbackData):
    """Выбор состояния выбранной настройки комнаты"""
    await callback.answer()
    room_id = callback_data.room_id
    setting = callback_data.setting
    value = callback_data.value
    user = users[callback.message.chat.id]
    room = rooms[room_id]

    room.set_setting(setting, value)
    await callback.message.edit_text(TEXTS['setting_changed'][user.language])

    keyboard = await generate_room_actions_cb(room, user.language, user)
    await callback.message.answer(TEXTS['room_actions'][user.language].format(', '.join("@" + x.username for x in user.current_room.users.values())), reply_markup=keyboard)


@dp.message(lambda message: message.chat.id not in users)
async def choose_language(message: Message):
    await message.answer(TEXTS['choose_language'], reply_markup=KEYBOARDS['choose_language'])


@dp.message(lambda message: '/start' in message.text)
async def startup(message: Message):
    user = users.get_user(message.chat.id)
    command = message.text.split()
    if len(command) == 2:  # Есть параметр у команды
        if user.current_room is not None:
            keyboard = await generate_room_actions_cb(user.current_room, user.language, user)
            return await message.answer(TEXTS['already_joined'][user.language], reply_markup=keyboard)
        token = command[-1]
        await join_room(message, token, user)
        if user.current_room is not None:
            keyboard = await generate_room_actions_cb(user.current_room, user.language, user)
            await message.answer(TEXTS['room_actions'][user.language].format(
                ', '.join("@" + x.username for x in user.current_room.users.values())), reply_markup=keyboard)
            return
    await message.answer(TEXTS['startup'][user.language], reply_markup=KEYBOARDS['startup'][user.language])


@dp.message(lambda message: users[message.chat.id].state == JOINING_ROOM_STATE)
async def room_joining(message: Message):
    user = users[message.chat.id]
    if message.text.lower() in ('отмена', 'cancel'):  # FIX ввод именно таких команд не требуется
        user.set_state(DEFAULT_STATE)
        return await message.answer(TEXTS['startup'][user.language], reply_markup=KEYBOARDS['startup'][user.language])
    await join_room(message, message.text, user)


async def join_room(message, token, user):
    """Вход в комнату с проверкой валидности действия и установкой состояния"""
    user.set_state(DEFAULT_STATE)
    for room in rooms.values():
        if room.token == token:
            if user.current_room is not None:
                keyboard = await generate_room_actions_cb(user.current_room, user.language, user)
                return await message.answer(TEXTS['already_joined'][user.language], reply_markup=keyboard)
            username = message.chat.username

            await message.answer(TEXTS['room_join'][user.language])
            for player in room.users.values():
                await bot.send_message(player.id, TEXTS['room_joined'][player.language].format(username))

            room.add_user(user)
            owner = room.owner
            language = owner.language

            keyboard = await generate_room_actions_cb(owner.current_room, user.language, owner)
            text = TEXTS['room_actions'][language].format(', '.join("@" + x.username for x in room.users.values()))
            await bot.send_message(owner.id, text, reply_markup=keyboard)
            return

    await message.answer(TEXTS['wrong_token'][user.language], reply_markup=KEYBOARDS['startup'][user.language])


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
