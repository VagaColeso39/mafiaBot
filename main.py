from aiogram import Bot, Dispatcher
from aiogram.types import Message
import dotenv
import os
import asyncio
import psycopg2
import secrets
from adds import *

dotenv.load_dotenv('.env')
TOKEN = os.getenv('TOKEN', '')
dp = Dispatcher()
bot = Bot(TOKEN)
users = Users()
rooms = {}
roles = {0: Civilian, 1: Mafia, 2: Doctor}

# conn = psycopg2.connect(
#     host=os.getenv('DB_HOST'),
#     database=os.getenv('DB_NAME'),
#     user=os.getenv('DB_USER'),
#     password=os.getenv('DB_PASSWORD'),
#     port=os.getenv('DB_PORT')
# )


@dp.callback_query(LangCb.filter())
async def choose_language_handler(callback: CallbackQuery, callback_data: CallbackData):
    await callback.answer()
    language = callback_data.language
    user_id = callback.message.chat.id
    if user_id in users:
        users[user_id].set_language(language)
    else:
        users.create_user(user_id, language, DEFAULT_STATE)
    await callback.message.edit_text(TEXTS['language_changed'][language])
    await callback.message.answer(TEXTS['startup'][language], reply_markup=KEYBOARDS['startup'][language])


@dp.callback_query(JoinRoomCb.filter())
async def join_room_handler(callback: CallbackQuery, callback_data: CallbackData):
    await callback.answer()
    user = users[callback.message.chat.id]
    if user.current_room is not None:
        return await callback.message.answer(TEXTS['already_joined'][user.language])
    user.set_state(JOINING_ROOM_STATE)
    await callback.message.edit_text(TEXTS['enter_token'][user.language])



@dp.callback_query(RoomCreationCb.filter())
async def room_creation_handler(callback: CallbackQuery, callback_data: CallbackData):
    await callback.answer()
    user = users[callback.message.chat.id]
    if user.current_room is not None:
        return await callback.message.answer(TEXTS['already_joined'][user.language])
    room_id = len(rooms)
    token = secrets.token_urlsafe(16)
    room = Room(owner=user, room_id=room_id, token=token)
    rooms[room_id] = room
    keyboard = await generate_room_actions_cb(room_id, user.language)
    await callback.message.answer(TEXTS['room_actions'][user.language], reply_markup=keyboard)


@dp.callback_query(RoomActionsCb.filter())
async def room_actions_handler(callback: CallbackQuery, callback_data: CallbackData):
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

        keyboard = await generate_room_actions_cb(room.id, user.language)
        await callback.message.answer(TEXTS['room_actions'][user.language], reply_markup=keyboard)
        
    elif action == 'settings':
        if room.owner == user:
            keyboard = await generate_room_settings_kb(room.id, user.language)
            await callback.message.edit_text(TEXTS['room_settings'][user.language], reply_markup=keyboard)
        else:
            await callback.message.edit_text(TEXTS['forbidden_action'][user.language])
            
            keyboard = await generate_room_actions_cb(room.id, user.language)
            await callback.message.answer(TEXTS['room_actions'][user.language], reply_markup=keyboard)
            
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


@dp.callback_query(RolesAddingCb.filter())
async def roles_adding_handler(callback: CallbackQuery, callback_data: CallbackData):
    await callback.answer()
    role_id = callback_data.role_id
    room_id = callback_data.room_id
    user = users[callback.message.chat.id]
    room = rooms[room_id]
    role = roles[role_id]
    amount = room.available_roles[role]
    name = role.name[user.language]

    keyboard = await generate_role_adding_kb(role_id, room_id, user.language)
    await callback.message.edit_text(TEXTS['change_role_amount'][user.language].format(amount, name), reply_markup=keyboard)

@dp.callback_query(RoleAddCb.filter())
async def role_add_handler(callback: CallbackQuery, callback_data: CallbackData):
    await callback.answer()
    role_id = callback_data.role_id
    room_id = callback_data.room_id
    value = callback_data.value
    user = users[callback.message.chat.id]
    room = rooms[room_id]
    role = roles[role_id]


    room.available_roles[role] += value
    if room.available_roles[role] < 0:
        room.available_roles[role] = 0

    amount = room.available_roles[role]
    name = role.name[user.language]

    keyboard = await generate_role_adding_kb(role_id, room_id, user.language)
    await callback.message.edit_text(TEXTS['change_role_amount'][user.language].format(amount, name), reply_markup=keyboard)



@dp.callback_query(UserSettingsCb.filter())
async def user_settings_handler(callback: CallbackQuery, callback_data: CallbackData):
    await callback.answer()
    user = users[callback.message.chat.id]
    await callback.message.edit_text(TEXTS['choose_user_setting'][user.language], reply_markup=KEYBOARDS['choose_user_setting'][user.language])


@dp.callback_query(UserSettingCb.filter())
async def user_setting_handler(callback: CallbackQuery, callback_data: CallbackData):
    await callback.answer()
    user = users[callback.message.chat.id]
    setting = callback_data.setting
    if setting == 'language':
        await callback.message.edit_text(TEXTS['choose_language'], reply_markup=KEYBOARDS['choose_language'])
    else:
        raise NotImplementedError


@dp.callback_query(RoomSettingsCb.filter())
async def room_settings_handler(callback: CallbackQuery, callback_data: CallbackData):
    await callback.answer()
    room_id = callback_data.room_id
    setting = callback_data.setting
    user = users[callback.message.chat.id]
    keyboard = await generate_room_setting_kb(room_id, setting, user.language)
    if setting == 'doReveal':
        await callback.message.edit_text(TEXTS['setting_change'][user.language], reply_markup=keyboard)
    elif setting == 'cancel':
        keyboard = await generate_room_actions_cb(room_id, user.language)
        await callback.message.edit_text(TEXTS['room_actions'][user.language], reply_markup=keyboard)
    
    
@dp.callback_query(RoomSettingCb.filter())
async def room_settings_handler(callback: CallbackQuery, callback_data: CallbackData):
    await callback.answer()
    room_id = callback_data.room_id
    setting = callback_data.setting
    value = callback_data.value
    user = users[callback.message.chat.id]
    room = rooms[room_id]
    
    room.set_setting(setting, value)
    await callback.message.edit_text(TEXTS['setting_changed'][user.language])   
    
    keyboard = await generate_room_actions_cb(room_id, user.language)
    await callback.message.answer(TEXTS['room_actions'][user.language], reply_markup=keyboard)


@dp.message(lambda message: message.chat.id not in users)
async def choose_language(message: Message):
    await message.answer(TEXTS['choose_language'], reply_markup=KEYBOARDS['choose_language'])


@dp.message(lambda message: '/start' in message.text)
async def startup(message: Message):
    user = users.get_user(message.chat.id)
    command = message.text.split()
    if len(command) == 2:  # Есть параметр у команды
        if user.current_room is not None:
            return await message.answer(TEXTS['already_joined'][user.language])
        token = command[-1]
        await join_room(message, token, user)

    await message.answer(TEXTS['startup'][user.language], reply_markup=KEYBOARDS['startup'][user.language])


@dp.message(lambda message: users[message.chat.id].state == JOINING_ROOM_STATE)
async def room_joining(message: Message):
    user = users[message.chat.id]
    if message.text.lower() in ('отмена', 'cancel'):
        user.set_state(DEFAULT_STATE)
        return await message.answer(TEXTS['startup'][user.language], reply_markup=KEYBOARDS['startup'][user.language])
    await join_room(message, message.text, user)


async def join_room(message, token, user):
    user.set_state(DEFAULT_STATE)
    for room in rooms.values():
        if room.token == token:

            room.add_user(user)
            owner_id = room.owner.id
            username = message.chat.username

            await message.answer(TEXTS['room_join'][user.language])
            await bot.send_message(owner_id, TEXTS['room_join_owner'][user.language].format(username))
            return

    await message.answer(TEXTS['wrong_token'][user.language], reply_markup=KEYBOARDS['startup'][user.language])


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
