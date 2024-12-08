import telebot
import subprocess
import os
import signal
import json
from datetime import datetime, timedelta

# File to store approved users
APPROVED_USERS_FILE = 'approved_users.json'

# Global dictionaries
user_targets = {}
user_attacks = {}
approved_users = {}
admins = [7823487580, 5510109123]  # Replace with actual admin user IDs

bot_token = '7904440836:AAF_uJTGSV870WjyAxHmkB0M_nMVT19Thfg'
bot = telebot.TeleBot(bot_token)


# Helper functions
def is_admin(user_id):
    return user_id in admins


def is_approved(user_id):
    if user_id in approved_users:
        expiration = approved_users[user_id]['expiration']
        if datetime.now() <= datetime.strptime(expiration, "%Y-%m-%d %H:%M:%S"):
            return True
    return False


def load_approved_users():
    global approved_users
    if os.path.exists(APPROVED_USERS_FILE):
        with open(APPROVED_USERS_FILE, 'r') as f:
            approved_users = json.load(f)


def save_approved_users():
    with open(APPROVED_USERS_FILE, 'w') as f:
        json.dump(approved_users, f, indent=4)


# Command handler for /start
@bot.message_handler(commands=['start'])
def start_command(message):
    bot.reply_to(
        message,
        (
            "Welcome! Here are the available commands:\n"
            "/set_target - Set your target (Admins only)\n"
            "/start_attack - Start an attack (Admins only)\n"
            "/stop_attack - Stop the attack (Admins only)\n"
            "/approve - Approve a user (Admins only)\n"
            "/disapprove - Disapprove a user (Admins only)\n"
            "/approved_users - View all approved users (Admins only)\n"
            "/my_account - View your account status\n"
        ),
    )


# Command handler for /approve
@bot.message_handler(commands=['approve'])
def approve_command(message):
    user_id = message.chat.id
    if not is_admin(user_id):
        bot.reply_to(message, "Only admins can use this command.")
        return

    msg = bot.reply_to(
        message,
        "Please provide the user ID and approval duration (in hours) in this format: `USER_ID HOURS`",
        parse_mode='Markdown',
    )
    bot.register_next_step_handler(msg, process_approval)


def process_approval(message):
    try:
        user_id = message.chat.id
        if not is_admin(user_id):
            bot.reply_to(message, "You are not authorized to perform this action.")
            return

        user_id_to_approve, hours = message.text.split()
        user_id_to_approve = int(user_id_to_approve)
        hours = int(hours)

        expiration_time = datetime.now() + timedelta(hours=hours)
        approved_users[user_id_to_approve] = {
            'approved_by': user_id,
            'expiration': expiration_time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        save_approved_users()

        bot.reply_to(message, f"User {user_id_to_approve} approved for {hours} hours.")
    except Exception as e:
        bot.reply_to(message, f"Error processing approval: {e}")


# Command handler for /disapprove
@bot.message_handler(commands=['disapprove'])
def disapprove_command(message):
    user_id = message.chat.id
    if not is_admin(user_id):
        bot.reply_to(message, "Only admins can use this command.")
        return

    msg = bot.reply_to(message, "Please provide the user ID to disapprove.")
    bot.register_next_step_handler(msg, process_disapproval)


def process_disapproval(message):
    try:
        user_id = message.chat.id
        if not is_admin(user_id):
            bot.reply_to(message, "You are not authorized to perform this action.")
            return

        user_id_to_disapprove = int(message.text)

        if user_id_to_disapprove in approved_users:
            del approved_users[user_id_to_disapprove]
            save_approved_users()
            bot.reply_to(message, f"User {user_id_to_disapprove} has been disapproved.")
        else:
            bot.reply_to(message, "User is not in the approved list.")
    except Exception as e:
        bot.reply_to(message, f"Error processing disapproval: {e}")


# Command handler for /approved_users
@bot.message_handler(commands=['approved_users'])
def approved_users_command(message):
    user_id = message.chat.id
    if not is_admin(user_id):
        bot.reply_to(message, "Only admins can use this command.")
        return

    if not approved_users:
        bot.reply_to(message, "No approved users.")
    else:
        response = "Approved Users:\n"
        for user, details in approved_users.items():
            response += (
                f"User ID: {user}, Approved By: {details['approved_by']}, "
                f"Expiration: {details['expiration']}\n"
            )
        bot.reply_to(message, response)


# Command handler for /my_account
@bot.message_handler(commands=['my_account'])
def my_account_command(message):
    user_id = message.chat.id
    if is_admin(user_id):
        bot.reply_to(message, "You are an admin.")
    elif is_approved(user_id):
        expiration = approved_users[user_id]['expiration']
        bot.reply_to(
            message,
            f"You are an approved user. Your approval expires on {expiration}.",
        )
    else:
        bot.reply_to(message, "You are not approved.")


# Other command handlers (set_target, start_attack, stop_attack) remain the same
# Ensure they check is_approved(user_id) before proceeding


# Load approved users from file at startup
load_approved_users()

# Main polling loop
def main():
    print("Bot is starting...")
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            print(f"Error: {e}. Restarting bot...")
            continue


if __name__ == "__main__":
    main()