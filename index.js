const { Telegraf } = require('telegraf');
const axios = require('axios');
const express = require('express');

const BOT_TOKEN = process.env.BOT_TOKEN;
const HF_TOKEN = process.env.HF_TOKEN;
const bot = new Telegraf(BOT_TOKEN);
const app = express();

// Веб-сервер для Render
app.get('/', (req, res) => {
  res.send('🤖 AI Bot is running!');
});
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
    
    // Нейросеть Hugging Face
    const response = await axios.post(
      'https://router.huggingface.co/hf-inference/models/microsoft/DialoGPT-medium',
      {
        inputs: userMessage,
        parameters: { 
          max_length: 1000, 
          temperature: 0.7
        }
      },
      {
        headers: {
          'Authorization': `Bearer ${HF_TOKEN}`,
          'Content-Type': 'application/json'
        },
        timeout: 30000
      }
    );
    
    let aiResponse = response.data[0]?.generated_text || "Извини, не могу придумать ответ";
    if (aiResponse.length > 4000) aiResponse = aiResponse.substring(0, 4000) + "...";
    
    await ctx.reply(aiResponse);
    
  } catch (error) {
    console.error('Ошибка нейросети:', error);
    await ctx.reply('🧠 Нейросеть загружается... Попробуй через минуту!');
  }
});

// Запуск бота
bot.launch().then(() => {
  console.log('🧠 AI бот запущен!');
});

process.once('SIGINT', () => bot.stop('SIGINT'));
process.once('SIGTERM', () => bot.stop('SIGTERM'));
