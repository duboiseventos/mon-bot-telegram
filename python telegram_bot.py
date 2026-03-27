"""
╔══════════════════════════════════════════════════════════════╗
║              BOT TELEGRAM - BOUTIQUE CRYPTO                  ║
║  Paiement via Trust Wallet | Multi-langue | Commandes auto   ║
╚══════════════════════════════════════════════════════════════╝

INSTALLATION :
  pip install python-telegram-bot==20.7

LANCEMENT :
  python telegram_bot.py

OBTENIR UN TOKEN BOT :
  1. Ouvrir Telegram → chercher @BotFather
  2. Envoyer /newbot
  3. Suivre les instructions → copier le token ici

OBTENIR VOTRE CHAT ID (pour recevoir les commandes) :
  1. Ouvrir Telegram → chercher @userinfobot
  2. Envoyer /start → il vous affiche votre ID
"""


import logging
import os
import random
import string
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes, ConversationHandler
)

# ─────────────────────────────────────────────
# ⚙️  CONFIGURATION — À REMPLIR OBLIGATOIREMENT
# ─────────────────────────────────────────────

BOT_TOKEN = os.environ.get("BOT_TOKEN")
# Exemple : "7412345678:AAHxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

ADMIN_CHAT_ID = int(os.environ.get("ADMIN_CHAT_ID"))
# Remplacez par votre vrai Chat ID (entier, pas une string)
# Obtenez-le avec @userinfobot sur Telegram

# ─────────────────────────────────────────────
# 💰  ADRESSES TRUST WALLET (selon la crypto)
# ─────────────────────────────────────────────
# Collez ici les adresses copiées depuis Trust Wallet
# ⚠️  Vérifiez bien le réseau (TRC20 ≠ ERC20 ≠ BEP20)

WALLET_ADDRESSES = {
    "USDT_TRC20": "VOTRE_ADRESSE_USDT_TRC20_ICI",    # Réseau Tron
    "USDT_ERC20": "VOTRE_ADRESSE_USDT_ERC20_ICI",    # Réseau Ethereum
    "BNB_BEP20":  "VOTRE_ADRESSE_BNB_BEP20_ICI",     # Réseau BSC
    "BTC":        "VOTRE_ADRESSE_BITCOIN_ICI",         # Réseau Bitcoin
}

# ─────────────────────────────────────────────
# 🛍️  CATALOGUE — 4 ARTICLES À PERSONNALISER
# ─────────────────────────────────────────────
# Modifiez les noms, descriptions et prix selon vos produits
# Prix en EUR (€) — ils seront convertis automatiquement en crypto (à intégrer si besoin)

PRODUCTS = {
    "p1": {
        "name_fr": "Article 1",                          # ← Nom en français
        "name_es": "Artículo 1",                         # ← Nom en espagnol
        "name_en": "Product 1",                          # ← Nom en anglais
        "desc_fr": "Description de l'article 1",         # ← Description FR
        "desc_es": "Descripción del artículo 1",         # ← Description ES
        "desc_en": "Description of product 1",           # ← Description EN
        "price": 00.00,                                  # ← Prix en € (ex: 45.00)
        "emoji": "📦",                                   # ← Emoji décoratif
    },
    "p2": {
        "name_fr": "Article 2",
        "name_es": "Artículo 2",
        "name_en": "Product 2",
        "desc_fr": "Description de l'article 2",
        "desc_es": "Descripción del artículo 2",
        "desc_en": "Description of product 2",
        "price": 00.00,
        "emoji": "🎁",
    },
    "p3": {
        "name_fr": "Article 3",
        "name_es": "Artículo 3",
        "name_en": "Product 3",
        "desc_fr": "Description de l'article 3",
        "desc_es": "Descripción del artículo 3",
        "desc_en": "Description of product 3",
        "price": 00.00,
        "emoji": "✨",
    },
    "p4": {
        "name_fr": "Article 4",
        "name_es": "Artículo 4",
        "name_en": "Product 4",
        "desc_fr": "Description de l'article 4",
        "desc_es": "Descripción del artículo 4",
        "desc_en": "Description of product 4",
        "price": 00.00,
        "emoji": "💎",
    },
}

# ─────────────────────────────────────────────
# 🌐  TEXTES MULTILINGUES (interface du bot)
# ─────────────────────────────────────────────

TEXTS = {
    "fr": {
        "welcome":        "👋 Bienvenue ! Choisissez votre langue :",
        "choose_product": "🛍️ Choisissez un article :",
        "ask_name":       "📝 Quel est votre nom complet ?",
        "ask_address":    "🏠 Quelle est votre adresse de livraison ? (rue, ville, code postal, pays)",
        "ask_phone":      "📞 Votre numéro de téléphone ?",
        "ask_crypto":     "💰 Choisissez votre crypto pour payer :",
        "payment_info":   "✅ Commande enregistrée !\n\n📋 N° de commande : *{order_id}*\n\n💸 Envoyez *{price}€* en {crypto} à cette adresse :\n\n`{address}`\n\n⚠️ Indiquez le N° *{order_id}* dans la note/memo du paiement.\n\nMerci et bonne livraison ! 🚀",
        "order_received": "✅ Commande reçue ! Nous vous contactons dès confirmation du paiement.",
        "cancel":         "❌ Commande annulée. Tapez /start pour recommencer.",
    },
    "es": {
        "welcome":        "👋 ¡Bienvenido! Elige tu idioma:",
        "choose_product": "🛍️ Elige un artículo:",
        "ask_name":       "📝 ¿Cuál es tu nombre completo?",
        "ask_address":    "🏠 ¿Cuál es tu dirección de entrega? (calle, ciudad, código postal, país)",
        "ask_phone":      "📞 ¿Tu número de teléfono?",
        "ask_crypto":     "💰 Elige tu crypto para pagar:",
        "payment_info":   "✅ ¡Pedido registrado!\n\n📋 N° de pedido: *{order_id}*\n\n💸 Envía *{price}€* en {crypto} a esta dirección:\n\n`{address}`\n\n⚠️ Indica el N° *{order_id}* en la nota/memo del pago.\n\n¡Gracias y buena entrega! 🚀",
        "order_received": "✅ ¡Pedido recibido! Te contactamos al confirmar el pago.",
        "cancel":         "❌ Pedido cancelado. Escribe /start para empezar de nuevo.",
    },
    "en": {
        "welcome":        "👋 Welcome! Choose your language:",
        "choose_product": "🛍️ Choose a product:",
        "ask_name":       "📝 What is your full name?",
        "ask_address":    "🏠 What is your delivery address? (street, city, postal code, country)",
        "ask_phone":      "📞 Your phone number?",
        "ask_crypto":     "💰 Choose your crypto to pay:",
        "payment_info":   "✅ Order registered!\n\n📋 Order N°: *{order_id}*\n\n💸 Send *{price}€* in {crypto} to this address:\n\n`{address}`\n\n⚠️ Include N° *{order_id}* in the payment note/memo.\n\nThank you and enjoy your delivery! 🚀",
        "order_received": "✅ Order received! We'll contact you once payment is confirmed.",
        "cancel":         "❌ Order cancelled. Type /start to restart.",
    },
}

# ─────────────────────────────────────────────
# 🔢  ÉTATS DE LA CONVERSATION
# ─────────────────────────────────────────────

(
    STEP_LANG,       # Choix de la langue
    STEP_PRODUCT,    # Choix de l'article
    STEP_NAME,       # Saisie du nom
    STEP_ADDRESS,    # Saisie de l'adresse
    STEP_PHONE,      # Saisie du téléphone
    STEP_CRYPTO,     # Choix de la crypto
) = range(6)

# ─────────────────────────────────────────────
# 🔧  FONCTIONS UTILITAIRES
# ─────────────────────────────────────────────

def generate_order_id():
    """Génère un numéro de commande unique ex: ORD-X7K2A9"""
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"ORD-{suffix}"

def t(lang: str, key: str, **kwargs) -> str:
    """Retourne le texte traduit dans la langue choisie"""
    text = TEXTS.get(lang, TEXTS["fr"]).get(key, "")
    return text.format(**kwargs) if kwargs else text

def get_product_name(product: dict, lang: str) -> str:
    """Retourne le nom du produit selon la langue"""
    return product.get(f"name_{lang}", product["name_fr"])

def get_product_desc(product: dict, lang: str) -> str:
    """Retourne la description du produit selon la langue"""
    return product.get(f"desc_{lang}", product["desc_fr"])

# ─────────────────────────────────────────────
# 📩  ÉTAPE 1 : /start → Choix de la langue
# ─────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Point d'entrée du bot — propose le choix de la langue"""
    context.user_data.clear()  # Réinitialise la session

    keyboard = [
        [
            InlineKeyboardButton("🇫🇷 Français", callback_data="lang_fr"),
            InlineKeyboardButton("🇪🇸 Español",  callback_data="lang_es"),
            InlineKeyboardButton("🇬🇧 English",  callback_data="lang_en"),
        ]
    ]
    await update.message.reply_text(
        t("fr", "welcome"),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return STEP_LANG

# ─────────────────────────────────────────────
# 📩  ÉTAPE 2 : Langue choisie → Catalogue
# ─────────────────────────────────────────────

async def choose_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Enregistre la langue et affiche le catalogue de 4 articles"""
    query = update.callback_query
    await query.answer()

    lang = query.data.split("_")[1]           # "fr", "es" ou "en"
    context.user_data["lang"] = lang

    # Construction du clavier avec les 4 articles
    keyboard = []
    for pid, product in PRODUCTS.items():
        name = get_product_name(product, lang)
        price = product["price"]
        emoji = product["emoji"]
        label = f"{emoji} {name} — {price}€"
        keyboard.append([InlineKeyboardButton(label, callback_data=f"product_{pid}")])

    await query.edit_message_text(
        t(lang, "choose_product"),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return STEP_PRODUCT

# ─────────────────────────────────────────────
# 📩  ÉTAPE 3 : Article choisi → Demande le nom
# ─────────────────────────────────────────────

async def choose_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Enregistre le produit choisi et demande le nom du client"""
    query = update.callback_query
    await query.answer()

    lang = context.user_data["lang"]
    pid = query.data.split("_")[1]            # "p1", "p2", "p3" ou "p4"
    product = PRODUCTS[pid]

    context.user_data["product_id"] = pid
    context.user_data["product_name"] = get_product_name(product, lang)
    context.user_data["product_price"] = product["price"]

    # Affiche un résumé de l'article sélectionné
    desc = get_product_desc(product, lang)
    summary = f"{product['emoji']} *{get_product_name(product, lang)}*\n_{desc}_\n💶 {product['price']}€"

    await query.edit_message_text(summary, parse_mode="Markdown")
    await query.message.reply_text(t(lang, "ask_name"))
    return STEP_NAME

# ─────────────────────────────────────────────
# 📩  ÉTAPE 4 : Nom → Demande l'adresse
# ─────────────────────────────────────────────

async def receive_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Enregistre le nom et demande l'adresse de livraison"""
    lang = context.user_data["lang"]
    context.user_data["name"] = update.message.text.strip()

    await update.message.reply_text(t(lang, "ask_address"))
    return STEP_ADDRESS

# ─────────────────────────────────────────────
# 📩  ÉTAPE 5 : Adresse → Demande le téléphone
# ─────────────────────────────────────────────

async def receive_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Enregistre l'adresse et demande le numéro de téléphone"""
    lang = context.user_data["lang"]
    context.user_data["address"] = update.message.text.strip()

    await update.message.reply_text(t(lang, "ask_phone"))
    return STEP_PHONE

# ─────────────────────────────────────────────
# 📩  ÉTAPE 6 : Téléphone → Choix de la crypto
# ─────────────────────────────────────────────

async def receive_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Enregistre le téléphone et propose le choix de la crypto"""
    lang = context.user_data["lang"]
    context.user_data["phone"] = update.message.text.strip()

    # Boutons pour chaque crypto disponible dans WALLET_ADDRESSES
    keyboard = [
        [InlineKeyboardButton("💵 USDT (TRC20 - Tron)",     callback_data="crypto_USDT_TRC20")],
        [InlineKeyboardButton("💵 USDT (ERC20 - Ethereum)", callback_data="crypto_USDT_ERC20")],
        [InlineKeyboardButton("🟡 BNB (BEP20 - BSC)",       callback_data="crypto_BNB_BEP20")],
        [InlineKeyboardButton("🟠 Bitcoin (BTC)",            callback_data="crypto_BTC")],
    ]
    await update.message.reply_text(
        t(lang, "ask_crypto"),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return STEP_CRYPTO

# ─────────────────────────────────────────────
# 📩  ÉTAPE 7 : Crypto choisie → Récap + Paiement
# ─────────────────────────────────────────────

async def choose_crypto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Finalise la commande :
    - Génère un numéro de commande unique
    - Affiche l'adresse Trust Wallet + montant à envoyer
    - Envoie un récapitulatif complet à l'admin
    """
    query = update.callback_query
    await query.answer()

    lang = context.user_data["lang"]
    crypto_key = query.data.replace("crypto_", "")      # ex: "USDT_TRC20"
    wallet_address = WALLET_ADDRESSES.get(crypto_key, "ADRESSE_NON_CONFIGUREE")

    # Nom lisible de la crypto
    crypto_labels = {
        "USDT_TRC20": "USDT (TRC20)",
        "USDT_ERC20": "USDT (ERC20)",
        "BNB_BEP20":  "BNB (BEP20)",
        "BTC":        "Bitcoin (BTC)",
    }
    crypto_name = crypto_labels.get(crypto_key, crypto_key)

    # Génération du numéro de commande
    order_id = generate_order_id()
    context.user_data["order_id"] = order_id
    context.user_data["crypto"] = crypto_name
    context.user_data["wallet"] = wallet_address

    # ── Message au CLIENT avec instructions de paiement ──
    client_msg = t(lang, "payment_info",
        order_id=order_id,
        price=context.user_data["product_price"],
        crypto=crypto_name,
        address=wallet_address
    )
    await query.edit_message_text(client_msg, parse_mode="Markdown")
    await query.message.reply_text(t(lang, "order_received"))

    # ── Message à l'ADMIN avec récapitulatif complet ──
    admin_msg = (
        f"🛒 *NOUVELLE COMMANDE*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📋 N° : `{order_id}`\n"
        f"🌐 Langue : {lang.upper()}\n"
        f"\n"
        f"👤 *CLIENT*\n"
        f"Nom : {context.user_data['name']}\n"
        f"Adresse : {context.user_data['address']}\n"
        f"Téléphone : {context.user_data['phone']}\n"
        f"\n"
        f"🛍️ *ARTICLE*\n"
        f"Produit : {context.user_data['product_name']}\n"
        f"Prix : {context.user_data['product_price']}€\n"
        f"\n"
        f"💸 *PAIEMENT*\n"
        f"Crypto : {crypto_name}\n"
        f"Adresse : `{wallet_address}`\n"
        f"Statut : ⏳ En attente de confirmation"
    )

    try:
        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=admin_msg,
            parse_mode="Markdown"
        )
    except Exception as e:
        # Si l'envoi admin échoue (mauvais Chat ID), log l'erreur
        logging.error(f"Erreur envoi admin : {e}")

    return ConversationHandler.END

# ─────────────────────────────────────────────
# ❌  ANNULATION
# ─────────────────────────────────────────────

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Commande /cancel — annule la commande en cours"""
    lang = context.user_data.get("lang", "fr")
    await update.message.reply_text(t(lang, "cancel"))
    return ConversationHandler.END

# ─────────────────────────────────────────────
# 🚀  DÉMARRAGE DU BOT
# ─────────────────────────────────────────────

def main():
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO
    )

    # Construction de l'application avec votre token
    app = Application.builder().token(BOT_TOKEN).build()

    # Gestionnaire de conversation (flux principal)
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            STEP_LANG:    [CallbackQueryHandler(choose_language, pattern="^lang_")],
            STEP_PRODUCT: [CallbackQueryHandler(choose_product,  pattern="^product_")],
            STEP_NAME:    [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_name)],
            STEP_ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_address)],
            STEP_PHONE:   [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_phone)],
            STEP_CRYPTO:  [CallbackQueryHandler(choose_crypto,   pattern="^crypto_")],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)

    print("✅ Bot démarré ! Appuyez sur Ctrl+C pour arrêter.")
    app.run_polling()

if __name__ == "__main__":
    main()