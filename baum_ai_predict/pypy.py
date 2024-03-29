import psycopg2
import pandas as pd
import matplotlib
from filter import filter_shd
from prognoz import prediction_linear_regression_shd
from visual import vis_overload_realtime
from new_data_to_df_log import new_data_to_df_log
from fastapi import FastAPI, HTTPException
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


# Функция для выполнения SQL-запроса к PostgreSQL
def execute_query(query):
    while True:
        try:
            connection = psycopg2.connect(**db_params)
            cursor = connection.cursor()

            cursor.execute(query)

            # Получение метаданных о столбцах
            column_names = [desc[0] for desc in cursor.description]

            # Если запрос начинается с SELECT, получаем результат
            if query.strip().lower().startswith('select'):
                result = cursor.fetchall()
            else:
                result = None

            connection.commit()

            cursor.close()
            connection.close()

            # Возвращаем результат и названия столбцов
            return result, column_names


        except psycopg2.OperationalError as e:
            print(f"Ошибка при выполнении запроса: {e}")
            print("Повторная попытка подключения через 5 секунд...")

        except Exception as e:
            print(f"Произошла ошибка: {e}")
            return None


result_shd, column_names_shd = execute_query('select * from shd_from_csv')

if result_shd is not None:
    df_shd = pd.DataFrame(result_shd, columns=column_names_shd)

result_level, column_names_level = execute_query('select * from level')
if result_level is not None:
    df_levels = pd.DataFrame(result_level, columns=column_names_level)

print('df_shd')
print(df_shd)

print('df_levels')
print(df_levels)

vars_dict_real = {
    'features_columns': ['time'],  # Список колонок признаков, включая время sigh
    'targets_columns': ['Capacity usage(%)'],  # Список колонок целевых признаков target
}


@app.post("/api/get_graph")
async def get_shd_data(data: dict):
    try:

        print(data)
        # Извлекаем необходимые параметры из данных
        param = [item['key'] for item in data['param']]
        sigh = str(data.get('sigh'))
        target = str(data.get('target'))
        sp_flag = str(data.get('sp_flag'))
        select_window_type = str(data.get('select_window_type'))
        dropdown_block = data.get('dropdown_block', {})
        levels_list = [item['key'] for item in data['levels_list']]
        use_cloud = data.get('use_cloud')

        print(param)
        print(sigh)
        print(target)
        print(sp_flag)
        print(select_window_type)
        print(dropdown_block)
        print(levels_list)
        print(use_cloud)

        result_shd, column_names_shd = execute_query('select * from shd_from_csv')
        if result_shd is not None:
            df_shd = pd.DataFrame(result_shd, columns=column_names_shd)

        result_level, column_names_level = execute_query('select * from level')
        if result_level is not None:
            df_levels = pd.DataFrame(result_level, columns=column_names_level)

        df_filter_shd, df_filter_level, error1 = filter_shd(df_shd, df_levels, param)
        print(1)
        df_filter_shd_log, gui_dict1, error4 = new_data_to_df_log(df_filter_shd)
        print(2)
        vars_dict_real = {
            'features_columns': [sigh],
            'targets_columns': [target],
        }

        predict_model, df_predict, error2 = prediction_linear_regression_shd(df_filter_shd, df_filter_level,
                                                                             vars_dict_real,
                                                                             sp_flag, select_window_type,
                                                                             dropdown_block,
                                                                             levels_list, use_cloud)


        df_predict_log, gui_dict2, error5 = new_data_to_df_log(df_predict)
        result, error3 = vis_overload_realtime(df_filter_shd_log, df_predict_log, df_filter_level)

        # Возвращаем отфильтрованные данные в формате JSON
        return result
    except Exception as e:
        # Если возникает ошибка, возвращаем ошибку сервера
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host="predict", port=8000)
