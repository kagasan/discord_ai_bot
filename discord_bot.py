"""
# run bot
nohup python3 discord_bot.py > /dev/null 2>&1 &
# stop bot
kill -9 $(pgrep -f discord_bot.py)
"""

import discord
import os
import re
from discord.ext import commands
from openai import OpenAI
client = OpenAI()

# Botの設定
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

# コマンドプレフィックスを'!'に設定
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.event
async def on_message(message):
    # Bot自身のメッセージは無視
    if message.author == bot.user:
        return
    # Botにメッセージが届いていない場合は無視
    if bot.user not in message.mentions:
        return

    # すでにスレッド内の場合
    if isinstance(message.channel, discord.Thread):
        # 親チャンネルを取得
        thread = message.channel
        parent_channel = bot.get_channel(thread.parent_id)
        
        # スレッドの起点となるメッセージを取得
        origin_message = await parent_channel.fetch_message(thread.id)

        # スレッド内のメッセージ履歴を取得
        question_history = [re.sub(r'<@!?(\d+)>', '', origin_message.content).strip()]
        async for msg in thread.history(limit=100, oldest_first=True):
            question_history.append(re.sub(r'<@!?(\d+)>', '', msg.content).strip())
        print(question_history)

        # 質問を受け付けた旨の投稿を行う
        initial_message = await message.channel.send('スレッドで質問を受け付けました。少々お待ちください...')

        stream = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "必要に応じてマークダウンを使用して回答してください。"},
                {"role": "user", "content": '\n'.join(question_history)},
            ],
            stream=True,
        )
        
        reply = ''
        cnt = 0
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:                
                reply += chunk.choices[0].delta.content
                cnt += 1
                if len(chunk.choices[0].delta.content) > 0 and cnt % 10 == 9:
                    await initial_message.edit(content=reply)
        await initial_message.edit(content=reply)
        await initial_message.add_reaction('\N{THUMBS UP SIGN}')
    else:
        # スレッドを作成
        cleaned_content = re.sub(r'<@!?(\d+)>', '', message.content).strip()[:20]
        thread = await message.create_thread(name=f'{message.author}:{cleaned_content}')
        
        # OpenAI APIに問い合わせる用の質問を取得
        question = re.sub(r'<@!?(\d+)>', '', message.content).strip()
        print(question)
        
        # スレッドに初期メッセージを投稿
        initial_message = await thread.send('チャンネルで質問を受け付けました。少々お待ちください...')

        stream = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "必要に応じてマークダウンを使用して回答してください。"},
                {"role": "user", "content": question},
            ],
            stream=True,
        )
        
        reply = ''
        cnt = 0
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:                
                reply += chunk.choices[0].delta.content
                cnt += 1
                if len(chunk.choices[0].delta.content) > 0 and cnt % 10 == 9:
                    await initial_message.edit(content=reply)
        await initial_message.edit(content=reply)
        await initial_message.add_reaction('\N{THUMBS UP SIGN}')

# Botを起動
bot.run(os.environ['DISCORD_BOT_TOKEN'])
