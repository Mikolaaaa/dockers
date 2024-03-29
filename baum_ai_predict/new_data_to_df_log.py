from datetime import datetime
import pandas as pd
import numpy as np
from typing import Union
from DataLogs import DataLogs
from MainModel import MainModel
from init_gui_dict import init_gui_dict


def new_data_to_df_log(
        data: pd.DataFrame,
        data_logs: Union[DataLogs, None] = None,
        model: Union[MainModel, None] = None
) -> (DataLogs, str):
    """
    Записывает новые данные в датасет логирования для дальнейшего прогноза,
    data может быть пустой при авторегресии,
    проверяет ширину входных данных и типы данных.

    Если model передается None, значит, имеем дело с обычным могиторингом фактических значений.
    Если data_logs передается как None, значит, его нужно инициализировать.
    В data_logs.df_log записываем дату/время получения новых данных (индекс датасета),
    входящие реальные значения, промежуточные трансформации,
    трансформированные значения, прогнозные значения.
    Для временного ряда в каждый момент времени должно приходить одно значение!

    :code_assign: users
    :code_type: Анализ данных
    :imports: MainModel, DataLogs, init_gui_dict

    :packages:
    from datetime import datetime

    :param_block pd.DataFrame data DataSet: датасет с новыми данными
    :param_block DataLogs data_logs DFLog: датасет логирования
    :param_block MainModel model Model: модель

    :returns: data_logs, gui_dict, error
    :rtype: DataLogs, dict, str
    :semrtype: DFLog,  ,
    """

    # Инициализируем ошибку
    error = None

    gui_dict = init_gui_dict()

    # Из новых данных удаляем строки, где все значения NaN
    data = data.fillna(value=np.nan)
    data = data.dropna(how='all')

    # Фиксируем время получения новых данных
    now_ = pd.to_datetime(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))

    # Если датасет логирования не None
    if data_logs is not None:

        # если передана model
        if model is not None:
            # добавляем данные в df_log, используя vars_dict модели
            error = data_logs.add_data_with_vars_dict(
                new_data=data,
                now_=now_,
                model_vars_dict=model.vars_dict)
            # если ошибка, выходим
            if error: return data_logs, gui_dict, error

        # если model не передана
        else:
            # добавляем данные из data
            data_logs.add_data(new_data=data, now_=now_)

    # если data_logs не передан, то при добавлении новых данных его нужно инициализировать
    else:
        # если передана модель
        if model is not None:

            # инициализируем data_logs с помощью vars_dict из модели
            data_logs = DataLogs(model_vars_dict=model.vars_dict)
            # добавляем данные в df_log, используя vars_dict модели
            error = data_logs.add_data_with_vars_dict(
                new_data=data,
                now_=now_,
                model_vars_dict=model.vars_dict)
            # если ошибка, выходим
            if error: return data_logs, gui_dict, error

        # если модель не передана,
        # то есть случай мониторинга фактических значений без использования модели
        else:
            # инициализируем с помощью data и добавляем новые данные
            data_logs = DataLogs(new_data=data, now_=now_)

    # Таблица с последними 10 строками из датасета логирования
    gui_dataset = data_logs.df_log.iloc[-10:].fillna('')
    gui_dict['table'].append({
        'title': f'Датасет логирования (последние 10 строк):',
        'index': gui_dataset.index.strftime("%Y-%m-%d %H:%M:%S").to_list(),
        'value': gui_dataset.to_dict('list'),
    })

    # Таблица с новыми данными (последние 10 строк)
    data = data.fillna('')
    gui_dict['table'].append({
        'title': f'Новые данные (последние 10 строк):',
        'value': data.to_dict('list'),
    })

    # Возвращаем датасет логирования, словарь переменных, ошибку
    return data_logs, gui_dict, error