import psycopg2
import asyncio
import pandas as pd
import matplotlib
from filter import filter_shd
from prognoz import prediction_linear_regression_shd
from visual import vis_overload_realtime
from new_data_to_df_log import new_data_to_df_log
from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware

matplotlib.use('Agg')

app = FastAPI()

app.add_middleware(CORSMiddleware, allow_origins=["*"],
                   allow_credentials=True,
                   allow_methods=["*"], allow_headers=['*'])

# Параметры подключения к PostgreSQL
db_params = {
    'host': 'post_cont',
    'port': '5432',
    'database': 'postgres',
    'user': 'postgres',
    'password': '1576',
    'connect_timeout': 5
}

prev_data = {}

data_mega = {}

offset = 0

result_shd_all = pd.DataFrame()


def execute_query_v2(query):
    try:
        # Устанавливаем соединение с базой данных
        connection = psycopg2.connect(**db_params)
        cursor = connection.cursor()

        print(query)

        # Выполняем SQL-запрос
        cursor.execute(query)

        # Получаем результаты запроса
        result = cursor.fetchall()

        # Получаем метаданные о столбцах
        column_names = [desc[0] for desc in cursor.description]

        # Фиксируем изменения в базе данных
        connection.commit()

        # Закрываем курсор и соединение
        cursor.close()
        connection.close()

        # Возвращаем результаты запроса и имена столбцов
        return result, column_names

    except psycopg2.Error as e:
        print(f"Ошибка при выполнении запроса: {e}")


# Функция для выполнения SQL-запроса к PostgreSQL
def execute_query(query):
    while True:
        try:
            connection = psycopg2.connect(**db_params)
            cursor = connection.cursor()

            cursor.execute(query)

            # Если запрос начинается с SELECT, получаем результат
            if query.strip().lower().startswith('select'):
                # Получение метаданных о столбцах
                column_names = [desc[0] for desc in cursor.description]
                result = cursor.fetchall()
            else:
                result = None

            connection.commit()

            cursor.close()
            connection.close()

            # Возвращаем результат и названия столбцов
            return result, column_names if 'column_names' in locals() else None


        except psycopg2.OperationalError as e:
            print(f"Ошибка при выполнении запроса: {e}")
            print("Повторная попытка подключения через 5 секунд...")

        except Exception as e:
            print(f"Произошла ошибка: {e}")
            return None


"""result_shd, column_names_shd = execute_query('select * from shd_from_csv')

if result_shd is not None:
    df_shd = pd.DataFrame(result_shd, columns=column_names_shd)

result_level, column_names_level = execute_query('select * from level')
if result_level is not None:
    df_levels = pd.DataFrame(result_level, columns=column_names_level)"""

# print('df_shd')
# print(df_shd)

# print('df_levels')
# print(df_levels)

"""vars_dict_real = {
    'features_columns': ['time'],  # Список колонок признаков, включая время sigh
    'targets_columns': ['Capacity usage(%)'],  # Список колонок целевых признаков target
}"""


@app.post("/api/get_graph")
async def get_shd_data(data: dict):
    global prev_data, result_shd_all, offset
    realtime = data.get('realtime')
    offset = 0
    """if realtime:
        result_shd_all = pd.DataFrame()"""
    prev_data = data
    """realtime = data.get('realtime')
    if realtime:
        return"""

    try:

        print(data)
        # Извлекаем необходимые параметры из данных
        param = [item['key'] for item in data['param']]
        sigh = str(data.get('sigh'))
        target = str(data.get('target'))
        sp_flag = data.get('sp_flag')
        select_window_type = str(data.get('select_window_type'))
        dropdown_block = data.get('dropdown_block', {})
        levels_list = [item['key'] for item in data['levels_list']]
        use_cloud = data.get('use_cloud')
        realtime = data.get('realtime')
        sqlRequest = str(data.get('sqlRequest'))
        try:
            sqlRequestLevel = data.get('sqlRequestLevel')
            print(33)
            execute_query(f"{sqlRequestLevel}")
            print(33)
            print(sqlRequestLevel)
        except:
            pass

        print(param)
        print(sigh)
        print(target)
        print(sp_flag)
        print(select_window_type)
        print(dropdown_block)
        print(levels_list)
        print(use_cloud)
        print(sqlRequest)
        print('realtime: ', realtime)

        try:

            """result_shd, column_names_shd = execute_query(f"{sqlRequest}")
            if result_shd is not None:
                df_shd = pd.DataFrame(result_shd, columns=column_names_shd)"""

            if select_window_type == 'auto_interval':
                # Разделение строки по пробелам
                tablitsa = sqlRequest.split()
                # Получение последнего слова
                tablitsa = tablitsa[-1]
                # Получение кол-ва строк датасета
                if len(param) == 1:
                    dlina = execute_query(f"SELECT COUNT(*) FROM {tablitsa} WHERE object = '{param[0]}'")

                    dlina = int(dlina[0][0][0])
                    half_dlina = int(dlina / 2)

                    print('dlina : ', dlina)
                    print('half_dlina : ', half_dlina)

                    result_shd, column_names_shd = execute_query(
                        f"{sqlRequest} WHERE object = '{param[0]}' order by time LIMIT {half_dlina}")
                elif len(param) == 2:
                    dlina = execute_query(
                        f"SELECT COUNT(*) FROM {tablitsa} WHERE object = '{param[0]}' or object = '{param[1]}'")

                    dlina = int(dlina[0][0][0])
                    half_dlina = int(dlina / 2)
                    if half_dlina % 2 != 0:  # Проверяем, является ли результат нечетным числом
                        half_dlina += 1  # Если да, уменьшаем на 1, чтобы сделать четным
                    print('dlina : ', dlina)
                    print('half_dlina : ', half_dlina)

                    result_shd, column_names_shd = execute_query(
                        f"{sqlRequest} WHERE object = '{param[0]}' or object = '{param[1]}' order by time LIMIT {half_dlina}")

                elif len(param) == 3:
                    dlina = execute_query(
                        f"SELECT COUNT(*) FROM {tablitsa} WHERE object = '{param[0]}' or object = '{param[1]}' or object = '{param[2]}'")

                    dlina = int(dlina[0][0][0])
                    half_dlina = int(dlina / 2)
                    if half_dlina % 3 != 0:  # Проверяем, делится ли результат на 3 с остатком
                        half_dlina += (3 - half_dlina % 3)  # Увеличиваем на оставшееся до ближайшего кратного числа 3
                    print('dlina : ', dlina)
                    print('half_dlina : ', half_dlina)

                    result_shd, column_names_shd = execute_query(
                        f"{sqlRequest} WHERE object = '{param[0]}' or object = '{param[1]}' or object = '{param[2]}' order by time LIMIT {half_dlina}")

                offset = half_dlina

                if result_shd is not None:
                    df_shd = pd.DataFrame(result_shd, columns=column_names_shd)

            elif select_window_type == 'advanced_interval':
                # Разделение строки по пробелам
                tablitsa = sqlRequest.split()
                # Получение последнего слова
                tablitsa = tablitsa[-1]

                gap = dropdown_block['interval']
                num = dropdown_block['interval_num']

                if gap == 'День':
                    gap = 'day'
                elif gap == 'Неделя':
                    gap = 'week'
                elif gap == 'Месяц':
                    gap = 'month'
                elif gap == 'Год':
                    gap = 'year'

                if len(param) == 1:
                    result_shd, column_names_shd = execute_query_v2(
                        f"WITH start_date AS (SELECT MIN(time) AS start_date FROM {tablitsa} WHERE object = '{param[0]}'), end_date AS (SELECT (SELECT start_date FROM start_date) + INTERVAL '{num} {gap}' - INTERVAL '1 day' AS end_date) SELECT * FROM {tablitsa}, start_date, end_date WHERE (object = '{param[0]}') AND (time BETWEEN (SELECT start_date FROM start_date) AND (SELECT end_date FROM end_date)) ORDER BY time")
                    dlina = execute_query_v2(
                        f"WITH start_date AS (SELECT MIN(time) AS start_date FROM {tablitsa} WHERE object = '{param[0]}'), end_date AS (SELECT (SELECT start_date FROM start_date) + INTERVAL '{num} {gap}' - INTERVAL '1 day' AS end_date) SELECT COUNT(*) FROM {tablitsa}, start_date, end_date WHERE (object = '{param[0]}') AND (time BETWEEN (SELECT start_date FROM start_date) AND (SELECT end_date FROM end_date))")
                    half_dlina = int(dlina[0][0][0])
                elif len(param) == 2:
                    result_shd, column_names_shd = execute_query_v2(
                        f"WITH start_date AS (SELECT MIN(time) AS start_date FROM {tablitsa} WHERE object = '{param[0]}' or object = '{param[1]}'), end_date AS (SELECT (SELECT start_date FROM start_date) + INTERVAL '{num} {gap}' - INTERVAL '1 day' AS end_date) SELECT * FROM {tablitsa}, start_date, end_date WHERE (object = '{param[0]}' or object = '{param[1]}') AND (time BETWEEN (SELECT start_date FROM start_date) AND (SELECT end_date FROM end_date)) ORDER BY time")
                    dlina = execute_query_v2(
                        f"WITH start_date AS (SELECT MIN(time) AS start_date FROM {tablitsa} WHERE object = '{param[0]}'), end_date AS (SELECT (SELECT start_date FROM start_date) + INTERVAL '{num} {gap}' - INTERVAL '1 day' AS end_date) SELECT COUNT(*) FROM {tablitsa}, start_date, end_date WHERE (object = '{param[0]}' or object = '{param[1]}') AND (time BETWEEN (SELECT start_date FROM start_date) AND (SELECT end_date FROM end_date))")
                    half_dlina = int(dlina[0][0][0])
                elif len(param) == 3:
                    result_shd, column_names_shd = execute_query_v2(
                        f"WITH start_date AS (SELECT MIN(time) AS start_date FROM {tablitsa} WHERE object = '{param[0]}' or object = '{param[1]}' or object = '{param[2]}'), end_date AS (SELECT (SELECT start_date FROM start_date) + INTERVAL '{num} {gap}' - INTERVAL '1 day' AS end_date) SELECT * FROM {tablitsa}, start_date, end_date WHERE (object = '{param[0]}' or object = '{param[1]}' or object = '{param[2]}') AND (time BETWEEN (SELECT start_date FROM start_date) AND (SELECT end_date FROM end_date)) ORDER BY time")
                    dlina = execute_query_v2(
                        f"WITH start_date AS (SELECT MIN(time) AS start_date FROM {tablitsa} WHERE object = '{param[0]}'), end_date AS (SELECT (SELECT start_date FROM start_date) + INTERVAL '{num} {gap}' - INTERVAL '1 day' AS end_date) SELECT COUNT(*) FROM {tablitsa}, start_date, end_date WHERE (object = '{param[0]}' or object = '{param[1]}' or object = '{param[2]}') AND (time BETWEEN (SELECT start_date FROM start_date) AND (SELECT end_date FROM end_date))")
                    half_dlina = int(dlina[0][0][0])

                offset = half_dlina
                if result_shd is not None:
                    df_shd = pd.DataFrame(result_shd, columns=column_names_shd)

            result_level, column_names_level = execute_query('select * from level')
            if result_level is not None:
                df_levels = pd.DataFrame(result_level, columns=column_names_level)

            # print('df_shd')
            # print(df_shd)

            df_filter_shd, df_filter_level, error1 = filter_shd(df_shd, df_levels, param)
            df_filter_shd_log, gui_dict1, error4 = new_data_to_df_log(df_filter_shd)
            print(2)
            vars_dict_real = {
                'features_columns': [sigh],
                'targets_columns': [target],
            }
            predict_model, df_predict, error2 = prediction_linear_regression_shd(df=df_filter_shd,
                                                                                 df_levels=df_filter_level,
                                                                                 vars_dict=vars_dict_real,
                                                                                 sp_flag=sp_flag,
                                                                                 select_window_type=select_window_type,
                                                                                 dropdown_block=dropdown_block,
                                                                                 levels_list=levels_list,
                                                                                 use_cloud=use_cloud)
            print(3)
            df_predict_log, gui_dict2, error5 = new_data_to_df_log(df_predict)
            result, error3 = vis_overload_realtime(df_filter_shd_log, df_predict_log, df_filter_level)

            result_shd_all = df_shd
        except Exception as e:
            if type(e).__name__ == 'OutOfBoundsDatetime':
                # Если возникает ошибка "OutOfBoundsDatetime", возвращаем ошибку сервера
                raise HTTPException(status_code=500, detail=(
                        'Невозможно построить график, т.к. крайняя точка очень удалена по времени\n' + str(e) +
                        '\nРекомендуем убрать галочку с параметра "облако точек"'
                ))
            elif type(e).__name__ == 'OverflowError':
                # Если возникает ошибка "timestamp out of range for platform time_t", возвращаем ошибку сервера
                raise HTTPException(status_code=500, detail=(
                        'Невозможно построить график, т.к. временная метка находится вне допустимого диапазона\n' + str(
                    e) +
                        '\nРекомендуем изменить временной дипазон"'
                ))
            elif type(e).__name__ == 'ValueError' and 'is out of range' in str(e):
                # Если возникает ошибка "year is out of range", возвращаем ошибку сервера
                raise HTTPException(status_code=500, detail=(
                        'Невозможно построить график, т.к. год находится вне допустимого диапазона\n' + str(e) +
                        '\nРекомендуем проверить годы"'
                ))
            elif type(e).__name__ == 'KeyError':
                # Если возникает ошибка "timestamp out of range for platform time_t", возвращаем ошибку сервера
                raise HTTPException(status_code=500, detail=(
                        'Неверно введены значения признаков/целевых признаков\n' + str(e) +
                        '\nРекомендуем проверить введенные значения"'
                ))
            elif type(e).__name__ == 'ValueError':
                raise HTTPException(status_code=500, detail=(
                        'Нет значений для построения графика\n' + str(e) +
                        '\nРекомендуем проверить датасет"'
                ))
            else:
                # В остальных случаях возвращаем общую ошибку сервера
                raise HTTPException(status_code=500, detail=str(e))
        # Возвращаем отфильтрованные данные в формате JSON
        return result
    except Exception as e:
        # Если возникает ошибка, возвращаем ошибку сервера
        raise HTTPException(status_code=500, detail=str(e))


@app.websocket("/api/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    global prev_data, result_shd_all, offset, data_mega
    x = 0
    while True:
        if prev_data:
            try:
                print('prev_data : ', prev_data)
                print('data_mega : ', data_mega)
                if data_mega != prev_data and data_mega != {}:
                    await asyncio.sleep(15)
                    x = 1
                else:
                    pass
                data_mega = prev_data
                data = prev_data  # Копируем данные для избежания изменения исходных данных
                # Извлекаем необходимые параметры из данных
                param = [item['key'] for item in data['param']]
                l = len(param)
                print(param)
                sigh = str(data.get('sigh'))
                target = str(data.get('target'))
                sp_flag = data.get('sp_flag')
                select_window_type = str(data.get('select_window_type'))
                dropdown_block = data.get('dropdown_block', {})
                levels_list = [item['key'] for item in data['levels_list']]
                use_cloud = data.get('use_cloud')
                sqlRequest = str(data.get('sqlRequest'))
                try:
                    sqlRequestLevel = data.get('sqlRequestLevel')
                    print(33)
                    execute_query(f"{sqlRequestLevel}")
                    print(33)
                    print(sqlRequestLevel)
                except:
                    pass

                print(param)
                print(sigh)
                print(target)
                print(sp_flag)
                print(select_window_type)
                print(dropdown_block)
                print(levels_list)
                print(use_cloud)
                print(sqlRequest)
                try:

                    if len(param) == 1:
                        result_shd, column_names_shd = execute_query(
                            f"{sqlRequest} where object = '{param[0]}' ORDER BY time LIMIT {l} offset {offset}")
                    elif len(param) == 2:
                        result_shd, column_names_shd = execute_query(
                            f"{sqlRequest} where object = '{param[0]}' or object = '{param[1]}' ORDER BY time LIMIT {l} offset {offset}")
                    elif len(param) == 3:
                        result_shd, column_names_shd = execute_query(
                            f"{sqlRequest} where object = '{param[0]}' or object = '{param[1]}' or object = '{param[2]}' ORDER BY time LIMIT {l} offset {offset}")
                    # result_shd, column_names_shd = execute_query(f"select * from shd_from_csv_v2 where object = 'System' ORDER BY time LIMIT 1 offset {offset}")

                    if result_shd is not None:
                        # Создайте DataFrame из результата запроса
                        df_shd = pd.DataFrame(result_shd, columns=column_names_shd)

                        print(df_shd)
                        print(result_shd_all)
                        result_shd_all_old = result_shd_all
                        # Добавьте данные к общему DataFrame
                        result_shd_all = pd.concat([result_shd_all, df_shd], ignore_index=True)
                        print('result_shd_all')
                        print(result_shd_all.to_string())
                        print('offset = ', offset)
                        if result_shd_all_old.equals(result_shd_all):
                            pass
                        else:
                            offset += l

                    result_level, column_names_level = execute_query('select * from level')
                    if result_level is not None:
                        df_levels = pd.DataFrame(result_level, columns=column_names_level)
                    print(228)

                    df_filter_shd, df_filter_level, error1 = filter_shd(result_shd_all, df_levels, param)
                    print(229)

                    print(df_levels)
                    print(df_filter_level)
                    df_filter_shd_log, gui_dict1, error4 = new_data_to_df_log(df_filter_shd)
                    print(230)
                    vars_dict_real = {
                        'features_columns': [sigh],
                        'targets_columns': [target],
                    }
                    predict_model, df_predict, error2 = prediction_linear_regression_shd(df=df_filter_shd,
                                                                                         df_levels=df_filter_level,
                                                                                         vars_dict=vars_dict_real,
                                                                                         sp_flag=sp_flag,
                                                                                         select_window_type=select_window_type,
                                                                                         dropdown_block=dropdown_block,
                                                                                         levels_list=levels_list,
                                                                                         use_cloud=use_cloud)
                    print(231)
                    df_predict_log, gui_dict2, error5 = new_data_to_df_log(df_predict)
                    print(232)
                    result, error3 = vis_overload_realtime(df_filter_shd_log, df_predict_log, df_filter_level)
                    print(233)
                except Exception as e:
                    if type(e).__name__ == 'OutOfBoundsDatetime':
                        # Если возникает ошибка "OutOfBoundsDatetime", возвращаем ошибку сервера
                        raise HTTPException(status_code=500, detail=(
                                'Невозможно построить график, т.к. крайняя точка очень удалена по времени\n' + str(e) +
                                '\nРекомендуем убрать галочку с параметра "облако точек"'
                        ))
                    elif type(e).__name__ == 'OverflowError':
                        # Если возникает ошибка "timestamp out of range for platform time_t", возвращаем ошибку сервера
                        raise HTTPException(status_code=500, detail=(
                                'Невозможно построить график, т.к. временная метка находится вне допустимого диапазона\n' + str(
                            e) +
                                '\nРекомендуем изменить временной дипазон"'
                        ))
                    elif type(e).__name__ == 'ValueError' and 'is out of range' in str(e):
                        # Если возникает ошибка "year is out of range", возвращаем ошибку сервера
                        raise HTTPException(status_code=500, detail=(
                                'Невозможно построить график, т.к. год находится вне допустимого диапазона\n' + str(e) +
                                '\nРекомендуем проверить годы"'
                        ))
                    elif type(e).__name__ == 'KeyError':
                        # Если возникает ошибка "timestamp out of range for platform time_t", возвращаем ошибку сервера
                        raise HTTPException(status_code=500, detail=(
                                'Неверно введены значения признаков/целевых признаков\n' + str(e) +
                                '\nРекомендуем проверить введенные значения"'
                        ))
                    elif type(e).__name__ == 'ValueError':
                        raise HTTPException(status_code=500, detail=(
                                'Нет значений для построения графика\n' + str(e) +
                                '\nРекомендуем проверить датасет"'
                        ))
                    else:
                        print(type(e))
                        # В остальных случаях возвращаем общую ошибку сервера
                        raise HTTPException(status_code=500, detail=str(e))
                # Возвращаем отфильтрованные данные в формате JSON
                await websocket.send_json(result)
            except Exception as e:
                await websocket.send_text(f"Error: {str(e)}")
        print('offset = ', offset)
        print('x = ', x)
        if x == 1:
            await asyncio.sleep(6)
            x = 0
        else:
            await asyncio.sleep(6)


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host="predict", port=8000)
