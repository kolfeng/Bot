const { Telegraf } = require('telegraf');
const axios = require('axios');
const express = require('express');

const BOT_TOKEN = process.env.BOT_TOKEN;
const HF_TOKEN = process.env.HF_TOKEN;
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
      'https://api-inference.huggingface.co/models/gpt2',
      {
        inputs: userMessage,
        parameters: { 
          max_length: 100,
          temperature: 0.7,
          return_full_text: false
        }
      },
      {
        headers: {
          'Authorization': `Bearer ${HF_TOKEN}`
        },
        timeout: 10000
      }
    );
    
    let aiResponse = response.data[0]?.generated_text || "Думаю...";
    if (aiResponse.length > 1000) aiResponse = aiResponse.substring(0, 1000);
    
    await ctx.reply(aiResponse);
    
  } catch (error) {
    const answers = [
      "Привет!",
      "Интересно",
      "Спроси еще"
    ];
    const randomAnswer = answers[Math.floor(Math.random() * answers.length)];
    await ctx.reply(randomAnswer);
  }
});

bot.launch().then(() => {
  console.log('Bot started');
});

process.once('SIGINT', () => bot.stop('SIGINT'));
process.once('SIGTERM', () => bot.stop('SIGTERM'));
