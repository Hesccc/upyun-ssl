-- schema.sql

-- 系统用户登录表
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);

-- 云账户配置表
CREATE TABLE IF NOT EXISTS cloud_config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cloud_user NOT NULL,
    cloud_pass NOT NULL
);