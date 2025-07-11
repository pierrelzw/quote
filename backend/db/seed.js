const sqlite3 = require('sqlite3').verbose();
const db = new sqlite3.Database('./db/quote.db');

const quotes = [
  { content: "天生我材必有用。", author: "李白" },
  { content: "路漫漫其修远兮，吾将上下而求索。", author: "屈原" },
  { content: "不积跬步，无以至千里。", author: "荀子" },
  { content: "千里之行，始于足下。", author: "老子" },
  { content: "会当凌绝顶，一览众山小。", author: "杜甫" },
  { content: "海内存知己，天涯若比邻。", author: "王勃" },
  { content: "长风破浪会有时，直挂云帆济沧海。", author: "李白" },
  { content: "人生自古谁无死，留取丹心照汗青。", author: "文天祥" },
  { content: "少壮不努力，老大徒伤悲。", author: "《汉乐府》" },
  { content: "业精于勤荒于嬉，行成于思毁于随。", author: "韩愈" },
  { content: "黑发不知勤学早，白首方悔读书迟。", author: "颜真卿" },
  { content: "三人行，必有我师焉。", author: "孔子" },
  { content: "己所不欲，勿施于人。", author: "孔子" },
  { content: "知之者不如好之者，好之者不如乐之者。", author: "孔子" },
  { content: "敏而好学，不耻下问。", author: "孔子" },
  { content: "学而不思则罔，思而不学则殆。", author: "孔子" },
  { content: "读万卷书，行万里路。", author: "刘彝" },
  { content: "书山有路勤为径，学海无涯苦作舟。", author: "韩愈" },
  { content: "千教万教教人求真，千学万学学做真人。", author: "陶行知" },
  { content: "立身以立学为先，立学以读书为本。", author: "欧阳修" }
];

quotes.forEach(q => {
  db.run(
    'INSERT INTO quotes (content, author) VALUES (?, ?)',
    [q.content, q.author]
  );
});

db.close();
console.log('已插入20条名言');
