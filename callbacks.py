from aiogram.filters.callback_data import CallbackData


class NightActionCb(CallbackData, prefix="NightAction"):
    target_id: int
    player_id: int


class DayVotingCb(CallbackData, prefix="DayVoting"):
    target_id: int
    player_id: int


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
