const { Telegraf } = require('telegraf');
const axios = require('axios');

const BOT_TOKEN = process.env.BOT_TOKEN;
const HF_TOKEN = process.env.HF_TOKEN;
const bot = new Telegraf(BOT_TOKEN);

bot.start((ctx) => {
  ctx.reply('🧠 Привет! Я AI бот с нейросетью! Задай вопрос!');
});

bot.on('text', async (ctx) => {
  try {
    await ctx.sendChatAction('typing');
    const userMessage = ctx.message.text;
    
    // НОВЫЙ URL для Hugging Face API
    const response = await axios.post(
      'https://router.huggingface.co/hf-inference/models/microsoft/DialoGPT-medium',
      {
        inputs: userMessage,
        parameters: { 
          max_length: 1000, 
          temperature: 0.7,
          do_sample: true
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
    
    // Запасные ответы
    const fallbackAnswers = [
      "🧠 Нейросеть загружается... Попробуй через минуту!",
      "💭 AI думает слишком долго, задай вопрос короче!",
      "🤖 Пока использую простые ответы, нейросеть недоступна",
      "Извини, нейросеть временно не работает 😔"
    ];
    
    const randomAnswer = fallbackAnswers[Math.floor(Math.random() * fallbackAnswers.length)];
    await ctx.reply(randomAnswer);
  }
});

bot.launch().then(() => {
  console.log('🧠 AI бот запущен!');
});

process.once('SIGINT', () => bot.stop('SIGINT'));
process.once('SIGTERM', () => bot.stop('SIGTERM'));
