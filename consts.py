RU = 0
EN = 1
DAY = 0
NIGHT = 1
DEFAULT_STATE = 0
JOINING_ROOM_STATE = 1
GOOD = 0
BAD = 1
NEUTRAL = 2
MAFIA_WON = 0
CIVILIANS_WON = 1

GET_ALL_USERS = "SELECT id, username, language FROM users"
CREATE_USER = "INSERT INTO users (id, username, language) VALUES (%s, %s, %s)"
CREATE_USERS_TABLE = """
CREATE TABLE IF NOT EXISTS users (
    id BIGINT PRIMARY KEY,
    username VARCHAR(100) UNIQUE,
    language INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);"""

FORMS = {"Доктор": ('Доктор', "Доктора", "Докторов"), "Мафия": ("Мафия", "Мафии", "Мафий"), "Мирный": ("Мирный", "Мирных", "Мирных")}