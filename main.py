import os
import easyocr
import psycopg2
from datetime import datetime

"""
В директории screenshots лежат скриншоты
Обходим каждый файл скриншота и распознаем
Результат сохраняем в таблицу баз данных PostgreSQL 
Заранее надо создать ее
CREATE TABLE public.running_strings (
  id serial NOT NULL,
  time_c timestamp NULL,
  "text" text NULL
);
"""

debug = True
directory = ("screenshots")
DB_dbname = "postgres"
DB_user = "postgres"
DB_password = ""
DB_host = "127.0.0.1"
DB_port = "5432"


def get_all_files(directory):
    """
    Обходит указанный каталог и возвращает список полных путей ко всем файлам.

    :param directory: Путь к каталогу для обхода
    :return: Список полных путей к файлам
    """
    file_paths = []
    if debug:
        print(f"Обходим каталог: {directory}")
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_cur = os.path.join(root, file)
            if debug:
                print(f"Текущий файл: {file_cur}")
            file_paths.append(file_cur)
            screenshot_parse(file_cur)
    return file_paths


def screenshot_parse(file_cur):
    """
    Распознаем текст на картинке и возвращаем строку

    :param file_cur: Путь к файлу скриншота
    :return: Текст с картинки
    """
    # file_cur = 'screenshots/screen_21.29.01_26.12.2024.jpg'
    if debug:
        print(f"Распознаем скриншот: {file_cur}")
    reader = easyocr.Reader(['ru'], gpu=True)
    result = reader.readtext(file_cur)
    text = ''
    for detection in result:
        text += detection[1] + ' '
    text = text.strip()
    if debug:
        print(f"Получили текст: {text}")
    insert_into_db(text)
    return text


def insert_into_db(text):
    """
    Вставляет строку в таблицу public.running_strings

    :param text: Текст для вставки
    """
    try:
        conn = psycopg2.connect(dbname=DB_dbname, user=DB_user, password=DB_password, host=DB_host, port=DB_port)
        cur = conn.cursor()
        insert_query = """
        INSERT INTO public.running_strings (time_c, text)
        VALUES (%s, %s);
        """
        cur.execute(insert_query, (datetime.now(), text))
        conn.commit()
        if debug:
            print(f"Успешно добавлена запись: {text}")
    except (Exception, psycopg2.Error) as error:
        if debug:
            print("Ошибка при работе с PostgreSQL", error)
        pass
    finally:
        if conn:
            cur.close()
            conn.close()

get_all_files(directory)