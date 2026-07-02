import discord
import asyncio
import feedparser
import os
import aiohttp

TOKEN = "TOKEN"
CHANNEL_ID = ID
RSS_URLS = [
    "https://www.phoronix.com/rss.php",
    "https://archlinux.org/feeds/news/",
    "https://www.gentoo.org/feeds/news.xml",
    "https://distrowatch.com/news/dw.xml",
    "https://micronews.debian.org/feeds/feed.rss",
    "https://blog.linuxmint.com/?feed=rss2",
    "https://news.opensuse.org/category/announcements/feed/",
    "https://fedoramagazine.org/feed/",
    "https://forum.endeavouros.com/c/important-notifications/125.rss"
]
CHECK_INTERVAL = 300
SENT_FILE = "sent_links.txt"

class NewsBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(intents=intents)
        self.seen = self.load_seen()

    def load_seen(self):
        if os.path.exists(SENT_FILE):
            with open(SENT_FILE, "r") as f:
                return set(line.strip() for line in f)
        return set()

    def save_seen(self, link):
        with open(SENT_FILE, "a") as f:
            f.write(link + "\n")

    async def fetch_feed(self, url):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
            "Accept": "application/rss+xml, application/xml, text/xml; q=0.9, */*; q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Cache-Control": "no-cache",
        }
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, timeout=10, headers=headers) as response:
                    if response.status != 200:
                        print(f"Ошибка {url}: статус {response.status}")
                        return None
                    text = await response.text()
                    if not text.strip():
                        print(f"Пустой ответ от {url}")
                        return None
                    return feedparser.parse(text)
            except Exception as e:
                print(f"Ошибка загрузки {url}: {e}")
                return None

    async def on_ready(self):
        print(f"Бот {self.user} запущен")
        print(f"Бот готов отвечать на сообщения!")
        self.loop.create_task(self.check_news())

    async def check_news(self):
        await self.wait_until_ready()
        while not self.is_closed():
            try:
                for url in RSS_URLS:
                    feed = await self.fetch_feed(url)
                    if feed is None or not feed.entries:
                        continue
                    for entry in feed.entries[:5]:
                        if entry.link not in self.seen:
                            self.seen.add(entry.link)
                            self.save_seen(entry.link)
                            channel = self.get_channel(CHANNEL_ID)
                            if channel:
                                await channel.send(f"**{entry.title}**\n{entry.link}")
                await asyncio.sleep(CHECK_INTERVAL)
            except Exception as e:
                print(f"Ошибка: {e}")
                await asyncio.sleep(60)

    async def on_message(self, message):
        if message.author == self.user:
            return

        msg_clean = message.content.strip().lower()
                
        if "редхат" in msg_clean:
             await message.channel.send("https://cdn.discordapp.com/attachments/1520382246161485855/1521852916670009416/GCC_SystemD_nJZSQDGXOLg.webm?ex=6a465779&is=6a4505f9&hm=7faa83cfcef23e5b0d9564923ce127275507b9a13333dc44aa2c540ceedff870&")
             return

        if "да" in msg_clean:
             await message.channel.send("ПИЗДА")
             return

        print(f"Сообщение от {message.author}: {message.content}")

client = NewsBot()
client.run(TOKEN)
