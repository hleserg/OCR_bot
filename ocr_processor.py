"""
Модуль для обработки изображений и извлечения текста с помощью OCR
"""

import cv2
import numpy as np
import pytesseract
from PIL import Image
import io
import logging
import asyncio

class OCRProcessor:
    """
    Класс для обработки изображений и извлечения текста
    """
    
    def __init__(self):
        """
        Инициализация OCR процессора
        """
        self.logger = logging.getLogger(__name__)
        
        # Настройки для Tesseract
        self.tesseract_config = {
            'russian': '--oem 1 --psm 3 -l rus',
            'english': '--oem 1 --psm 3 -l eng',
            'auto': '--oem 1 --psm 3 -l rus+eng'
        }
    
    async def preprocess_image(self, image_bytes):
        """
        Асинхронная предварительная обработка изображения для улучшения OCR
        
        Args:
            image_bytes: Байты изображения
            
        Returns:
            Обработанное изображение
        """
        try:
            loop = asyncio.get_running_loop()
            
            def _process():
                # Конвертируем байты в изображение
                pil_image = Image.open(io.BytesIO(image_bytes))
                
                # Конвертируем в RGB если необходимо
                if pil_image.mode != 'RGB':
                    pil_image = pil_image.convert('RGB')
                
                # Конвертируем в numpy array для OpenCV
                cv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
                
                # Конвертируем в градации серого
                gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
                
                # Применяем адаптивную пороговую обработку
                thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
                
                # Применяем медианный фильтр для удаления шума
                denoised = cv2.medianBlur(thresh, 3)
                
                # Увеличиваем резкость
                kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
                sharpened = cv2.filter2D(denoised, -1, kernel)
                
                self.logger.info("Изображение успешно обработано")
                return sharpened
            
            return await loop.run_in_executor(None, _process)
            
        except Exception as e:
            self.logger.error(f"Ошибка при обработке изображения: {e}")
            raise
    
    async def extract_text(self, image_bytes, language='auto'):
        """
        Асинхронное извлечение текста из изображения
        
        Args:
            image_bytes: Байты изображения
            language: Язык для распознавания ('russian', 'english', 'auto')
            
        Returns:
            Распознанный текст
        """
        try:
            # Предварительная обработка изображения
            processed_image = await self.preprocess_image(image_bytes)
            
            # Получаем конфигурацию Tesseract
            config = self.tesseract_config.get(language, self.tesseract_config['auto'])
            
            loop = asyncio.get_running_loop()
            
            def _extract():
                # Извлекаем текст
                text = pytesseract.image_to_string(processed_image, config=config)
                
                # Очищаем текст от лишних символов
                text = text.strip()
                
                # Удаляем пустые строки
                lines = [line.strip() for line in text.split('\n') if line.strip()]
                cleaned_text = '\n'.join(lines)
                
                self.logger.info(f"Текст успешно извлечен, длина: {len(cleaned_text)} символов")
                return cleaned_text
            
            return await loop.run_in_executor(None, _extract)
            
        except Exception as e:
            self.logger.error(f"Ошибка при извлечении текста: {e}")
            raise
    
    def detect_language(self, text):
        """
        Определение языка текста
        
        Args:
            text: Текст для анализа
            
        Returns:
            Определенный язык ('russian', 'english', 'mixed')
        """
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
    
    def get_text_info(self, text):
        """
        Получение информации о тексте
        
        Args:
            text: Текст для анализа
            
        Returns:
            Словарь с информацией о тексте
        """
        try:
            info = {
                'length': len(text),
                'lines': len(text.split('\n')),
                'words': len(text.split()),
                'language': self.detect_language(text),
                'has_numbers': any(c.isdigit() for c in text),
                'has_special_chars': any(not c.isalnum() and not c.isspace() for c in text)
            }
            
            return info
            
        except Exception as e:
            self.logger.error(f"Ошибка при получении информации о тексте: {e}")
            return {}
    
    def detect_language(self, text):
        """
        Определение языка текста
        
        Args:
            text: Текст для анализа
            
        Returns:
            Определенный язык ('russian', 'english', 'mixed')
        """
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
    
    def get_text_info(self, text):
        """
        Получение информации о тексте
        
        Args:
            text: Текст для анализа
            
        Returns:
            Словарь с информацией о тексте
        """
        try:
            info = {
                'length': len(text),
                'lines': len(text.split('\n')),
                'words': len(text.split()),
                'language': self.detect_language(text),
                'has_numbers': any(c.isdigit() for c in text),
                'has_special_chars': any(not c.isalnum() and not c.isspace() for c in text)
            }
            
            return info
            
        except Exception as e:
            self.logger.error(f"Ошибка при получении информации о тексте: {e}")
            return {}
