const { Telegraf } = require('telegraf');
const axios = require('axios');
const express = require('express');

const BOT_TOKEN = process.env.BOT_TOKEN;
const bot = new Telegraf(BOT_TOKEN);
const app = express();

app.get('/', (req, res) => {
  res.send('Bot is running');
});
app.listen(3000, () => {
  console.log('Server started');
});

bot.start((ctx) => {
  ctx.reply('Привет! Я бот с нейросетью');
});

bot.on('text', async (ctx) => {
  try {
    await ctx.sendChatAction('typing');
    const userMessage = ctx.message.text;
    
    const response = await axios.post(
      'https://free.churchless.tech/v1/chat/completions',
      {
        model: "gpt-3.5-turbo",
        messages: [
          {role: "user", content: userMessage}
        ],
        max_tokens: 500
      },
      {
        headers: {
          'Content-Type': 'application/json'
        },
        timeout: 30000
      }
    );
    
    const aiResponse = response.data.choices[0].message.content;
    await ctx.reply(aiResponse);
    
  } catch (error) {
    await ctx.reply('Нейросеть временно недоступна');
  }
});

bot.launch().then(() => {
  console.log('Bot started');
});

process.once('SIGINT', () => bot.stop('SIGINT'));
process.once('SIGTERM', () => bot.stop('SIGTERM'));
