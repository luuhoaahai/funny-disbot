import discord
from discord.ext import commands
from discord.utils import get
import os
from dotenv import load_dotenv
import datetime
import asyncio
from pymongo import MongoClient

uri = "mongodb://localhost:27017/"
client = MongoClient(uri)
db = client["tkbvabtvn"]
tkb = db["tkb"]
btvndb = db["btvn"]

cur_date = datetime.datetime.today().weekday()

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

spamming = False

def get_tomorrow() -> int:
    tomorrow = (cur_date + 2) % 7
    return tomorrow

def get_tkbnmai() -> str:
    tkb2 = tkb.find_one({"thu": get_tomorrow() + 1})
    tkbnmai = tkb2["value"] if tkb2 else "chưa có"
    return tkbnmai

@bot.event
async def on_ready():
    print(f"Bot ready: {bot.user} (ID: {bot.user.id})")

@bot.command(name="hello")
async def hello_command(ctx):
    await ctx.send(f"Hello, {ctx.author.mention}! 👋")


@bot.command(name="doitkb")
async def doi_tkb(ctx, thu: int, tkbmoi: str = None):
    if any(role.name == "admin top 1 sv" for role in ctx.author.roles):
        print("yes")
    else:
        return
    if tkbmoi is None:
        return await ctx.send("dcmm tkb ms có bell đâu")
    if thu not in range(2, 8):
        return await ctx.send("tkb thứ mấy?")

    old_doc = tkb.find_one({"thu": thu})
    old_value = old_doc["value"] if old_doc else "chưa có"

    tkb.update_one(
        {"thu": thu},
        {"$set": {"value": tkbmoi}},
        upsert=True
    )

    await ctx.send(f"đã đổi tkb thứ {thu} từ `{old_value}` thành `{tkbmoi}`")

@bot.command(name="tkb")
async def tkb_command(ctx):
    text = f"{ctx.author.mention} tkb đây bé:\n"
    for i in range(2, 8):
        doc = tkb.find_one({"thu": i})
        value = doc["value"] if doc else "chưa có"
        text += f"Thứ {i}: {value}\n"
    tomorrow = get_tomorrow()
    if tomorrow == 0:
        return await ctx.send(text + "\nmai nghỉ")
    text += f"\n**tkb ngày mai (Thứ {tomorrow + 1}):** {get_tkbnmai()}"

    await ctx.send(text)

@bot.command(name="thembtvn")
async def them_btvn(ctx, mon: str, btvn: str):
    if any(role.name == "admin top 1 sv" for role in ctx.author.roles):
        print("yes")
    else:
        return
    if mon is None:
        await ctx.send("mon jvcu")
        return
    if btvn is None:
        await ctx.send("btvn la jvaj")
    
    old_doc = btvndb.find_one({"mon": mon})
    old_val = old_doc["value"] if old_doc else ""
    
    btvndb.update_one(
        {"mon": mon},
        {"$set": {"value": old_val + ", " + btvn}},
        upsert=True
    )
    
    await ctx.send(f"đã thêm bài tập môn {mon} là: `{btvn}`")

@bot.command(name="btvn")
async def xem_btvn(ctx):
    text = "Bài tập hôm nay là: \n"
    for mon in get_tkbnmai().split(", "):
        print(mon)
        baitap = btvndb.find_one({"mon": mon})["value"] if btvndb.find_one({"mon": mon}) else "không có hoặc chưa ghi"
        text = text + f"{mon}: {baitap}\n"
    await ctx.send(text)
        

@bot.command(name="xoabtvn")
async def xoa_btvn(ctx, mon, baitap):
    if any(role.name == "admin top 1 sv" for role in ctx.author.roles):
        print("yes")
    else:
        return
    if mon is None:
        await ctx.send("mon jvcu")
        return
    if baitap is None:
        await ctx.send("btvn la jvaj")
    
    old_doc = btvndb.find_one({"mon": mon})
    old_val = old_doc["value"] if old_doc else ""
    
    btvndb.update_one(
        {"mon": mon},
        {"$set": {"value": old_val.removesuffix(", " + baitap)}},
        upsert=True
    )
    await ctx.send(f"đã xóa bài tập môn {mon}: `{baitap}`")

@bot.command(name="spam")
async def spam_command(ctx, message: str, delay: float):
    global spamming
    spamming = True

    await ctx.send(f"bắt đầu spam: `{message}` mỗi {delay}s")

    while spamming:
        await ctx.send(message)
        await asyncio.sleep(delay)


@bot.command(name="tatspam")
async def tatspam(ctx):
    global spamming
    spamming = False
    await ctx.send("đã tắt spam")

@bot.command(name="lenh")
async def all_code(ctx):
    cmds = [
        "!lenh",
        "!hello",
        "!tkb",
        "*!doitkb <thu> <noidung>",
        "!spam <text> <delay>",
        "!tatspam"
    ]
    await ctx.send("Tất cả lệnh:\n" + "\n".join(cmds))

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("dcmm dell co lenh nhu nay")
    else:
        await ctx.send(f"lỗi: {error}")

if __name__ == "__main__":
    if not TOKEN:
        raise ValueError("no token found")
    bot.run(TOKEN)
