# discord_ai_bot
discordで動くAIbotを導入する
- awsのlightsailで動かします。(Pythonの実行をローカルで試すこともできます。その場合はいい感じに読み替えてください)
- User <---> bot on Discord <---> python on AWS Lightsail <---> OpenAI API

## OpenAIのセッティング
### OpenAIのAPI keyを取得
- https://platform.openai.com/api-keys から「Create new secret key」を実行します。
- Nameは分かりやすい名前にしておきます。（例えば日付や用途を含めておく）
- `Save your key`の画面で表示されるkeyは手元に控えておく。再表示できないので注意。
- 世に出回ると他人があなたのお金で実行できてしまうので取扱いに注意。

### OpenAIのクレジット残高を追加
- https://platform.openai.com/account/billing/overview の画面で使いたい金額をチャージしておく。

## Discordのセッティング
### 新しいアプリケーションを作成。
- https://discord.com/developers/applications?new_application=true から作成します。
- NAMEは分かりやすい名前にしておきます。（例えばgpt_botなど）
- APP ICONは好きに変えておきます。
  - https://www.irasutoya.com/2023/04/ai.html
- 左メニューの「Bot」面に移動し、
  - PUBLIC BOTをオフ
  - MESSAGE CONTENT INTENTをオン
  - 「Reset Token」を実行
  - 表示されるTOKENは手元に控えておく。再表示できないので注意。
- 世に出回ると他人があなたのbotを実行できてしまうので取扱いに注意。

- oauth2 > url generatorの面に移動しbotのみにチェックを付けて、次のパーミッションをオンにする
  - Read Messages/View Channels
  - Send Messages
  - Create Public Threads
  - Send Messages in Threads
  - Manage Messages
- 下部にurlが生成されるのでコピーして開く
- 自分が管理者のサーバーに導入できる

サーバーにオフラインのbotがいることを確認する。

## AWS Lightsailのセッティング
### 新しいインスタンスを作成
https://lightsail.aws.amazon.com/ls/webapp/create/instance?region=ap-northeast-1
- select a platform = linux/unix
- os only = centos 9
- 3.5$のやつ
- Identify your instanceは分かりやすい名前にする
  - gpt_botとか

待つとインスタンス作られる。
- https://lightsail.aws.amazon.com/ls/webapp/home/instances
- インスタンスを選んでNetworkingタブからIPv4とIPv6の開いているFirewallを削除する。
- IPv4 Firewallに「Add rule」して以下設定でCreateする
  - Application=SSH
  - Restrict to IP address = yes
- Lightsail browser SSH/RDP Onlyの状態になる

ブラウザのConnectタブから「Connect using SSH」でコンソールを開いてアプデかける(放置でrebootされるのでコネクションが切れる)
```
sudo dnf update -y && sudo reboot
```

rebootされたら再度繋ぎ、python周りをインストールする。
```
sudo dnf install python3 -y && sudo dnf install python3-pip -y && pip3 install --upgrade openai && pip3 install discord.py
```

環境変数にAPIKEYとTOKENを設定する。
```
sudo vi /etc/environment
```
以下を記述して保存し、rebootかける。
```
OPENAI_API_KEY='ここに控えておいたOpenAIのAPIKEY'
DISCORD_BOT_TOKEN='ここに控えておいたDiscordのTOKEN'
```
```
sudo reboot
```
環境変数に反映されたか確認するならechoする。
```
echo $OPENAI_API_KEY && echo $DISCORD_BOT_TOKEN
```

### コードをダウンロードする
```
curl https://raw.githubusercontent.com/kagasan/discord_ai_bot/main/discord_bot.py -o discord_bot.py
```

### 実行したくなったら
```
nohup python3 discord_bot.py > /dev/null 2>&1 &
```
Discord画面でbotがオンラインになればOKです。

### 実行中のbotを止めたくなったら
```
kill -9 $(pgrep -f discord_bot.py)
```
Discord画面でbotがオフラインになればOKです。
