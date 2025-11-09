const { Telegraf } = require('telegraf');
const axios = require('axios');
const express = require('express');

const BOT_TOKEN = process.env.BOT_TOKEN;
const HF_TOKEN = process.env.HF_TOKEN;
const bot = new Telegraf(BOT_TOKEN);
const app = express();

// Простой веб-сервер для Render
app.get('/', (req, res) => {
  res.send('🤖 AI Bot is running!');
});

// Запускаем веб-сервер на порту 3000
app.listen(3000, () => {
  console.log('🌐 Web server started on port 3000');
});

// Команда /start
bot.start((ctx) => {
  ctx.reply('🧠 Привет! Я AI бот с нейросетью! Задай вопрос!');
});

bot.on('text', async (ctx) => {
  try {
    await ctx.sendChatAction('typing');
    const userMessage = ctx.message.text;
    
    // Пока используем простые ответы
    const answers = [
      "🧠 Я бот с нейросетью! Пока настраиваюсь...",
      "💭 Скоро я стану умнее!",
      "🤖 AI модуль загружается...",
      "Пока отвечаю просто, но скоро научусь!"
    ];
    
    const randomAnswer = answers[Math.floor(Math.random() * answers.length)];
    await ctx.reply(randomAnswer);
    
  } catch (error) {
    console.error('Ошибка:', error);
    await ctx.reply('Упс! Что-то пошло не так.');
  }
});

// Запуск бота
bot.launch().then(() => {
  console.log('🧠 AI бот запущен!');
});

process.once('SIGINT', () => bot.stop('SIGINT'));
process.once('SIGTERM', () => bot.stop('SIGTERM'));
