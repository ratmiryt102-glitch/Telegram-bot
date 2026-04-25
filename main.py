from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import random
import json
import os
import asyncio

# 🔑 ТОКЕН
TOKEN = "8313266747:AAHPDMft-wWMIvlQlcvvE7N5lmnlGjABpIc"

# 👑 АДМИНЫ
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
        users[user_id] = {
            "balance": 100,
            "nick": None
        }
        save_data()
    return users[user_id]

def is_admin(user_id):
    return user_id in ADMINS

load_data()

# ---------- START / HELP ----------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
"""👋 Привет!
Этот бот создан @Tg_Jn0VaX
Тут ты можешь написать по поводу админки, фикса или идеи для добавки!

Чтобы посмотреть команды напиши /help"""
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
"""📌 КОМАНДЫ:

💰 /balance
👤 /p
👤 /nick имя

🎰 /casino red/blue сумма
🎲 /cubik число сумма
🎰 /slots сумма

💸 /transfer ник сумма

🎁 /promo CODE
👑 /createpromo CODE сумма

💬 /chat текст
💬 /chatview

🏆 /top

😂 /joke
"""
    )

# ---------- BALANCE ----------

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = get_user(update.effective_user.id)
    await update.message.reply_text(f"💰 GCube: {u['balance']}")

async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = get_user(update.effective_user.id)
    await update.message.reply_text(f"👤 Ник: {u['nick']}\n💰 GCube: {u['balance']}")

# ---------- NICK ----------

async def nick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = get_user(update.effective_user.id)

    if len(context.args) < 1:
        return await update.message.reply_text("/nick имя")

    u["nick"] = context.args[0]
    save_data()

    await update.message.reply_text(f"✅ Ник: {u['nick']}")

# ---------- CASINO ----------

async def casino(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = get_user(update.effective_user.id)

    if len(context.args) < 2:
        return await update.message.reply_text("/casino red 10")

    choice = context.args[0].lower()
    bet = int(context.args[1])

    if bet < 5:
        return await update.message.reply_text("❌ минимум 5 GCube")

    if u["balance"] < bet:
        return await update.message.reply_text("❌ нет GCube")

    result = random.choice(["red", "blue"])

    if choice == result:
        u["balance"] += bet * 2
        msg = f"🎉 WIN {result}"
    else:
        u["balance"] -= bet
        msg = f"💀 LOSE {result}"

    save_data()
    await update.message.reply_text(msg)

# ---------- CUBIK ----------

async def cubik(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = get_user(update.effective_user.id)

    if len(context.args) < 2:
        return await update.message.reply_text("/cubik 1 10")

    n = int(context.args[0])
    bet = int(context.args[1])

    if u["balance"] < bet:
        return await update.message.reply_text("❌ нет GCube")

    r = random.randint(1, 6)

    if n == r:
        u["balance"] += bet * 3
        msg = f"🎲 WIN {r}"
    else:
        u["balance"] -= bet
        msg = f"🎲 LOSE {r}"

    save_data()
    await update.message.reply_text(msg)

# ---------- SLOT MACHINE (АНИМАЦИЯ) ----------

symbols = ["🍒", "🍋", "🍊", "💎", "7️⃣"]

async def slots(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = get_user(update.effective_user.id)

    if len(context.args) < 1:
        return await update.message.reply_text("/slots сумма")

    bet = int(context.args[0])

    if bet < 5:
        return await update.message.reply_text("❌ минимум 5")

    if u["balance"] < bet:
        return await update.message.reply_text("❌ нет GCube")

    msg = await update.message.reply_text("🎰 крутится...")

    # 🎰 АНИМАЦИЯ
    for _ in range(3):
        r = f"{random.choice(symbols)} | {random.choice(symbols)} | {random.choice(symbols)}"
        await msg.edit_text(f"🎰 {r}")
        await asyncio.sleep(0.7)

    r1, r2, r3 = random.choice(symbols), random.choice(symbols), random.choice(symbols)
    result = f"{r1} | {r2} | {r3}"

    # WIN LOGIC
    if r1 == r2 == r3:
        win = bet * 10
        u["balance"] += win
        text = f"🎰 {result}\n🔥 JACKPOT +{win}"

    elif r1 == r2 or r1 == r3 or r2 == r3:
        win = bet * 2
        u["balance"] += win
        text = f"🎰 {result}\n✨ WIN +{win}"

    else:
        u["balance"] -= bet
        text = f"🎰 {result}\n💀 LOSE -{bet}"

    save_data()
    await msg.edit_text(text)

# ---------- JOKE ----------

async def joke(update: Update, context: ContextTypes.DEFAULT_TYPE):
    jokes = [
        "😂 Я просто бот",
        "💀 Ошибка 404",
        "🤣 Код сам себя сломал",
        "🔥 Программист спит",
    ]
    await update.message.reply_text(random.choice(jokes))

# ---------- PROMO ----------

async def createpromo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return

    code = context.args[0].upper()
    amount = int(context.args[1])

    promo_codes[code] = amount
    await update.message.reply_text(f"🎁 {code} +{amount}")

async def promo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = get_user(update.effective_user.id)

    code = context.args[0].upper()

    if code not in promo_codes:
        return await update.message.reply_text("❌ нет промо")

    u["balance"] += promo_codes[code]
    del promo_codes[code]
    save_data()

    await update.message.reply_text("🎉 получено!")

# ---------- CHAT ----------

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(context.args)

    if not text:
        return await update.message.reply_text("/chat текст")

    chat_messages.append(f"{update.effective_user.id}: {text}")

    if len(chat_messages) > 30:
        chat_messages.pop(0)

    await update.message.reply_text("✅ отправлено")

async def chatview(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("\n".join(chat_messages) or "пусто")

# ---------- TOP ----------

async def top(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sorted_users = sorted(users.items(), key=lambda x: x[1]["balance"], reverse=True)[:10]

    text = "🏆 TOP PLAYERS\n\n"

    for i, (uid, data) in enumerate(sorted_users, 1):
        name = data.get("nick") or uid
        text += f"{i}. {name} — {data['balance']} GCube\n"

    await update.message.reply_text(text)

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

app.add_handler(CommandHandler("promo", promo))
app.add_handler(CommandHandler("createpromo", createpromo))

app.add_handler(CommandHandler("chat", chat))
app.add_handler(CommandHandler("chatview", chatview))

app.add_handler(CommandHandler("top", top))

app.run_polling()
