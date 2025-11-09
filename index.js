const { Telegraf } = require('telegraf');

const BOT_TOKEN = process.env.BOT_TOKEN;
const bot = new Telegraf(BOT_TOKEN);

bot.start((ctx) => ctx.reply('Привет! Бот работает на Render! 🚀'));
bot.on('text', (ctx) => ctx.reply('Получил: ' + ctx.message.text));

bot.launch();
console.log('🤖 Бот запущен!');
