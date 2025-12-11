#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChatBook MVP - простой прототип для чтения текста из файла и ответов на вопросы.

Этот скрипт:
1. Читает текст из .txt файла
2. Разбивает текст на части (абзацы/предложения)
3. Отвечает на вопросы пользователя на основе содержимого файла
4. Использует простой поиск по ключевым словам (без нейросетей)
"""

import os
import sys
from typing import List, Tuple, Optional


def read_text_file(file_path: str) -> str:
    """
    Читает текст из файла и возвращает его содержимое.
    
    Args:
        file_path: Путь к текстовому файлу
        
    Returns:
        Строка с содержимым файла
        
    Raises:
        FileNotFoundError: Если файл не найден
        ValueError: Если файл пустой
    """
    # Проверяем существование файла
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Файл не найден: {file_path}")
    
    # Проверяем, что это файл, а не директория
    if not os.path.isfile(file_path):
        raise ValueError(f"Указанный путь не является файлом: {file_path}")
    
    # Читаем файл с правильной кодировкой для русского текста
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
    except UnicodeDecodeError:
        # Пробуем другие кодировки, если UTF-8 не подходит
        with open(file_path, 'r', encoding='cp1251') as file:
            text = file.read()
    
    # Проверяем, что файл не пустой
    if not text.strip():
        raise ValueError(f"Файл пустой: {file_path}")
    
    return text


def split_text(text: str, max_length: int = 5000) -> List[str]:
    """
    Разбивает текст на части (абзацы или предложения).
    
    Сначала пытается разбить по двойным переносам строк (абзацы),
    если части все еще слишком длинные, разбивает по предложениям.
    
    Args:
        text: Исходный текст
        max_length: Максимальная длина одной части (по умолчанию 5000 символов)
        
    Returns:
        Список частей текста
    """
    # Сначала разбиваем по абзацам (двойной перенос строки)
    parts = [part.strip() for part in text.split('\n\n') if part.strip()]
    
    # Если какие-то части все еще слишком длинные, разбиваем их по предложениям
    final_parts = []
    for part in parts:
        if len(part) <= max_length:
            final_parts.append(part)
        else:
            # Разбиваем по предложениям (точка, восклицательный или вопросительный знак)
            sentences = []
            current_sentence = ""
            
            for char in part:
                current_sentence += char
                if char in '.!?':
                    sentences.append(current_sentence.strip())
                    current_sentence = ""
            
            # Добавляем остаток, если есть
            if current_sentence.strip():
                sentences.append(current_sentence.strip())
            
            # Объединяем предложения в части нужной длины
            current_part = ""
            for sentence in sentences:
                if len(current_part) + len(sentence) + 1 <= max_length:
                    if current_part:
                        current_part += " " + sentence
                    else:
                        current_part = sentence
                else:
                    if current_part:
                        final_parts.append(current_part)
                    current_part = sentence
            
            if current_part:
                final_parts.append(current_part)
    
    return final_parts if final_parts else [text]


def find_answer(question: str, text_parts: List[str]) -> Tuple[str, int]:
    """
    Находит ответ на вопрос, используя простой поиск по ключевым словам.
    
    Ищет части текста, содержащие слова из вопроса, и возвращает наиболее релевантную.
    
    Args:
        question: Вопрос пользователя
        text_parts: Список частей текста для поиска
        
    Returns:
        Кортеж (найденный текст, количество совпадений)
    """
    # Приводим вопрос к нижнему регистру и разбиваем на слова
    question_lower = question.lower()
    # Убираем знаки препинания и разбиваем на слова
    question_words = [word.strip('.,!?;:()[]{}"\'') 
                     for word in question_lower.split() 
                     if len(word.strip('.,!?;:()[]{}"\'')) > 2]  # Игнорируем короткие слова
    
    if not question_words:
        return "Не удалось определить ключевые слова в вопросе.", 0
    
    best_match = ""
    best_score = 0
    
    # Ищем в каждой части текста
    for part in text_parts:
        part_lower = part.lower()
        score = 0
        
        # Подсчитываем количество совпадений ключевых слов
        for word in question_words:
            if word in part_lower:
                score += 1
        
        # Если нашли больше совпадений, обновляем лучший результат
        if score > best_score:
            best_score = score
            best_match = part
    
    # Если не нашли совпадений, возвращаем первую часть текста
    if best_score == 0:
        return "Не найдено точного совпадения. Вот начало текста:\n" + text_parts[0][:500], 0
    
    return best_match, best_score


def format_answer(answer_text: str, max_display_length: int = 1000) -> str:
    """
    Форматирует ответ для вывода, ограничивая длину при необходимости.
    
    Args:
        answer_text: Текст ответа
        max_display_length: Максимальная длина для отображения
        
    Returns:
        Отформатированный текст ответа
    """
    if len(answer_text) <= max_display_length:
        return answer_text
    
    # Обрезаем текст и добавляем указание на продолжение
    return answer_text[:max_display_length] + "\n\n[... текст обрезан ...]"


def main():
    """
    Основная функция для запуска ChatBook MVP.
    
    Читает файл, разбивает текст и позволяет задавать вопросы.
    """
    print("=" * 60)
    print("ChatBook MVP - Прототип для работы с текстовыми файлами")
    print("=" * 60)
    print()
    
    # Путь к файлу по умолчанию
    default_file = "narnia.txt"
    
    # Позволяем пользователю указать другой файл
    file_path = input(f"Введите путь к текстовому файлу (Enter для '{default_file}'): ").strip()
    if not file_path:
        file_path = default_file
    
    # Читаем файл
    try:
        print(f"\nЧтение файла: {file_path}")
        text = read_text_file(file_path)
        print(f"✓ Файл успешно прочитан. Размер: {len(text)} символов")
    except FileNotFoundError as e:
        print(f"❌ Ошибка: {e}")
        print("\nУбедитесь, что файл существует в указанном пути.")
        return
    except ValueError as e:
        print(f"❌ Ошибка: {e}")
        return
    except Exception as e:
        print(f"❌ Неожиданная ошибка при чтении файла: {e}")
        return
    
    # Разбиваем текст на части
    print("\nРазбиение текста на части...")
    text_parts = split_text(text)
    print(f"✓ Текст разбит на {len(text_parts)} частей")
    
    # Основной цикл вопросов
    print("\n" + "=" * 60)
    print("Можете задавать вопросы. Для выхода введите 'выход' или 'exit'")
    print("=" * 60)
    print()
    
    while True:
        question = input("Ваш вопрос: ").strip()
        
        # Проверяем команды выхода
        if question.lower() in ['выход', 'exit', 'quit', 'q']:
            print("\nДо свидания!")
            break
        
        if not question:
            print("Пожалуйста, введите вопрос.")
            continue
        
        # Ищем ответ
        try:
            answer, score = find_answer(question, text_parts)
            formatted_answer = format_answer(answer)
            
            print("\n" + "-" * 60)
            print("Ответ:")
            print("-" * 60)
            print(formatted_answer)
            if score > 0:
                print(f"\n(Найдено совпадений: {score})")
            print("-" * 60)
            print()
        except Exception as e:
            print(f"❌ Ошибка при поиске ответа: {e}")
            print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nПрограмма прервана пользователем.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        sys.exit(1)

