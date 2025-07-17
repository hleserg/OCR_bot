"""
Телеграм бот для извлечения текста из изображений документов
"""

import asyncio
import logging
import os
import tempfile
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from config import BOT_TOKEN, LOG_LEVEL, LOG_FORMAT
from ocr_processor import OCRProcessor


class OCRTelegramBot:
    """
    Основной класс OCR телеграм бота
    """
    
    def __init__(self):
        """
        Инициализация OCR бота
        """
        # Настройка логирования
        logging.basicConfig(
            format=LOG_FORMAT,
            level=getattr(logging, LOG_LEVEL)
        )
        self.logger = logging.getLogger(__name__)
        
        # Инициализация OCR процессора
        self.ocr_processor = OCRProcessor()
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Обработчик команды /start
        """
        user_name = update.effective_user.first_name or "друг"
        
        welcome_text = f"""
🤖 Привет, {user_name}! Добро пожаловать в OCR бот!

📱 <b>Что я умею:</b>
Я извлекаю текст из изображений документов на русском и английском языках.

📷 <b>Как использовать:</b>
1. Отправьте мне фотографию документа
2. Я обработаю её и извлеку текст
3. Получите распознанный текст

⚙️ <b>Технологии:</b>
• OpenCV для предобработки изображений
• Tesseract OCR для распознавания текста
• Поддержка русского и английского языков

💡 <b>Рекомендации для лучшего результата:</b>
• Используйте четкие, хорошо освещенные фотографии
• Избегайте размытых изображений
• Убедитесь, что текст читаем

ℹ️ Для получения справки введите /help
        """
        
        await update.message.reply_text(welcome_text, parse_mode='HTML')
        self.logger.info(f"Пользователь {user_name} начал работу с OCR ботом")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Обработчик команды /help
        """
        help_text = """
🔍 <b>Как пользоваться OCR ботом:</b>

1️⃣ <b>Отправьте фотографию</b>
   • Просто загрузите изображение с документом
   • Поддерживаются форматы: JPG, PNG, GIF, BMP

2️⃣ <b>Подождите обработки</b>
   • Бот обработает изображение с помощью OpenCV
   • Применит OCR для извлечения текста

3️⃣ <b>Получите результат</b>
   • Извлеченный текст
   • Информацию о языке и количестве символов

🌐 <b>Поддерживаемые языки:</b>
• Русский (автоматическое определение)
• Английский (автоматическое определение)
• Смешанный текст (русский + английский)

📊 <b>Что показывает бот:</b>
• Распознанный текст
• Определенный язык
• Количество символов и слов
• Информацию о наличии цифр и спецсимволов

⚡ <b>Доступные команды:</b>
/start - Начать работу с ботом
/help - Показать эту справку

❗ <b>Ограничения:</b>
• Обрабатываются только изображения
• Качество распознавания зависит от четкости фото
• Максимальный размер файла определяется Telegram API

🛠️ <b>Технические детали:</b>
• Предобработка изображений с OpenCV
• OCR с помощью Tesseract
• Автоматическое определение языка

🤖 OCR бот готов извлечь текст из ваших документов!
        """
        
        await update.message.reply_text(help_text, parse_mode='HTML')
    
    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Обработчик фотографий
        """
        user_name = update.effective_user.first_name or "Пользователь"
        user_id = update.effective_user.id
        
        self.logger.info(f"Получена фотография от {user_name} (ID: {user_id})")
        
        # Отправляем сообщение о том, что обрабатываем
        processing_msg = await update.message.reply_text(
            "🔍 Обрабатываю изображение...\n"
            "⏳ Это может занять несколько секунд", 
            parse_mode='HTML'
        )
        
        try:
            # Получаем файл фотографии (берем самый большой размер)
            photo_file = await update.message.photo[-1].get_file()
            
            # Обновляем сообщение
            await processing_msg.edit_text(
                "📥 Загружаю изображение...", 
                parse_mode='HTML'
            )
            
            # Скачиваем файл в память
            photo_bytes = await photo_file.download_as_bytearray()
            
            # Обновляем сообщение
            await processing_msg.edit_text(
                "🔧 Предобрабатываю изображение с OpenCV...", 
                parse_mode='HTML'
            )
            
            # Извлекаем текст
            extracted_text = await self.ocr_processor.extract_text(photo_bytes)
            
            # Проверяем, что текст извлечен
            if not extracted_text or len(extracted_text.strip()) == 0:
                await processing_msg.edit_text(
                    "❌ <b>Не удалось извлечь текст</b>\n\n"
                    "💡 <b>Возможные причины:</b>\n"
                    "• Изображение слишком размытое\n"
                    "• Текст неразборчивый\n"
                    "• Неподдерживаемый язык\n"
                    "• Слишком сложный фон\n\n"
                    "🔄 Попробуйте другое изображение с более четким текстом.",
                    parse_mode='HTML'
                )
                return
            
            # Получаем информацию о тексте
            text_info = self.ocr_processor.get_text_info(extracted_text)
            
            # Определяем эмодзи для языка
            language_emoji = {
                'russian': '🇷🇺',
                'english': '🇺🇸',
                'mixed': '🌐',
                'unknown': '❓'
            }.get(text_info.get('language', 'unknown'), '❓')
            
            # Обрезаем текст если он слишком длинный для сообщения
            max_text_length = 3000
            display_text = extracted_text
            is_truncated = False
            
            if len(extracted_text) > max_text_length:
                display_text = extracted_text[:max_text_length] + "..."
                is_truncated = True
            
            # Формируем результат
            result_text = f"""
📄 <b>Результат извлечения текста:</b>

📝 <b>Извлеченный текст:</b>
<pre>{display_text}</pre>

📊 <b>Статистика:</b>
• Язык: {language_emoji} {text_info.get('language', 'unknown').title()}
• Символов: <b>{text_info.get('length', 0)}</b>
• Слов: <b>{text_info.get('words', 0)}</b>
• Строк: <b>{text_info.get('lines', 0)}</b>
• Содержит цифры: {'✅' if text_info.get('has_numbers', False) else '❌'}
• Спецсимволы: {'✅' if text_info.get('has_special_chars', False) else '❌'}
"""
            
            if is_truncated:
                result_text += f"\n⚠️ <i>Текст обрезан (показаны первые {max_text_length} символов)</i>"
            
            result_text += "\n\n📷 <i>Отправьте новое изображение для анализа!</i>"
            
            # Отправляем результат
            await processing_msg.edit_text(result_text, parse_mode='HTML')
            
            # Логируем результат
            self.logger.info(f"Обработка завершена для {user_name}: {len(extracted_text)} символов, язык: {text_info.get('language', 'unknown')}")
            
        except Exception as e:
            self.logger.error(f"Ошибка при обработке фотографии: {e}")
            await processing_msg.edit_text(
                "❌ <b>Произошла ошибка при обработке изображения</b>\n\n"
                "🔄 Попробуйте еще раз или отправьте другое изображение.\n"
                "💡 Убедитесь, что изображение содержит читаемый текст.",
                parse_mode='HTML'
            )
    
    async def handle_document(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Обработчик документов (изображений, отправленных как документы)
        """
        document = update.message.document
        
        # Проверяем, что это изображение
        if not document.mime_type or not document.mime_type.startswith('image/'):
            await update.message.reply_text(
                "❌ <b>Неподдерживаемый тип файла</b>\n\n"
                "📷 Пожалуйста, отправьте изображение (JPG, PNG, GIF, BMP).",
                parse_mode='HTML'
            )
            return
        
        # Проверяем размер файла (максимум 20MB)
        if document.file_size > 20 * 1024 * 1024:
            await update.message.reply_text(
                "❌ <b>Файл слишком большой</b>\n\n"
                "📏 Максимальный размер файла: 20MB\n"
                "🔄 Попробуйте сжать изображение или отправить файл меньшего размера.",
                parse_mode='HTML'
            )
            return
        
        user_name = update.effective_user.first_name or "Пользователь"
        user_id = update.effective_user.id
        
        self.logger.info(f"Получен документ-изображение от {user_name} (ID: {user_id})")
        
        # Отправляем сообщение о том, что обрабатываем
        processing_msg = await update.message.reply_text(
            "🔍 Обрабатываю документ-изображение...\n"
            "⏳ Это может занять несколько секунд", 
            parse_mode='HTML'
        )
        
        try:
            # Получаем файл документа
            doc_file = await document.get_file()
            
            # Обновляем сообщение
            await processing_msg.edit_text(
                "📥 Загружаю документ...", 
                parse_mode='HTML'
            )
            
            # Скачиваем файл в память
            doc_bytes = await doc_file.download_as_bytearray()
            
            # Обновляем сообщение
            await processing_msg.edit_text(
                "🔧 Предобрабатываю изображение с OpenCV...", 
                parse_mode='HTML'
            )
            
            # Извлекаем текст
            extracted_text = await self.ocr_processor.extract_text(doc_bytes)
            
            # Проверяем, что текст извлечен
            if not extracted_text or len(extracted_text.strip()) == 0:
                await processing_msg.edit_text(
                    "❌ <b>Не удалось извлечь текст</b>\n\n"
                    "💡 <b>Возможные причины:</b>\n"
                    "• Изображение слишком размытое\n"
                    "• Текст неразборчивый\n"
                    "• Неподдерживаемый язык\n"
                    "• Слишком сложный фон\n\n"
                    "🔄 Попробуйте другое изображение с более четким текстом.",
                    parse_mode='HTML'
                )
                return
            
            # Получаем информацию о тексте
            text_info = self.ocr_processor.get_text_info(extracted_text)
            
            # Определяем эмодзи для языка
            language_emoji = {
                'russian': '🇷🇺',
                'english': '🇺🇸',
                'mixed': '🌐',
                'unknown': '❓'
            }.get(text_info.get('language', 'unknown'), '❓')
            
            # Обрезаем текст если он слишком длинный для сообщения
            max_text_length = 3000
            display_text = extracted_text
            is_truncated = False
            
            if len(extracted_text) > max_text_length:
                display_text = extracted_text[:max_text_length] + "..."
                is_truncated = True
            
            # Формируем результат
            result_text = f"""
📄 <b>Результат извлечения текста из документа:</b>

📝 <b>Извлеченный текст:</b>
<pre>{display_text}</pre>

📊 <b>Статистика:</b>
• Язык: {language_emoji} {text_info.get('language', 'unknown').title()}
• Символов: <b>{text_info.get('length', 0)}</b>
• Слов: <b>{text_info.get('words', 0)}</b>
• Строк: <b>{text_info.get('lines', 0)}</b>
• Содержит цифры: {'✅' if text_info.get('has_numbers', False) else '❌'}
• Спецсимволы: {'✅' if text_info.get('has_special_chars', False) else '❌'}
"""
            
            if is_truncated:
                result_text += f"\n⚠️ <i>Текст обрезан (показаны первые {max_text_length} символов)</i>"
            
            result_text += "\n\n📷 <i>Отправьте новое изображение для анализа!</i>"
            
            # Отправляем результат
            await processing_msg.edit_text(result_text, parse_mode='HTML')
            
            # Логируем результат
            self.logger.info(f"Обработка документа завершена для {user_name}: {len(extracted_text)} символов, язык: {text_info.get('language', 'unknown')}")
            
        except Exception as e:
            self.logger.error(f"Ошибка при обработке документа: {e}")
            await processing_msg.edit_text(
                "❌ <b>Произошла ошибка при обработке документа</b>\n\n"
                "🔄 Попробуйте еще раз или отправьте другой файл.\n"
                "💡 Убедитесь, что файл содержит читаемый текст.",
                parse_mode='HTML'
            )
    
    async def handle_unsupported(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Обработчик неподдерживаемых типов сообщений
        """
        await update.message.reply_text(
            "❌ <b>Неподдерживаемый тип сообщения</b>\n\n"
            "📷 Я обрабатываю только изображения для извлечения текста.\n\n"
            "💡 <b>Что можно отправить:</b>\n"
            "• Фотографии документов\n"
            "• Изображения с текстом\n"
            "• Файлы изображений (JPG, PNG, GIF, BMP)\n\n"
            "🔄 Пожалуйста, отправьте изображение для анализа.",
            parse_mode='HTML'
        )
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Обработчик ошибок
        """
        self.logger.error(f"Ошибка в OCR боте: {context.error}")
        
        if update and update.message:
            await update.message.reply_text(
                "❌ <b>Произошла непредвиденная ошибка</b>\n\n"
                "🔄 Попробуйте еще раз или отправьте другое изображение.\n"
                "💡 Если проблема повторяется, обратитесь к администратору.",
                parse_mode='HTML'
            )
    
    def run(self):
        """
        Запуск OCR бота
        """
        self.logger.info("Создание приложения OCR бота...")
        
        # Создаем приложение
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Добавляем обработчики команд
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("help", self.help_command))
        
        # Добавляем обработчик фотографий
        application.add_handler(
            MessageHandler(filters.PHOTO, self.handle_photo)
        )
        
        # Добавляем обработчик документов-изображений
        application.add_handler(
            MessageHandler(filters.Document.IMAGE, self.handle_document)
        )
        
        # Добавляем обработчик неподдерживаемых сообщений
        application.add_handler(
            MessageHandler(~(filters.PHOTO | filters.Document.IMAGE | filters.COMMAND), self.handle_unsupported)
        )
        
        # Добавляем обработчик ошибок
        application.add_error_handler(self.error_handler)
        
        print("🤖 OCR бот запущен и готов к работе!")
        print("📷 Отправьте боту изображение для извлечения текста")
        print("🔧 Используется OpenCV + Tesseract OCR")
        print("🌐 Поддерживаются русский и английский языки")
        print("🛑 Нажмите Ctrl+C для остановки")
        
        self.logger.info("OCR бот запущен! Ожидание изображений...")
        
        # Запускаем бота
        try:
            print("▶️ Запуск polling...")
            application.run_polling(
                allowed_updates=Update.ALL_TYPES,
                drop_pending_updates=True
            )
        except KeyboardInterrupt:
            self.logger.info("Получен сигнал остановки OCR бота")
            print("\n🛑 OCR бот остановлен пользователем")
        except Exception as e:
            if "Conflict" in str(e):
                self.logger.error("Конфликт: другой экземпляр OCR бота уже запущен")
                print("❌ Ошибка: Другой экземпляр OCR бота уже запущен. Остановите его перед запуском нового.")
            else:
                self.logger.error(f"Критическая ошибка OCR бота: {e}")
                print(f"❌ Критическая ошибка OCR бота: {e}")


def main():
    """
    Главная функция запуска OCR бота
    """
    try:
        bot = OCRTelegramBot()
        bot.run()
    except Exception as e:
        print(f"❌ Не удалось запустить OCR бота: {e}")
        logging.error(f"Не удалось запустить OCR бота: {e}")


if __name__ == "__main__":
    main()
