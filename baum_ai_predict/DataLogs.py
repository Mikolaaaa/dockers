import pandas as pd
from typing import Union
import numpy as np
from Limits import Limits

class DataLogs():
    """
    Класс Логи данных
    Внимание! Для временных рядов индексы должны быть уникальные,
    в один момент времени должно передаваться одно наблюдение.
    Для других данных возможно несколько наблюдений в один момент времени.
    
    :code_assign: service
    :code_type: Анализ данных
    :imports: Limits

    Параметры:
    new_data: pd.DataFrame
        Датасет с новыми данными
    now_: Union[pd.Timestamp, None]
        Временная метка получения данных
    model_vars_dict: Union[dict, None]
        Словарь переменных от модели

    Атрибуты:
    vars_dict: dict
        Словарь переменных
    df_log: pd.Dataframe
        Датасет логирования
    new_rows_after_preprocess: bool     
        Флаг добавления новой строки после препроцессинга (временные ряды)
    check: dict
        Словарь проверок:
         - на принадлежность к интервалу min-max: по ключу ['limits'] записывается класс Limits()
    columns: list
        Вспомогательный список для столбцов
    columns_init: list
        Вспомогательный список для оригинальных столбцов
    """

    def __init__(
        self,
        new_data: pd.DataFrame = None,
        now_: Union[pd.Timestamp, None] = None,
        model_vars_dict: Union[dict, None] = None,
    ) -> None:

        # словарь переменных
        self.vars_dict = {}
        # флаг добавления новой строки после препроцессинга (временные ряды)
        self.new_rows_after_preprocess = False
        # словарь проверок
        self.check = {}
        
        # если передан словарь переменных от модели
        # создаем экземпляр с помощью инфо из model_vars_dict
        if model_vars_dict: self._create_from_model_vars_dict(model_vars_dict=model_vars_dict)
        # иначе делаем глубокую копию из new_data
        else: self._create_from_new_data(new_data=new_data, now_=now_)

    def _create_from_model_vars_dict(
        self,
        model_vars_dict: dict,        
    ) -> None:
        
        """ Создает датасет логирования и добавляет новые названия столбцов в словарь переменных """
        
        # формируем новые названия столбцов, которые будут использоваться для preprocess и predict
        # названия столбцов с входящими/фактическими значениями таргетов
        self.vars_dict['fact_targets_columns'] = [target_name + '_fact' for target_name in model_vars_dict['init_targets_columns']]
        # названия столбцов с прогнозными значениями
        self.vars_dict['predictions_columns'] = [target_name + '_pred' for target_name in model_vars_dict['init_targets_columns']]
        # названия столбцов с входящими/фактическими значениями признаков
        self.vars_dict['fact_features_columns'] = [feature_name + '_fact' for feature_name in model_vars_dict['init_features_columns']]

        # Сохраняем названия оригинальных столбцов
        self.vars_dict['init_targets_columns'] = model_vars_dict['init_targets_columns']
        # Сохраняем тип классификации
        self.vars_dict['class_type'] = model_vars_dict.get('class_type', None)
        
        # если наши данные - временной ряд
        if model_vars_dict.get('flag_ts', None):
            # если модель авторегрессии
            if model_vars_dict.get('steps_auto_regr', None):
                # создаем df_log только со столбцами для прогноза
                self.df_log = pd.DataFrame(columns = self.vars_dict['predictions_columns'])

                # названия столбцов
                self.columns = self.vars_dict['predictions_columns']
                # названия оригинальных столбцов
                self.columns_init = []

                # списки для преобразования типов
                key_list = self.vars_dict['predictions_columns']
                value_list = model_vars_dict['init_targets_columns']

            # иначе
            else:
                # создаем df_log со столбцами для прогноза, для целевых признаков, признаков
                self.df_log = pd.DataFrame(
                    columns = self.vars_dict['predictions_columns'] + \
                                self.vars_dict['fact_targets_columns'] + 
                                model_vars_dict['init_targets_columns'] + \
                                self.vars_dict['fact_features_columns'] + \
                                model_vars_dict['init_features_columns'] + \
                                model_vars_dict['features_columns'])
                # списки для преобразования типов
                key_list = self.vars_dict['predictions_columns'] + \
                           self.vars_dict['fact_targets_columns'] + model_vars_dict['init_targets_columns'] + \
                           self.vars_dict['fact_features_columns'] + model_vars_dict['init_features_columns']
                value_list = model_vars_dict['init_targets_columns'] * 3 +  model_vars_dict['init_features_columns'] * 2

                # названия столбцов для входящих значений таргетов и признаков
                self.columns = self.vars_dict['fact_targets_columns'] + self.vars_dict['fact_features_columns']
                # названия оригинальных столбцов таргетов и признаков
                self.columns_init = model_vars_dict['init_targets_columns'] + model_vars_dict['init_features_columns']

        # если не временной ряд
        else:
            # создаем df_log со столбцами для прогноза и признаков
            self.df_log = pd.DataFrame(
                columns = self.vars_dict['predictions_columns'] + \
                          self.vars_dict['fact_features_columns'] + \
                          model_vars_dict['features_columns'] +\
                          self.vars_dict['fact_targets_columns'])  


            # списки для преобразования типов
            key_list = self.vars_dict['predictions_columns'] + \
                            self.vars_dict['fact_targets_columns'] + \
                            self.vars_dict['fact_features_columns']
            value_list = model_vars_dict['init_targets_columns'] * 2 + model_vars_dict['init_features_columns']

            # названия столбцов для входящих значений признаков
            self.columns = self.vars_dict['fact_features_columns'] + self.vars_dict['fact_targets_columns']
            # названия оригинальных столбцов признаков
            self.columns_init = model_vars_dict['init_features_columns']

        # приводим столбцы к нужному типу данных у признаков в соответствии с типами из vars_dict['data_types']
        self.df_log = self.df_log.astype(dtype={**{key_list[i]: model_vars_dict['data_types'][value_list[i]] \
                                          for i in range(len(value_list))}})
        # features_columns отдельно приводим к float, так как это признаки для подачи в model
        self.df_log = self.df_log.astype(dtype={**{col: float \
                                          for col in model_vars_dict['features_columns']}})  

        # сохраняем список столбцов для использования в визуализции real time
        # значения столбцов _fact и _pred
        self.vars_dict['vis_cols_rt'] = [*filter(lambda x: x.endswith(('_pred', '_fact')) and self.df_log[x].dtype in (float, int), self.df_log.columns)]
        # значения столбцов _fact
        self.vars_dict['vis_cols_fact_rt'] = [*filter(lambda x: x.endswith('_fact'), self.vars_dict['vis_cols_rt'])]

    def _create_from_new_data(
        self,
        new_data: pd.DataFrame,
        now_: pd.Timestamp
        ) -> None:
        """ Создает датасет логирования через копию new_data """

        # делаем копию new_data
        self.df_log = new_data.copy(deep=True)
        # устанавливаем индекс, равный дате/времени получения данных
        self.df_log.set_index(pd.DatetimeIndex([now_] * len(new_data)), inplace=True)
        # сохраняем список столбцов для использования в визуализции real time
        # значения столбцов _fact и _pred
        self.vars_dict['vis_cols_rt'] = self.vars_dict['vis_cols_fact_rt'] = \
            [*filter(lambda x: self.df_log[x].dtype in (float, int), self.df_log.columns)]
        # сохраняем высоту входных данных
        self.vars_dict['data_height'] = len(new_data)

    def add_data(
        self,
        new_data: pd.DataFrame,
        now_: pd.Timestamp
    ) -> None:            
                
        # устанавливаем индекс
        new_data.set_index(pd.DatetimeIndex([now_] * len(new_data)), inplace=True)
        # добавляем данные из data в датасет логирования
        self.df_log = pd.concat([self.df_log, new_data])
        # сохраняем высоту входных данных
        self.vars_dict['data_height'] = len(new_data)
    
    def add_data_with_vars_dict(
        self,
        new_data: pd.DataFrame,
        now_: pd.Timestamp,
        model_vars_dict: dict
    ) -> str:
        """ Добавляет новые данные в датасет логирования с использованием информации из словаря переменнхы модели"""

        # инициализируем ошибку
        error = None

        # устанавливаем флаг набора данных
        accumulate = True
            
        # если нет данных, то ожидаем авторегрессию,
        # определяем по флагу steps_auto_regr
        # иначе ошибка (если нет данных с признаками и модель - не авторегрессия)
        if new_data is None and not self.vars_dict.get('steps_auto_regr', None):
            error = f"Ошибка: При остутствии входных признаков ожидается модель авторегрессии. ' +\
                    'Текущая модель - {self.vars_dict['model']}"
            return error
            
        # Проверяем ширину входных данных
        if len(new_data.columns) != len(self.columns):
            if len(new_data.columns) != len(self.columns) - len(self.vars_dict['fact_targets_columns']):
                error = 'Ошибка. Проверьте количество входных признаков в новых данных.' 
                return error
            
        # Проверяем типы столбцов новых данных на соответствие их указанным в vars_dict 
        if (new_data[self.columns_init].dtypes.values == model_vars_dict['data_types'][self.columns_init].values).sum() != \
            len(model_vars_dict['data_types'][self.columns_init]):
            try:
                # Пробуем привести к нужному типу данных
                new_data = new_data.astype(dtype={**{self.columns_init[i]: model_vars_dict['data_types'][self.columns_init[i]] \
                                          for i in range(len(self.columns_init))}})
            except:
                # Выдаем ошибку
                error = f'Ошибка типов входных данных {new_data.dtypes.values}. ' +\
                    f'Ожидаются типы: {model_vars_dict["data_types"][self.columns_init].values}'
                return error

        # если это временной ряд
        if model_vars_dict['flag_ts']:
                
             # если это не авторегрессия
            if not model_vars_dict.get('steps_auto_regr', None):
                    
                # проверяем высоту данных, если больше 1 наблюдения,
                # то для данного случая выдаем ошибку
                if len(new_data) > 1:
                    error = 'Ошибка. Для временного ряда ожидается одно наблюдение.'
                    return error

                # если высоты датасета больше, чем vars_dict['max_diff_step'],
                # то не добавляем строку, а записываем в последнюю, так как при создании признака-лага
                # в df_log добавляется строка, в которую должен быть записан прогноз
                if len(self.df_log) > model_vars_dict['max_diff_step']:
                    accumulate = False
                    
                # дублируем значения из столбцов init в столбцы fact для таргетов и признаков
                new_data[self.vars_dict['fact_targets_columns']] = new_data[model_vars_dict['init_targets_columns']]
                new_data[self.vars_dict['fact_features_columns']] = new_data[model_vars_dict['init_features_columns']]                

            # если авторегрессия 
            else:
                #?????? формируем пустой массив для создания df_tmp
                new_data = np.empty((model_vars_dict['steps_auto_regr'], len(self.columns)))
                # заполняем пустыми значениями
                new_data.fill(np.nan)
                #     # сначала записываем в столбец time_label смещение
                #     df_tmp['time_label'] = vars_dict['resample']
                #     # в первую ячейку time_label записываем последнюю дату/время из ряда + смещение
                #     df_tmp.loc[0, 'time_label'] = vars_dict['last_datetime_auto_regr'] + vars_dict['resample']
                #     # по всему столбцу time_label считаем сумму нарастающим итогом
                #     df_tmp['time_label'] = df_tmp['time_label'].cumsum()
                    
        # иначе (если это не временной ряд)
        else:
            # дублируем значения из столбцов init в столбцы fact для признаков
            new_data[self.vars_dict['fact_features_columns']] = new_data[model_vars_dict['init_features_columns']]
            try:
                new_data[self.vars_dict['fact_targets_columns']] = new_data[model_vars_dict['init_targets_columns']]
                new_data = new_data.drop(model_vars_dict['init_targets_columns'], axis=1)
            except KeyError: pass
        
        # сохраняем высоту входных данных
        self.vars_dict['data_height'] = len(new_data)
            
        # добавляем данные в df_log
        
        # если флаг набора данных == True
        # или флаг набора данных == False и не установлен флаг добавления новой строки на предыдущем шаге
        if accumulate or (not accumulate and not self.new_rows_after_preprocess):
            
            try:
                new_data_targets = new_data.dropna()[self.vars_dict['fact_targets_columns']]
            except KeyError:
                new_data_targets = pd.DataFrame()

            # устанавливаем индекс
            new_data.set_index(pd.DatetimeIndex([now_] * self.vars_dict['data_height']), inplace=True)
            # новые данные добавлеям к датасету логирования
            self.df_log = pd.concat([self.df_log, new_data.iloc[-(self.vars_dict['data_height'] - len(new_data_targets)):]])

            # Лишняя операция при временых рядах, но она происходит только на этапе накопления данных
            try:
                self.df_log.iloc[-self.vars_dict['data_height']:][self.vars_dict['fact_targets_columns']] = new_data[self.vars_dict['fact_targets_columns']].values
            except KeyError: pass
            
        # иначе
        else:
            # если стоит флаг добавления новой строки
            # то есть считаем, что в предыдущем шаге добавляли новую строку с признаками-лагами
            # Внимание! Речь идет об одной строке!
            if self.new_rows_after_preprocess:
                # индекс последней строки в df_log меняем на now_,
                # так как при создании признаков-лагов был установлен индекс = индекс последней строки + vars_dict['resample']
                self.df_log.index = self.df_log.index[:-1].append(pd.DatetimeIndex([now_]))
                # записываем в последнюю строку новые данные
                self.df_log.loc[now_, self.columns + self.columns_init] = new_data[self.columns + self.columns_init].values[0]
                # сбрасываем флаг добавления новой строки
                self.new_rows_after_preprocess = False

        return error

    def init_check_limits(self):
        """ Инициализация объекта Limits в словаре проверок check """
        self.check['limits'] = Limits()
        return self.check['limits']

