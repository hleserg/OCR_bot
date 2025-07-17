def extract_text(self, image_bytes, language='auto'):
    try:
        # Предварительная обработка изображения
        processed_image = self.preprocess_image(image_bytes)
        
        # Получаем конфигурацию Tesseract
        config = self.tesseract_config.get(language, self.tesseract_config['auto'])
        
        # Извлекаем текст
        text = pytesseract.image_to_string(processed_image, config=config)
        
        # Очищаем текст от лишних символов
        text = text.strip()
        
        # Удаляем пустые строки
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        cleaned_text = '\n'.join(lines)
        
        self.logger.info(f"Текст успешно извлечен, длина: {len(cleaned_text)} символов")
        return cleaned_text
        
    except Exception as e:
        self.logger.error(f"Ошибка при извлечении текста: {e}")
        raise
def extract_text(self, image_bytes, language='auto', psm=None):
    try:
        # Предварительная обработка изображения
        processed_image = self.preprocess_image(image_bytes)
        
        # Получаем конфигурацию Tesseract
        base_config = self.tesseract_config.get(language, self.tesseract_config['auto'])
        
        # Добавляем PSM параметр если он указан
        if psm is not None:
            base_config += f' --psm {psm}'
            
        # Извлекаем текст
        text = pytesseract.image_to_string(processed_image, config=base_config)
        
        # Очищаем текст от лишних символов
        cleaned_text = self._clean_text(text)
        
        self.logger.info(f"Текст успешно извлечен, длина: {len(cleaned_text)} символов")
        return cleaned_text
        
    except Exception as e:
        self.logger.error(f"Ошибка при извлечении текста: {e}")
        raise

def _clean_text(self, text):
    """Очистка текста от лишних символов"""
    text = text.strip()
    
    # Удаляем пустые строки
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    # Опционально: применяем кастомные правила очистки
    cleaned_lines = []
    for line in lines:
        if self.config.get('remove_special_chars', False):
            line = ''.join(c for c in line if c.isalnum() or c.isspace())
        cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines)
def detect_language(self, text):
    try:
        # Простая эвристика для определения языка
        russian_chars = len([c for c in text if 'а' <= c.lower() <= 'я' or c.lower() in 'ёъь'])
        english_chars = len([c for c in text if 'a' <= c.lower() <= 'z'])
        
        total_chars = russian_chars + english_chars
        
        if total_chars == 0:
            return 'unknown'
        
        russian_ratio = russian_chars / total_chars
        english_ratio = english_chars / total_chars
        
        if russian_ratio > 0.7:
            return 'russian'
        elif english_ratio > 0.7:
            return 'english'
        else:
            return 'mixed'
            
    except Exception as e:
        self.logger.error(f"Ошибка при определении языка: {e}")
        return 'unknown'
def detect_language(self, text):
    try:
        # Простая эвристика для определения языка
        russian_chars = len([c for c in text if 'а' <= c.lower() <= 'я' or c.lower() in 'ёъь'])
        english_chars = len([c for c in text if 'a' <= c.lower() <= 'z'])
        
        total_chars = russian_chars + english_chars
        
        if total_chars == 0:
            return 'unknown'
        
        russian_ratio = russian_chars / total_chars
        english_ratio = english_chars / total_chars
        
        if russian_ratio > 0.7:
            return 'russian'
        elif english_ratio > 0.7:
            return 'english'
        else:
            return 'mixed'
            
    except Exception as e:
        self.logger.error(f"Ошибка при определении языка: {e}")
        return 'unknown'
async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    ...
    photo_file = await update.message.photo[-1].get_file()
    ...
    photo_bytes = await photo_file.download_as_bytearray()
    ...
    extracted_text = self.ocr_processor.extract_text(photo_bytes)
    ...
async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    ...
    # Получаем файл фотографии (берем самый большой размер)
    photo_file = await update.message.photo[-1].get_file()
    
    # Проверяем размер изображения
    if photo_file.file_size > MAX_IMAGE_SIZE_FOR_PROCESSING:
        # Если изображение слишком большое, получаем меньший размер
        if len(update.message.photo) > 1:
            photo_file = await update.message.photo[-2].get_file()
        else:
            await processing_msg.edit_text(
                "🖼️ Изображение слишком большое для обработки. "
                "Попробуйте отправить изображение меньшего размера.",
                parse_mode='HTML'
            )
            return
    
    ...
    # Скачиваем файл в память
    photo_bytes = await photo_file.download_as_bytearray()
    
    # Преобразуем в numpy массив для OpenCV
    np_array = np.frombuffer(photo_bytes, dtype=np.uint8)
    img = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
    
    # Изменяем размер если нужно
    if max(img.shape[0], img.shape[1]) > MAX_IMAGE_DIMENSION:
        scale = MAX_IMAGE_DIMENSION / max(img.shape[0], img.shape[1])
        img = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
    
    # Преобразуем обратно в bytes
    _, buffer = cv2.imencode('.jpg', img)
    resized_bytes = buffer.tobytes()
    
    ...
    extracted_text = self.ocr_processor.extract_text(resized_bytes)
    ...
async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    ...
    # Получаем файл фотографии (берем самый большой размер)
    photo_file = await update.message.photo[-1].get_file()
    
    # Проверяем размер изображения
    if photo_file.file_size > MAX_IMAGE_SIZE_FOR_PROCESSING:
        # Если изображение слишком большое, получаем меньший размер
        if len(update.message.photo) > 1:
            photo_file = await update.message.photo[-2].get_file()
        else:
            await processing_msg.edit_text(
                "🖼️ Изображение слишком большое для обработки. "
                "Попробуйте отправить изображение меньшего размера.",
                parse_mode='HTML'
            )
            return
    
    ...
    # Скачиваем файл в память
    photo_bytes = await photo_file.download_as_bytearray()
    
    # Преобразуем в numpy массив для OpenCV
    np_array = np.frombuffer(photo_bytes, dtype=np.uint8)
    img = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
    
    # Изменяем размер если нужно
    if max(img.shape[0], img.shape[1]) > MAX_IMAGE_DIMENSION:
        scale = MAX_IMAGE_DIMENSION / max(img.shape[0], img.shape[1])
        img = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
    
    # Преобразуем обратно в bytes
    _, buffer = cv2.imencode('.jpg', img)
    resized_bytes = buffer.tobytes()
    
    ...
    extracted_text = self.ocr_processor.extract_text(resized_bytes)
    ...
def format_result(self, display_text, text_info, is_truncated, max_length):
    template = """
📄 <b>Результат извлечения текста:</b>

📝 <b>Извлеченный текст:</b>
<pre>{text}</pre>

📊 <b>Статистика:</b>
• Язык: {lang_emoji} {language}
• Символов: <b>{chars}</b>
• Слов: <b>{words}</b>
• Строк: <b>{lines}</b>
• Содержит цифры: {digits}
• Спецсимволы: {special_chars}
{truncated_note}
📷 <i>Отправьте новое изображение для анализа!</i>
"""
    
    language = text_info.get('language', 'unknown')
    lang_emoji = {
        'russian': '🇷🇺',
        'english': '🇺🇸',
        'mixed': '🌐',
        'unknown': '❓'
    }.get(language, '❓')
    
    truncated_note = ""
    if is_truncated:
        truncated_note = f"\n⚠️ <i>Текст обрезан (показаны первые {max_length} символов)</i>"
    
    return template.format(
        text=display_text,
        lang_emoji=lang_emoji,
        language=language.title(),
        chars=text_info.get('length', 0),
        words=text_info.get('words', 0),
        lines=text_info.get('lines', 0),
        digits='✅' if text_info.get('has_numbers', False) else '❌',
        special_chars='✅' if text_info.get('has_special_chars', False) else '❌',
        truncated_note=truncated_note
    )
def format_result(self, display_text, text_info, is_truncated, max_length):
    template = """
📄 <b>Результат извлечения текста:</b>

📝 <b>Извлеченный текст:</b>
<pre>{text}</pre>

📊 <b>Статистика:</b>
• Язык: {lang_emoji} {language}
• Символов: <b>{chars}</b>
• Слов: <b>{words}</b>
• Строк: <b>{lines}</b>
• Содержит цифры: {digits}
• Спецсимволы: {special_chars}
{truncated_note}
📷 <i>Отправьте новое изображение для анализа!</i>
"""
    
    language = text_info.get('language', 'unknown')
    lang_emoji = {
        'russian': '🇷🇺',
        'english': '🇺🇸',
        'mixed': '🌐',
        'unknown': '❓'
    }.get(language, '❓')
    
    truncated_note = ""
    if is_truncated:
        truncated_note = f"\n⚠️ <i>Текст обрезан (показаны первые {max_length} символов)</i>"
    
    return template.format(
        text=display_text,
        lang_emoji=lang_emoji,
        language=language.title(),
        chars=text_info.get('length', 0),
        words=text_info.get('words', 0),
        lines=text_info.get('lines', 0),
        digits='✅' if text_info.get('has_numbers', False) else '❌',
        special_chars='✅' if text_info.get('has_special_chars', False) else '❌',
        truncated_note=truncated_note
    )
   --oem 1 --psm 3  # Быстрый режим
   # Stage 1: Build
FROM python:3.11-slim as builder

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-rus \
    libglib2.0-0 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Final
FROM python:3.11-slim

# Установка Tesseract
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-rus \
    libglib2.0-0 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /app /logs

# Копирование зависимостей из stage 1
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONPATH=/root/.local/lib/python3.11/site-packages
COPY --from=builder /root/.local /root/.local

WORKDIR /app

# Копирование кода приложения
COPY . .

# Создание пользователя для безопасности
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app /logs
USER app

# Команда запуска
CMD ["python", "ocr_telegram_bot.py"]
# OCR Telegram Bot 🤖📄

Телеграм бот для извлечения текста из изображений документов с помощью OpenCV и Tesseract OCR.

## 🚀 Возможности

- **Извлечение текста** из фотографий документов
- **Поддержка языков**: русский, английский, смешанный текст
- **Предобработка изображений** с помощью OpenCV для улучшения качества OCR
- **Автоматическое определение языка** в распознанном тексте
- **Статистика текста**: количество символов, слов, строк
- **Поддержка различных форматов** изображений: JPG, PNG, GIF, BMP
- **Обработка документов** и обычных фотографий

## 🛠️ Технологии

- **Python 3.8+**
- **OpenCV** - предобработка изображений
- **Tesseract OCR** - распознавание текста
- **python-telegram-bot** - интеграция с Telegram
- **Pillow** - работа с изображениями

## 📦 Установка

### 1. Установка Python зависимостей

```bash
pip install -r requirements.txt
```

### 2. Установка Tesseract OCR

#### Windows:

1. **Скачайте Tesseract OCR для Windows:**
   - Перейдите на [UB Mannheim Tesseract](https://github.com/UB-Mannheim/tesseract/wiki)
   - Скачайте последнюю версию для Windows (например, `tesseract-ocr-w64-setup-5.3.3.20231005.exe`)

2. **Запустите установщик:**
   - Выберите язык установки
   - В разделе "Components" убедитесь, что выбран английский язык
   - Запомните путь установки (обычно `C:\Program Files\Tesseract-OCR`)

3. **Установите русский языковой пакет:**
   - Скачайте файл `rus.traineddata` с [GitHub tesseract-ocr/tessdata](https://github.com/tesseract-ocr/tessdata)
   - Скопируйте файл в папку `C:\Program Files\Tesseract-OCR\tessdata`

4. **Настройте переменные среды:**
   
   **Добавление в PATH:**
   - Откройте "Системные переменные" → "Переменные среды"
   - В "Системных переменных" найдите "Path" и нажмите "Изменить"
   - Добавьте путь: `C:\Program Files\Tesseract-OCR`
   
   **Создание TESSDATA_PREFIX:**
   - В "Системных переменных" нажмите "Создать"
   - Имя: `TESSDATA_PREFIX`
   - Значение: `C:\Program Files\Tesseract-OCR\tessdata`

5. **Проверьте установку:**
   ```bash
   tesseract --version
   tesseract --list-langs
   ```

#### Linux (Ubuntu/Debian):

```bash
sudo apt update
sudo apt install tesseract-ocr
sudo apt install tesseract-ocr-rus
```

#### macOS:

```bash
brew install tesseract
brew install tesseract-lang
```

### 3. Настройка бота

1. **Создайте бота в Telegram:**
   - Найдите [@BotFather](https://t.me/BotFather) в Telegram
   - Создайте нового бота командой `/newbot`
   - Получите токен бота

2. **Обновите конфигурацию:**
   - Откройте файл `config.py`
   - Замените `BOT_TOKEN` на токен вашего бота

## 🚀 Запуск

```bash
python ocr_telegram_bot.py
```

## 📝 Использование

1. **Запустите бота** командой `/start`
2. **Отправьте фотографию** документа или изображения с текстом
3. **Получите результат** с извлеченным текстом и статистикой

### Команды:
- `/start` - Начать работу с ботом
- `/help` - Получить справку по использованию

### Поддерживаемые форматы:
- **Фотографии**: JPG, PNG, GIF, BMP
- **Документы**: изображения, отправленные как файлы
- **Максимальный размер**: 20MB

## 🔧 Настройки OCR

### Tesseract конфигурация:
- **Режим OCR**: `--oem 3` (LSTM + Legacy)
- **Сегментация**: `--psm 6` (Единый блок текста)
- **Языки**: `rus+eng` (русский + английский)

### OpenCV предобработка:
- Конвертация в градации серого
- Размытие для удаления шума
- Пороговая обработка (OTSU)
- Морфологические операции
- Улучшение контрастности

## 📊 Функциональность

### Что показывает бот:
- ✅ **Извлеченный текст** из изображения
- 🌐 **Определенный язык** (русский/английский/смешанный)
- 📈 **Статистику**: символы, слова, строки
- 🔢 **Наличие цифр** и специальных символов
- ⚠️ **Предупреждения** при обрезке длинного текста

### Обработка ошибок:
- Проверка типа файла
- Проверка размера файла
- Обработка пустых результатов
- Информативные сообщения об ошибках

## 📁 Структура проекта

```
├── ocr_telegram_bot.py      # Основной файл OCR бота
├── ocr_processor.py         # Класс для обработки изображений и OCR
├── telegram_bot.py          # Существующий бот классификации
├── config.py               # Конфигурация (токен, настройки)
├── requirements.txt        # Python зависимости
├── README_OCR_Bot.md      # Данное руководство
└── model_loader.py        # Загрузчик модели (для классификации)
```

## 🐛 Решение проблем

### Tesseract не найден:
```bash
TesseractNotFoundError: tesseract is not installed
```
**Решение**: Убедитесь, что Tesseract установлен и добавлен в PATH

### Языковой пакет не найден:
```bash
TesseractError: Failed loading language 'rus'
```
**Решение**: Скачайте rus.traineddata и поместите в папку tessdata

### Плохое качество распознавания:
- Используйте четкие, хорошо освещенные фотографии
- Избегайте размытых изображений
- Убедитесь, что текст читаем
- Попробуйте обрезать изображение до текстовой области

### Проблемы с установкой OpenCV:
```bash
pip install opencv-python-headless
```

## 🔧 Продвинутые настройки

### Настройка качества OCR:
В файле `ocr_processor.py` можно изменить:
- Параметры размытия: `cv2.GaussianBlur(gray, (5, 5), 0)`
- Настройки пороговой обработки: `cv2.THRESH_BINARY + cv2.THRESH_OTSU`
- Морфологические операции: размер ядра

### Добавление новых языков:
1. Скачайте `.traineddata` файл для языка
2. Поместите в папку tessdata
3. Обновите конфигурацию в `ocr_processor.py`

## 📈 Производительность

### Время обработки:
- **Маленькие изображения** (< 1MB): 2-5 секунд
- **Средние изображения** (1-5MB): 5-10 секунд
- **Большие изображения** (> 5MB): 10-20 секунд

### Оптимизация:
- Сжимайте изображения перед отправкой
- Используйте четкие фотографии
- Обрезайте изображения до текстовой области

## 🤝 Поддержка

Если у вас возникли проблемы:
1. Проверьте, что все зависимости установлены
2. Убедитесь, что Tesseract настроен правильно
3. Проверьте логи бота для диагностики
4. Попробуйте разные изображения

## 📄 Лицензия

Этот проект использует open-source библиотеки:
- **Tesseract OCR**: Apache License 2.0
- **OpenCV**: BSD License
- **Python-telegram-bot**: LGPLv3

---

**Готов к использованию! 🎉**

Отправьте боту любую фотографию документа, и он извлечет из неё текст на русском или английском языке.
