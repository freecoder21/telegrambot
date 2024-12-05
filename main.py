import os
import logging
from flask import Flask, request
import asyncio
from aiogram import Bot, Dispatcher, Router  # Importing necessary modules for the Telegram bot
from aiogram.filters import CommandStart  # To handle the "/start" command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton  # To create messages and buttons
from aiogram.exceptions import TelegramBadRequest
import aiohttp
from aiogram.types import ContentType

from aiogram.contrib.middlewares.logging import LoggingMiddleware

TOKEN = "7807538479:AAE1SzsrjS0t8JcqXai7UUhs4qFOE7Yp8WI"
CHANNEL_ID = -1002340148619
CHANNEL_INVITE_LINK = "https://t.me/+tKtZNXcN96E1N2Q0"
# Initializing the bot and setting up the dispatcher (the manager of events and updates)
bot = Bot(TOKEN)
dp = Dispatcher()

router = Router()
# Set up logging
logging.basicConfig(level=logging.INFO)

# Initialize Flask app and bot
app = Flask(__name__)
@app.route('/webhook', methods=['POST'])
async def webhook():
    json_str = await request.get_data(as_text=True)
    update = types.Update.parse_raw(json_str)
    await dp.process_update(update)
    return 'OK', 200
async def on_startup(dp):
    logging.info("Bot started")
    webhook_url = "https://api.render.com/deploy/srv-ct8jgsm8ii6s73cbfiag?key=FnzL9gWlVo4"
    await bot.set_webhook(webhook_url)


# A dictionary to store user data. Each user will have their own entry with specific details.
user_data = {}

subscribe_button = KeyboardButton(text="S'abonner 📢")
# Define buttons for the bot's reply keyboard
button1 = KeyboardButton(text="Inviter 🧑‍🤝‍🧑")  # Button for inviting friends
button2 = KeyboardButton(text="Solde 💲")        # Button to check balance
button3 = KeyboardButton(text="Retirer 💳")     # Button to withdraw earnings
button4 = KeyboardButton(text="Bonus 💰")       # Button to claim bonus
button5 = KeyboardButton(text="paramètre ⚡⚙️") # Button to check settings
button6 = KeyboardButton(text="🤷comment ça marche💡") # Button to see how the bot works

# Setting up the reply keyboard layout
subscrib_keyboard = ReplyKeyboardMarkup(
    keyboard=[[subscribe_button]],
    resize_keyboard= True
)
keyboard1 = ReplyKeyboardMarkup(
    keyboard=[
        [button1, button2],   # First row: Invite and Check Balance buttons
        [button3, button4, button5],  # Second row: Withdraw, Bonus, and Settings buttons
        [button6]             # Third row: "How it works" button
    ],
    resize_keyboard=True  # Makes the keyboard fit the screen better
)

# Handle the "/start" command when a user starts the bot
@router.message(CommandStart())
async def start_command_handler(message: Message, command: CommandStart):
    user_id = message.from_user.id  # Get the user's unique Telegram ID
    member = await bot.get_chat_member(CHANNEL_ID,user_id)

    inviter_id = None
    if command.args:
        inviter_id = int(command.args)  # Process the argument
    else:
        inviter_id = None  # Default to None if no arguments provided
    while member.status not in ["member", "administrator", "creator"]:
            # Send invite link message
            await message.answer(
                f"❗ Vous devez rejoindre notre canal avant d'utiliser le bot.\n\n"
                f"🔗 [Cliquez ici pour rejoindre notre canal]({CHANNEL_INVITE_LINK})",
                parse_mode="Markdown"
                )

    if member.status in ["member", "administrator", "creator"]:
        if user_id not in user_data:
            user_data[user_id] = {
                "name": message.from_user.first_name,  # Save first name
                "invite": 0,
                "sold": 0,
                "phone": '',
                "Bonus": 0,
                "subscribed": False,
                "check_if_invite": False,
                "invited_message": '',
                "invitedId": inviter_id
            }
        welcome_message = f"""
           🎉 **Bienvenue, {message.from_user.first_name} !** 🎉  
          🚀 Prêt à démarrer votre aventure pour gagner et grandir avec nous ?  

           🌟 **Voici comment commencer :**  
           1️⃣ Invitez vos amis avec votre lien de parrainage unique.  
           2️⃣ Gagnez des récompenses à chaque nouvel inscrit !  
           3️⃣ Consultez vos statistiques à tout moment dans le tableau de bord.  

           💰 **Plus vous invitez, plus vous gagnez !**  
           🔥 Prêt à débloquer vos premiers 1 000 points bonus ? Allons-y !  

           🎯 Appuyez sur les boutons ci-dessous pour explorer et commencer à gagner dès aujourd'hui.  
          📲 **Bonnes gains et amusez-vous !** 😊
                           """
        if inviter_id:
            user_data[inviter_id]['invite']+=1
            user_data[inviter_id]['sold']+=1000
            user_data[inviter_id]["check_if_invite"] = True
            user_data[inviter_id]['invited_message'] = (
                f"🎉 Félicitations ! La personne que vous avez invitée a rejoint avec succès. 🥳\n"
                f"🔄 Vos détails de compte mis à jour :\n"
                f"👥 Invitations : {user_data[inviter_id]['invite']}\n"
                f"💰 Solde : {user_data[inviter_id]['sold']}"
              )
        await message.answer(
            welcome_message,
            reply_markup=keyboard1
           )


# Handle user interactions with the keyboard buttons
@router.message()
async def keyboard_answers(message: Message):
    user_id = message.from_user.id  # Get the user's ID
    text = message.text  # Get the text of the button they clicked
    if user_data[user_id]["check_if_invite"]:
        # CHECK IF GUEST SUCCESSFULY LOGIN
        await message.answer(user_data[user_id]["invited_message"])
    # Check if the user is expected to input their phone number
    if user_data.get(user_id, {}).get("awaiting_phone", False):
        if text.isdigit() and len(text) >= 9:  # Validate phone number (basic check for digits and length)
            user_data[user_id]["phone"] = text  # Save the phone number
            user_data[user_id]["awaiting_phone"] = False  # Mark that phone input is complete
            await message.answer("📱 Merci pour votre numéro de téléphone ! Votre demande de retrait sera traitée sous peu. 💳")
            phone = user_data[user_id]['phone']
            # Ensure the phone number has at least 6 digits and replace the last 6 digits
            if len(phone) > 6:
                hidden_phone = f"{phone[:-6]}******"
            else:
                hidden_phone = "******"  # Handle cases where the phone number is shorter than 6 digits

            # SENDING PAYMENT MESSAGES TO THE CHANNEL
            payment_message = (
                f"💸 Nouvelle Demande de Paiement Réussie !**\n\n"
                f"👤 Utilisateur** : {user_data[user_id]['name']}\n"
                f"📱  Numéro : {hidden_phone}\n"
                f"🏦 Méthode de Paiement** : Mobile Payment\n"
                f"💳 Montant : {user_data[user_id]['sold']} FCFA\n\n"
                f"✅ STATUS : APPROUVÉ ✅"
            )
            try:
                await bot.send_message(chat_id=CHANNEL_ID, text=payment_message, parse_mode="Markdown")
            except TelegramBadRequest:
                await message.answer("❗ Une erreur s'est produite lors de l'envoi du message au canal.")

        else:
            await message.answer("❗ Le numéro saisi est invalide. Veuillez entrer un numéro de téléphone correct.")
        return  # Stop further processing for this input

    # Handle "Solde 💲" button
    if text == "Solde 💲":
        if user_id in user_data:
            remaining_invites = 10 - user_data[user_id]['invite']  # Calculate invites needed for withdrawal
            await message.answer(
                f"👨🏻‍💼 Nom : {user_data[user_id]['name']}\n"
                f"🧑‍🤝‍🧑 Amis invités : {user_data[user_id]['invite']}\n"
                f"💰 Solde actuel : {user_data[user_id]['sold']} FCFA\n\n"
                f"🚀 Il vous reste encore {remaining_invites} invitations pour atteindre le seuil de retrait !"
            )

    # Handle "Inviter 🧑‍🤝‍🧑" button
    elif text == "Inviter 🧑‍🤝‍🧑":
        invite_link = f"https://t.me/YoutubeComunityBot?start={user_id}"  # Generate invite link
        await message.answer(
            f"🔗 Votre lien d'invitation :\n{invite_link}\n\n"
            "🎯 Partagez ce lien pour gagner 1 000 FCFA par ami invité ! 💸"
        )

    # Handle "Retirer 💳" button
    elif text == "Retirer 💳":
        if user_data[user_id]['sold'] >= 10000:  # Check if user reached minimum balance
            user_data[user_id]['awaiting_phone'] = True  # Mark that phone input is awaited
            await message.answer("🎉 Félicitations ! Vous pouvez retirer vos gains. Entrez votre numéro de téléphone. 📱")
        else:
            remaining_amount = 10000 - user_data[user_id]['sold']  # Calculate amount needed
            await message.answer(
           f"❗ Solde insuffisant.\n"
            f"💰 Votre solde actuel : {user_data[user_id]['sold']} FCFA\n"
            f"🚀 Il vous manque seulement {remaining_amount} FCFA pour effectuer un retrait !\n"
            f"🔗 Continuez à inviter vos amis pour atteindre le montant nécessaire et profitez de vos gains !"
)

    # Handle "Bonus 💰" button
    elif text == "Bonus 💰":
        if user_data[user_id]["Bonus"] == 0:  # Check if bonus is unclaimed
            user_data[user_id]["sold"] += 300  # Add bonus to balance
            user_data[user_id]["Bonus"] = 1  # Mark bonus as claimed
            await message.answer(
            f"🎉 Félicitations ! Vous avez reçu un bonus de 300 FCFA !\n"
            f"💰 Votre nouveau solde : {user_data[user_id]['sold']} FCFA\n"
            f"🚀 Invitez encore plus d'amis pour obtenir des bonus supplémentaires et faire croître votre solde !"
)
        else:
            await message.answer("❗ Bonus déjà réclamé.")

    # Handle "paramètre ⚡⚙️" button
    elif text == "paramètre ⚡⚙️":
        await message.answer(
            f"⚡⚙️ Historique de Paiement ⚡⚙️\n\n"
            f"👤 Nom : {user_data[user_id]['name']}\n"
            f"💳 Solde : {user_data[user_id]['sold']} FCFA\n"
            f"🧑‍🤝‍🧑 Amis invités : {user_data[user_id]['invite']}\n"
            f"🆔 ID Utilisateur : {user_id}\n"
        )

    # Handle "🤷comment ça marche💡" button
    elif text == "🤷comment ça marche💡":
        await message.answer(
            "🤷 **Comment ça marche ?** 💡\n\n"
            "👨‍💻 **Q : Comment puis-je gagner de l'argent avec ce bot ?**\n"
            "👉 **R :** Vous gagnez de l'argent en invitant vos amis à utiliser ce bot. Chaque invitation réussie vous rapporte **1 000 FCFA** ! 🎉\n\n"
            "💰 **Q : Est-ce que je reçois un bonus au départ ?**\n"
            "👉 **R :** Oui, tous les nouveaux utilisateurs reçoivent un bonus de **300 FCFA** lors de leur première inscription ! Cliquez sur le bouton **réclamer 💰** pour récupérer votre bonus maintenant ! 🚀\n\n"
            "🔗 **Q : Comment partager mon lien d'invitation ?**\n"
            "👉 **R :** Cliquez sur le bouton **Inviter 🧑‍🤝‍🧑** pour obtenir votre lien d'invitation unique. Partagez ce lien avec vos amis et gagnez des bonus lorsque vos amis s'inscrivent avec votre lien ! 💸\n\n"
            "🎯 **Q : Combien puis-je gagner par invitation ?**\n"
            "👉 **R :** Vous gagnez **1 000 FCFA** chaque fois qu'une personne s'inscrit via votre lien. De plus, vous recevez un petit bonus à chaque clic sur votre lien ! 📈\n\n"
            "💳 **Q : Comment retirer mes gains ?**\n"
            "👉 **R :** Une fois que vous atteignez un solde de **10 000 FCFA**, vous pouvez demander un retrait. Cliquez sur le bouton **Retirer 💳** et suivez les instructions pour fournir votre numéro de téléphone. 📱\n\n"
            "🎉 **Q : Est-ce qu'il y a des limites ?**\n"
            "👉 **R :** Non, vous pouvez inviter autant d'amis que vous le souhaitez et continuer à augmenter vos gains sans limite ! 🚀\n\n"
            "⚡ **Astuce :** Utilisez le bot régulièrement et partagez votre lien pour maximiser vos revenus. Plus vous invitez, plus vous gagnez ! 💪"
        )

# Main function to start the bot
async def main():
    print("Bot is starting...")  # Print a message to the console
    dp.include_router(router)  # Add the router to the dispatcher
    await dp.start_polling(bot)  # Start listening for updates

# Run the main function if this file is executed
# Run the Flask app
if __name__ == '__main__':
    from aiogram import executor
    start_webhook(dispatcher=dp, webhook_path="/webhook", on_startup=on_startup)

