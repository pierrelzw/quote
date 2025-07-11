const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const jwt = require('jsonwebtoken');

const router = express.Router();
const db = new sqlite3.Database('./db/quote.db');
const JWT_SECRET = 'your_jwt_secret'; // 与 auth.js 保持一致

// 获取所有名言（分页，按时间倒序）
router.get('/', (req, res) => {
  // 获取分页参数
  const page = parseInt(req.query.page) || 1;
  const pageSize = parseInt(req.query.pageSize) || 10;
  const offset = (page - 1) * pageSize;

  // 查询总数
  db.get(
    `SELECT COUNT(*) as count FROM quotes`,
    [],
    (err, countRow) => {
      if (err) return res.status(500).json({ message: '获取总数失败' });

      // 查询分页数据
      db.all(
        `SELECT quotes.id, quotes.content, quotes.author, quotes.created_at, users.username AS added_by
         FROM quotes
         LEFT JOIN users ON quotes.user_id = users.id
         ORDER BY quotes.created_at DESC
         LIMIT ? OFFSET ?`,
        [pageSize, offset],
        (err, rows) => {
          if (err) return res.status(500).json({ message: '获取名言失败' });
          res.json({
            total: countRow.count,
            page,
            pageSize,
            quotes: rows
          });
        }
      );
    }
  );
});

// 添加名言（需要登录）
router.post('/', (req, res) => {
  const token = req.headers.authorization?.split(' ')[1];
  if (!token) return res.status(401).json({ message: '未登录' });

  let user;
  try {
    user = jwt.verify(token, JWT_SECRET);
  } catch {
    return res.status(401).json({ message: '无效的 token' });
  }

  const { content, author } = req.body;
  if (!content || !author) {
    return res.status(400).json({ message: '内容和作者不能为空' });
  }

  db.run(
    'INSERT INTO quotes (content, author, user_id) VALUES (?, ?, ?)',
    [content, author, user.id],
    function (err) {
      if (err) return res.status(500).json({ message: '添加失败' });
      res.json({ id: this.lastID, content, author, user_id: user.id });
    }
  );
});

module.exports = router; 