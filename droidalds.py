import discord
import asyncio
import feedparser
import os

TOKEN = "TOKEN"
CHANNEL_ID = ID
RSS_URLS = [
    "https://lwn.net/headlines/rss",
    "https://www.phoronix.com/rss.php",
    "https://linux.org/forums/linux-news.52/index.rss",
    "https://archlinux.org/feeds/news/",
    "https://www.gentoo.org/feeds/news.xml",
    "https://voidlinux.org/atom.xml",
    "https://micronews.debian.org/feeds/feed.rss"
]
CHECK_INTERVAL = 300
SENT_FILE = "sent_links.txt"

class NewsBot(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.seen = self.load_seen()

    def load_seen(self):
        if os.path.exists(SENT_FILE):
            with open(SENT_FILE, "r") as f:
                return set(line.strip() for line in f)
        return set()

    def save_seen(self, link):
        with open(SENT_FILE, "a") as f:
            f.write(link + "\n")

    async def on_ready(self):
        print(f"Бот {self.user} запущен")
        self.loop.create_task(self.check_news())

    async def check_news(self):
        await self.wait_until_ready()
        while not self.is_closed():
            try:
                for url in RSS_URLS:
                    feed = feedparser.parse(url)
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

client = NewsBot()
client.run(TOKEN)
