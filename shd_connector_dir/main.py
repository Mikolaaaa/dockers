import sys
import time
import signal
import logging
from datetime import datetime
from connector import authorize, establish_connection, api_diskspace
from tenacity import retry, stop_never, stop_after_attempt, wait_fixed

# Настройка логгера
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TIME_INERVAL = 1.0
LOGIN_SHD = "admin"
PASSWORD_SHD = "123456"

URL_LOGIN = "http://172.16.11.8/api/v2.0/login"
URL_DISKSPACE = "http://172.16.11.8/api/v2.0/disks"
URL_POOLSPACE = "http://172.16.11.8/api/v2.0/pools"
URL_LOGIN_BACKUP = "https://172.16.11.25/api/v1.0/login"
URL_DISKSPACE_BACKUP = "https://172.16.11.25/api/v1.0/disks"
URL_POOLSPACE_BACKUP = "https://172.16.11.25/api/v1.0/pools"

DATA_LOGIN = {"login": LOGIN_SHD, "password": PASSWORD_SHD, "remember": True}

# Конфигурация для подключения к базе данных
DATABASE = "postgres"
USER = "postgres"
PASSWORD = "1576"
HOST = "post_cont"
PORT = "5432"


def connect_to_postgres():
    logger.info("gbfddffd")
    return establish_connection(DATABASE, USER, PASSWORD, HOST, PORT)


def handle_interrupt(signal, frame):
    sys.exit(0)


def main():
    headers = {"content-type": "application/json"}
    time.sleep(2)
    connection = connect_to_postgres()

    try:
        cursor = connection.cursor()
        running = True
        try:
            while running:

                # Функция перевода объёма в ГБ
                def convert_to_gb(size_str):
                    unit = size_str[-1]
                    size = float(size_str[:-1])
                    if unit == 'T':
                        size *= 1024
                    if unit == 'K':
                        size /= 1024 * 1024
                    if unit == 'M':
                        size /= 1024
                    else:
                        pass
                    return size

                total = 0

                # Считывание дисков
                print(URL_DISKSPACE)

                data = api_diskspace(
                    URL_DISKSPACE,
                    authorize(URL_LOGIN, DATA_LOGIN, headers, URL_LOGIN_BACKUP),
                    URL_DISKSPACE_BACKUP
                )

                # Объём array
                for ppp in data:
                    if not ppp['props']['rdcache']:
                        total += ppp['size']

                # Перевод объёма array в ГБ
                total_cap_array = total / (1024 * 1024 * 1024)

                # Считывание пуллов
                print(URL_POOLSPACE)

                data = api_diskspace(
                    URL_POOLSPACE,
                    authorize(URL_LOGIN, DATA_LOGIN, headers, URL_LOGIN_BACKUP),
                    URL_POOLSPACE_BACKUP
                )

                i = 1

                used_cap_all = 0

                # Получение текущей даты и времени
                current_time = datetime.now().strftime('%Y-%m-%d')

                # Преобразование строки в объект datetime
                datetime_object = datetime.strptime(current_time, "%Y-%m-%d")

                # Считывание used_cap_pool, total_cap_pool и used_cap_array
                for ppp in data['pools']:
                    size = ppp['props']['size']
                    used = ppp['props']['used']
                    name = ppp['name']
                    print(f"used_cap_{name}:", used)
                    print(f"total_cap_{name}:", size)
                    if used != '0':
                        used = convert_to_gb(used)
                        size = convert_to_gb(size)
                        cursor.execute(
                            "INSERT INTO real_data (sn, \"object type\", object, time, \"Capacity usage(%%)\", \"Total capacity(MB)\", \"Used capacity(MB)\", array_num) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                            ("20240207000000", "Storage Pool", f"StoragePool00{i}", datetime_object,
                             (used / size) * 100, size,
                             used, "Array1"))
                        used_cap_all += used
                    i = i + 1

                print()
                print("total_cap_array:", total_cap_array, "G")
                print("used_cap_array:", used_cap_all, "G")

                # Вычисление процента загруженности array
                percent = used_cap_all / total_cap_array * 100

                print("% заполнения array:", percent)

                # Запись в БД
                cursor.execute(
                    "INSERT INTO real_data (sn, array_num, \"object type\", object, time, \"Capacity usage(%%)\", \"Total capacity(MB)\", \"Used capacity(MB)\") VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                    ("20240207000000", "Array1", "Array", "System", datetime_object, percent, total_cap_array,
                     used_cap_all))

                connection.commit()

                logger.info("Ждем следующие сутки")
                time.sleep(20)


        except KeyboardInterrupt:
            if signal.signal(signal.SIGINT, handle_interrupt):
                connection.close()
                print()

        finally:
            print()

    except ValueError:
        print("vpn disabled cannot connect to postgres")


if __name__ == "__main__":
    main()
