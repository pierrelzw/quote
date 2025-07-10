const sqlite3 = require('sqlite3').verbose();
const db = new sqlite3.Database('./db/quote.db');

// 创建用户表
db.run(`
  CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
  )
`);

// 创建名言表
db.run(`
  CREATE TABLE IF NOT EXISTS quotes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT NOT NULL,
    author TEXT NOT NULL,
    user_id INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,å
    FOREIGN KEY(user_id) REFERENCES users(id)
  )
`);

db.close();
console.log('数据库初始化完成');
