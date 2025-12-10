WhatsApp Bot Qo'llanmasi
WhatsApp orqali qanday qilib bot yaratish va ulash mumkin?

WhatsApp botni ulashning ikki xil usuli mavjud: Rasmiy API va Norasmiy QR kod orqali ulash. Quyida har ikkisi haqida batafsil ma'lumot berilgan.

## 1. Rasmiy WhatsApp Business API (Tavsiya etiladi)
Bu usul Meta (Facebook) tomonidan rasman qo'llab-quvvatlanadi. 

### Afzalliklari:
* Bloklanish xavfi juda past
* 24/7 stabil ishlash
* Rasmiy tasdiqlangan belgi (Green tick) olish imkoniyati

### Talablar:
* Facebook Business Manager akkaunti
* Biznes telefon raqami (WhatsAppda ishlatilmagan bo'lishi kerak)
* Kompaniya hujjati (Guvohnoma)

### Ulash tartibi:
1. Facebook Developers saytida yangi ilova yarating.
2. WhatsApp mahsulotini qo'shing.
3. Biznes raqamni tasdiqlang.
4. Olingan `Access Token` va `Phone Number ID` ni BotFactory paneliga kiriting.

## 2. QR Kod orqali ulash (Oson usul)
Bu usul xuddi WhatsApp Web kabi ishlaydi. Sizning telefon raqamingiz orqali bot ishlaydi.

### Afzalliklari:
* Tez va oson ulanish (5 daqiqa)
* Qo'shimcha hujjatlar talab qilinmaydi
* Bepul (API to'lovlarisiz)

### Kamchiliklari:
* Telefoningiz doim internetga ulangan bo'lishi kerak
* WhatsApp tomonidan bloklanish ehtimoli bor (agar spam qilinsa)
* Rasmiy emas

### Qanday ishlatish kerak?
Afsuski, hozirgi vaqtda BotFactory platformasida QR kod orqali ulanish imkoniyati to'g'ridan-to'g'ri integratsiya qilinmagan, chunki bu usul uchun alohida Node.js server talab qilinadi (whatsapp-web.js kutubxonasi orqali).

Agar sizga ushbu usul kerak bo'lsa, bizga administrator orqali murojaat qiling, biz sizga alohida server sozlashda yordam beramiz.

---

### Murojaat uchun:
Texnik yordam: @BotFactorySupport
Email: support@botfactory.uz
