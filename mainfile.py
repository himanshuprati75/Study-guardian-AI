import json
import os
import asyncio
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ======== CONFIG ========

BOT_TOKEN = "8442524793:AAGRlqXGhLatf4U-7M2Yv7UzLchLqpWWwiI"
FILE_NAME = "tasks.json"

# ======== STORAGE ========

def load_tasks():
    if os.path.exists(FILE_NAME):
        with open(FILE_NAME, "r") as f:
            return json.load(f)
    return []

def save_tasks(tasks):
    with open(FILE_NAME, "w") as f:
        json.dump(tasks, f, indent=4)

tasks = load_tasks()

# ======== UTIL ========

def parse_time_input(time_str):
    now = datetime.now()
    if time_str.endswith("h"):
        hours = int(time_str[:-1])
        return now + timedelta(hours=hours)
    elif time_str.endswith("d"):
        days = int(time_str[:-1])
        return now + timedelta(days=days)
    else:
        return None

# ======== COMMANDS ========

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔥 Study Guardian AI Activated\n\n"
        "Commands:\n"
        "/add TaskName 2h high\n"
        "/list\n"
        "/done 1\n"
        "/report\n"
        "/motivate"
    )

async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        task_name = context.args[0]
        time_input = context.args[1]
        priority = context.args[2].lower()

        deadline = parse_time_input(time_input)
        if deadline is None:
            await update.message.reply_text("Invalid time format. Use 2h or 3d.")
            return

        tasks.append({
            "task": task_name,
            "priority": priority,
            "deadline": deadline.isoformat(),
            "completed": False
        })

        save_tasks(tasks)

        await update.message.reply_text(f"✅ Task Added: {task_name}")

    except:
        await update.message.reply_text("Usage: /add TaskName 2h high")

async def list_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not tasks:
        await update.message.reply_text("No tasks.")
        return

    message = "📋 Your Tasks:\n"
    for i, t in enumerate(tasks):
        status = "✅" if t["completed"] else "❌"
        message += f"{i+1}. {t['task']} ({t['priority']}) {status}\n"

    await update.message.reply_text(message)

async def done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        index = int(context.args[0]) - 1
        tasks[index]["completed"] = True
        save_tasks(tasks)
        await update.message.reply_text(f"🎉 Completed: {tasks[index]['task']}")
    except:
        await update.message.reply_text("Usage: /done 1")

async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    total = len(tasks)
    completed = sum(1 for t in tasks if t["completed"])
    pending = total - completed

    await update.message.reply_text(
        f"📊 Progress Report\n\n"
        f"Total: {total}\n"
        f"Completed: {completed}\n"
        f"Pending: {pending}"
    )

async def motivate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 Discipline beats motivation. Start now.")

# ======== REMINDER ENGINE ========

async def reminder_loop(app):
    while True:
        now = datetime.now()
        for t in tasks:
            if t["completed"]:
                continue

            deadline = datetime.fromisoformat(t["deadline"])
            remaining = (deadline - now).total_seconds()

            if remaining <= 0:
                await app.bot.send_message(
                    chat_id=list(app.bot_data["users"])[0],
                    text=f"🚨 OVERDUE: {t['task']}"
                )

            elif remaining <= 3600:
                if t["priority"] == "high":
                    interval = 300
                elif t["priority"] == "medium":
                    interval = 600
                else:
                    interval = 1200

                await app.bot.send_message(
                    chat_id=list(app.bot_data["users"])[0],
                    text=f"⏳ 1 hour left: {t['task']}"
                )

        await asyncio.sleep(300)

# ======== MAIN ========

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add))
    app.add_handler(CommandHandler("list", list_tasks))
    app.add_handler(CommandHandler("done", done))
    app.add_handler(CommandHandler("report", report))
    app.add_handler(CommandHandler("motivate", motivate))

    print("🤖 Bot Running...")
    app.run_polling()

if __name__ == "__main__":
    main()

