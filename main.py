from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import random
import json
import os
import asyncio

print("START BOT")

# 🔑 TOKEN (ONLY FROM RENDER ENV)
TOKEN = os.getenv("8313266747:AAHPDMft-wWMIvlQlcvvE7N5lmnlGjABpIc")
print("TOKEN LOADED:", TOKEN)

if not TOKEN:
    raise Exception("BOT_TOKEN is missing in Render environment variables")


# 👑 ADMINS
ADMINS = [6464074556]

DATA_FILE = "users.json"

users = {}
promo_codes = {}
chat_messages = []


# ---------- DATA ----------

def load_data():
    global users
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                users.update(json.load(f))
        except:
            pass


def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(users, f)


def get_user(user_id):
    user_id = str(user_id)
    if user_id not in users:
        users[user_id] = {"balance": 100, "nick": None}
        save_data()
    return users[user_id]


def is_admin(user_id):
    return user_id in ADMINS


load_data()


# ---------- START / HELP ----------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет!\n"
        "Бот запущен.\n\n"
        "Напиши /help"
    )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📌 КОМАНДЫ:\n\n"
        "/balance\n"
        "/p\n"
        "/nick имя\n\n"
        "/casino red/blue сумма\n"
        "/cubik число сумма\n"
        "/slots сумма\n\n"
        "/promo CODE\n"
        "/createpromo CODE сумма\n\n"
        "/chat текст\n"
        "/chatview\n\n"
        "/top\n"
        "/joke"
    )


# ---------- BALANCE ----------

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = get_user(update.effective_user.id)
    await update.message.reply_text(f"💰 Balance: {u['balance']}")


async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = get_user(update.effective_user.id)
    await update.message.reply_text(
        f"👤 Nick: {u['nick']}\n💰 Balance: {u['balance']}"
    )


# ---------- NICK ----------

async def nick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = get_user(update.effective_user.id)

    if not context.args:
        return await update.message.reply_text("/nick name")

    u["nick"] = context.args[0]
    save_data()
    await update.message.reply_text(f"✅ Nick set: {u['nick']}")


# ---------- CASINO ----------

async def casino(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = get_user(update.effective_user.id)

    if len(context.args) < 2:
        return await update.message.reply_text("/casino red 10")

    choice = context.args[0].lower()

    try:
        bet = int(context.args[1])
    except:
        return await update.message.reply_text("❌ Invalid bet")

    if bet < 5:
        return await update.message.reply_text("❌ Minimum 5")

    if u["balance"] < bet:
        return await update.message.reply_text("❌ Not enough balance")

    result = random.choice(["red", "blue"])

    if choice == result:
        u["balance"] += bet
        msg = f"🎉 WIN ({result}) +{bet}"
    else:
        u["balance"] -= bet
        msg = f"💀 LOSE ({result}) -{bet}"

    save_data()
    await update.message.reply_text(msg)


# ---------- CUBIK ----------

async def cubik(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = get_user(update.effective_user.id)

    if len(context.args) < 2:
        return await update.message.reply_text("/cubik 1 10")

    try:
        n = int(context.args[0])
        bet = int(context.args[1])
    except:
        return await update.message.reply_text("❌ Error")

    if u["balance"] < bet:
        return await update.message.reply_text("❌ No balance")

    r = random.randint(1, 6)

    if n == r:
        u["balance"] += bet * 3
        msg = f"🎲 WIN {r}"
    else:
        u["balance"] -= bet
        msg = f"🎲 LOSE {r}"

    save_data()
    await update.message.reply_text(msg)


# ---------- SLOTS ----------

symbols = ["🍒", "🍋", "🍊", "💎", "7️⃣"]

async def slots(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = get_user(update.effective_user.id)

    if not context.args:
        return await update.message.reply_text("/slots 10")

    bet = int(context.args[0])

    if bet < 5:
        return await update.message.reply_text("❌ Min 5")

    if u["balance"] < bet:
        return await update.message.reply_text("❌ No balance")

    msg = await update.message.reply_text("🎰 spinning...")

    for _ in range(3):
        r = f"{random.choice(symbols)} | {random.choice(symbols)} | {random.choice(symbols)}"
        await msg.edit_text(r)
        await asyncio.sleep(0.5)

    r1, r2, r3 = random.choice(symbols), random.choice(symbols), random.choice(symbols)

    if r1 == r2 == r3:
        win = bet * 10
        u["balance"] += win
        text = f"{r1}|{r2}|{r3}\n🔥 JACKPOT +{win}"
    else:
        u["balance"] -= bet
        text = f"{r1}|{r2}|{r3}\n💀 LOSE -{bet}"

    save_data()
    await msg.edit_text(text)


# ---------- JOKE ----------

async def joke(update: Update, context: ContextTypes.DEFAULT_TYPE):
    jokes = ["😂 bot joke", "💀 error 404", "🤣 crash moment", "🔥 dev sleeping"]
    await update.message.reply_text(random.choice(jokes))


# ---------- BOT ----------

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_cmd))
app.add_handler(CommandHandler("balance", balance))
app.add_handler(CommandHandler("p", profile))
app.add_handler(CommandHandler("nick", nick))
app.add_handler(CommandHandler("casino", casino))
app.add_handler(CommandHandler("cubik", cubik))
app.add_handler(CommandHandler("slots", slots))
app.add_handler(CommandHandler("joke", joke))

app.run_polling()
