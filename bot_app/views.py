import telebot
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Product, Order

TOKEN = '8066234942:AAFZhb0SnCsnE2yFRCgrBeSde-mlhPqA_64'
ADMIN_ID = 8513245980

bot = telebot.TeleBot(TOKEN)

# Foydalanuvchilar (va admin) holatlarini saqlash uchun xotira
user_states = {}


@csrf_exempt
def telegram_webhook(request):
    if request.method == 'POST':
        json_string = request.body.decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return HttpResponse("OK", status=200)
    return HttpResponse("Faqat POST so'rovlar qabul qilinadi.", status=400)


# --- KLAVIATURALAR ---

# Mijozlar uchun asosiy menyu (Mahsulotlar ro'yxati)
def get_client_keyboard():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    products = Product.objects.values_list('name', flat=True)
    for name in products:
        markup.add(telebot.types.KeyboardButton(name))
    return markup


# Admin uchun maxsus TG BOT ADMIN PANEL tugmalari
def get_admin_keyboard():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(telebot.types.KeyboardButton("📦 Buyurtmalar"), telebot.types.KeyboardButton("➕ Yangi mahsulot qo'shish"))
    markup.add(telebot.types.KeyboardButton("🏠 Mijoz rejimiga o'tish"))
    return markup


# --- COMMANDS ---

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id

    # SIZ ADMIN BO'LSANGIZ, TO'G'RIDAN-TO'G'RI TG BOT ADMIN PANEL CHIQADI
    if user_id == ADMIN_ID:
        bot.send_message(
            message.chat.id,
            "👋 Xush kelibsiz, hurmatli Admin!\n\nQuyidagi tugmalar orqali botni to'liq boshqarishingiz mumkin:",
            reply_markup=get_admin_keyboard()
        )
    else:
        # Oddiy mijozlarga shirinliklar menyusi chiqadi
        bot.send_message(
            message.chat.id,
            "Assalomu alaykum! Qandolatchilik do'konimiz botiga xush kelibsiz. Quyidagi menyudan shirinlik tanlang:",
            reply_markup=get_client_keyboard()
        )


# --- MAIN MESSAGE HANDLER ---

@bot.message_handler(func=lambda message: True, content_types=['text', 'photo', 'contact', 'location'])
def handle_all_messages(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    text = message.text

    # ----------------------------------------------------
    # 👑 1-BÖLIM: TG BOT ADMIN PANEL MANTIQI (FAQAT ADMIN UCHUN)
    # ----------------------------------------------------
    if user_id == ADMIN_ID and user_states.get(user_id, {}).get('step') not in ['get_order_amount', 'get_client_name',
                                                                                'get_client_phone', 'get_extra_phone',
                                                                                'get_location']:

        # Admin "Yangi mahsulot qo'shish" tugmasini bossa
        if text == "➕ Yangi mahsulot qo'shish":
            bot.send_message(chat_id, "📸 Yangi mahsulotning RASMINI yuboring:",
                             reply_markup=telebot.types.ReplyKeyboardRemove())
            user_states[user_id] = {'step': 'admin_image'}
            return

        # Admin "Buyurtmalar" tugmasini bossa
        elif text == "📦 Buyurtmalar":
            orders = Order.objects.all().order_by('-id')[:10]  # Oxirgi 10 ta buyurtma
            if not orders:
                bot.send_message(chat_id, "📭 Hozircha buyurtmalar mavjud emas.", reply_markup=get_admin_keyboard())
                return

            response = "📥 **Oxirgi kelgan buyurtmalar ro'yxati:**\n\n"
            for order in orders:
                response += f"👤 **Mijoz:** {order.client_name}\n📞 **Tel:** {order.phone}\n🍰 **Mahsulot:** {order.product_name}\n⏱ **Vaqti:** {order.created_at.strftime('%d-%m-%Y %H:%M')}\n------------------------\n"
            bot.send_message(chat_id, response, parse_mode="Markdown", reply_markup=get_admin_keyboard())
            return

        # Admin mijozlar menyusini ko'rmoqchi bo'lsa
        elif text == "🏠 Mijoz rejimiga o'tish":
            bot.send_message(chat_id,
                             "🛒 Mijozlar menyusi yuklandi. Admin panelga qaytish uchun /admin deb yozing yoki menyudan '⚙️ Admin panel' ni bosing.",
                             reply_markup=get_client_keyboard())
            return

        # Admin rejimiga qaytish buyrug'i
        elif text == "/admin" or text == "⚙️ Admin panel":
            bot.send_message(chat_id, "⚙️ Bot Admin Paneliga qaytdingiz:", reply_markup=get_admin_keyboard())
            return

        # Admin mahsulot qo'shish bosqichlari (Rasm, Nom, Narx olish)
        state = user_states.get(user_id, {})

        if state.get('step') == 'admin_image' and message.content_type == 'photo':
            user_states[user_id]['image_id'] = message.photo[-1].file_id  # Rasm ID sini eslab qoladi
            user_states[user_id]['step'] = 'admin_name'
            bot.send_message(chat_id, "✅ Rasm qabul qilindi. Endi mahsulot NOMINI yuboring:")
            return

        elif state.get('step') == 'admin_name' and message.content_type == 'text':
            user_states[user_id]['name'] = text
            user_states[user_id]['step'] = 'admin_price'
            bot.send_message(chat_id, "✅ Nom qabul qilindi. Endi mahsulot NARXINI yuboring (Masalan: 100,000 so'm):")
            return

        elif state.get('step') == 'admin_price' and message.content_type == 'text':
            name = state['name']
            image_id = state['image_id']

            # Mahsulotni Django bazasiga saqlaymiz
            Product.objects.create(name=name, price=text, image_id=image_id)

            del user_states[user_id]  # Admin holatini tozalaymiz
            bot.send_message(chat_id, f"🎉 Muvaffaqiyatli qo'shildi!\n🍰 Mahsulot: '{name}' menyuda paydo bo'ldi.",
                             reply_markup=get_admin_keyboard())
            return

    # ----------------------------------------------------
    # 🛒 2-BÖLIM: MIJOZ REJIMI VA MULTI-STEP BUYURTMA BERISH MANTIQI
    # ----------------------------------------------------
    state = user_states.get(user_id, {})

    # 1-Qadam: Mahsulotni qanchaga (shirinlik ulushini) olmoqchi ekanligini so'rash
    if state.get('step') == 'get_order_amount' and message.content_type == 'text':
        user_states[user_id]['order_amount'] = text
        user_states[user_id]['step'] = 'get_client_name'
        bot.send_message(chat_id, "🧁 Rahmat. Endi iltimos, ismingizni kiriting:")
        return

    # 2-Qadam: Mijoz ismi so'ralganda
    elif state.get('step') == 'get_client_name' and message.content_type == 'text':
        user_states[user_id]['client_name'] = text
        user_states[user_id]['step'] = 'get_client_phone'

        phone_markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        phone_markup.add(telebot.types.KeyboardButton("📱 Asosiy telefon raqamni yuborish", request_contact=True))
        bot.send_message(chat_id, "📞 Pastdagi tugmani bosib asosiy telefon raqamingizni yuboring:",
                         reply_markup=phone_markup)
        return

    # 3-Qadam: Mijoz asosiy telefoni so'ralganda
    elif state.get('step') == 'get_client_phone':
        phone_number = ""
        if message.content_type == 'contact' and message.contact is not None:
            phone_number = message.contact.phone_number
        elif message.content_type == 'text':
            phone_number = text
        else:
            bot.send_message(chat_id,
                             "Iltimos, telefon raqamingizni pastdagi tugma orqali yoki matn ko'rinishida yuboring.")
            return

        user_states[user_id]['phone'] = phone_number
        user_states[user_id]['step'] = 'get_extra_phone'
        bot.send_message(chat_id, "☎️ Qo'shimcha telefon raqamingizni kiriting (yoki 'yo'q' deb yozing):",
                         reply_markup=telebot.types.ReplyKeyboardRemove())
        return

    # 4-Qadam: Qo'shimcha telefon raqami so'ralganda
    elif state.get('step') == 'get_extra_phone' and message.content_type == 'text':
        user_states[user_id]['extra_phone'] = text
        user_states[user_id]['step'] = 'get_location'

        location_markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        location_markup.add(telebot.types.KeyboardButton("📍 Lokatsiyani yuborish", request_location=True))
        bot.send_message(chat_id,
                         "📍 Shirinlik yetkazilishi kerak bo'lgan manzilni (Lokatsiyani) pastdagi tugma orqali yuboring:\n⚠️ *(Eslatma: Yetkazib berish narxi alohida 10 000 so'm)*",
                         reply_markup=location_markup)
        return

    # 5-Qadam: Lokatsiya qabul qilinishi va buyurtmani tugatish
    elif state.get('step') == 'get_location':
        location_data = ""
        if message.content_type == 'location' and message.location is not None:
            location_data = f"https://maps.google.com/?q={message.location.latitude},{message.location.longitude}"
        elif message.content_type == 'text':
            location_data = text
        else:
            bot.send_message(chat_id,
                             "Iltimos, lokatsiyangizni pastdagi maxsus tugma orqali yoki matn ko'rinishida yuboring.")
            return

        # Ma'lumotlarni o'zgaruvchilarga olamiz
        product_name = state['buying_product']
        order_amount = state['order_amount']
        client_name = state['client_name']
        phone_number = state['phone']
        extra_phone = state['extra_phone']
        username = message.from_user.username

        # Buyurtmani Django bazasiga (Order modeliga) saqlaymiz.
        # Esingizda bo'lsin: Agar modelingizda qo'shimcha maydonlar (extra_phone, location) bo'lsa, ularni product_name yoki client_name ga qo'shib saqlashingiz mumkin yoki modelga o'sha maydonlarni qo'shib qo'yasiz.
        # Hozircha xato bermasligi uchun mahsulot nomi maydoniga summani ham qo'shib saqlaymiz:
        Order.objects.create(
            user_id=user_id,
            username=username,
            client_name=f"{client_name} (Qo'shimcha tel: {extra_phone})",
            phone=phone_number,
            product_name=f"{product_name} (Ulush: {order_amount} | Manzil: {location_data})"
        )

        # Mijozga yakuniy chek/rahmatnoma
        bot.send_message(
            chat_id,
            f"🎉 Rahmat, buyurtmangiz muvaffaqiyatli qabul qilindi!\n\n"
            f"🍰 Mahsulot: {product_name}\n"
            f"💰 So'ralgan ulush summasi: {order_amount}\n"
            f"🚴‍♂️ Yetkazib berish: 10 000 so'm\n\n"
            f"Tez orada operatorlarimiz siz bilan bog'lanishadi.",
            reply_markup=get_client_keyboard()
        )

        # Adminga barcha ma'lumotlar boradi (Lokatsiya linki bilan!)
        admin_alert = (
            f"🔔 **YANGI BUYURTMA KELDI (ULUSHLI)!**\n\n"
            f"👤 **Mijoz:** {client_name} (@{username if username else 'yoʻq'})\n"
            f"📞 **Asosiy Tel:** {phone_number}\n"
            f"☎️ **Qo'shimcha Tel:** {extra_phone}\n"
            f"🛒 **Mahsulot:** {product_name}\n"
            f"💵 **Xarid summasi:** {order_amount}\n"
            f"📍 **Manzil (Lokatsiya):** {location_data}\n"
            f"🚴‍♂️ **Yetkazib berish:** 10 000 so'm"
        )
        bot.send_message(ADMIN_ID, admin_alert, parse_mode="Markdown")

        del user_states[user_id]
        return

    # "🛒 Buyurtma berish:" tugmasi bosilganda (Jarayonni boshlash)
    if text and text.startswith("🛒 Buyurtma berish: "):
        product_name = text.replace("🛒 Buyurtma berish: ", "")
        user_states[user_id] = {'step': 'get_order_amount', 'buying_product': product_name}

        bot.send_message(
            chat_id,
            f"🧁 '{product_name}' mahsulotidan qancha qism (ulush) olmoqchisiz?\n\n"
            f"💰 Iltimos, xohlagan summangizni kiriting (Masalan: 20,000 so'm):",
            reply_markup=telebot.types.ReplyKeyboardRemove()
        )
        return

    # Mijoz (yoki admin mijoz rejimida) menyudan mahsulot tanlaganda rasm va narxini ko'rsatish
    if text:
        try:
            product = Product.objects.get(name=text)
            caption_text = f"✨ **{product.name}**\n\n💰 Umumiy narxi: {product.price}\n\n*(Eslatma: Ushbu mahsulotni o'zingizga ma'qul bo'lgan qismlarga bo'lib, xohlagan summangizga buyurtma berishingiz mumkin)*"

            order_markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
            order_markup.add(telebot.types.KeyboardButton(f"🛒 Buyurtma berish: {product.name}"))
            order_markup.add(telebot.types.KeyboardButton("⬅️ Orqaga"))

            if user_id == ADMIN_ID:
                order_markup.add(telebot.types.KeyboardButton("⚙️ Admin panel"))

            bot.send_photo(chat_id, product.image_id, caption=caption_text, reply_markup=order_markup,
                           parse_mode="Markdown")
        except Product.DoesNotExist:
            if text == "⬅️ Orqaga":
                if user_id == ADMIN_ID:
                    bot.send_message(chat_id, "Admin paneli:", reply_markup=get_admin_keyboard())
                else:
                    bot.send_message(chat_id, "Asosiy menyu:", reply_markup=get_client_keyboard())
            else:
                if user_id == ADMIN_ID:
                    bot.send_message(chat_id, "Tushunmadim. Admin panel tugmalaridan foydalaning:",
                                     reply_markup=get_admin_keyboard())
                else:
                    bot.send_message(chat_id, "Tushunmadim. Quyidagi menyudan shirinlik tanlang.",
                                     reply_markup=get_client_keyboard())