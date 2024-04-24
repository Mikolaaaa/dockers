from typing import Union
from DataLogs import DataLogs
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from datetime import timedelta, datetime
from scipy.signal import find_peaks
from train_regression import train_regression

import pandas as pd


def prediction_linear_regression_shd(
        df: pd.DataFrame,
        df_levels: Union[pd.DataFrame, DataLogs],
        vars_dict: dict,
        sp_flag: bool,
        select_window_type: str,
        dropdown_block:dict,
        levels_list: Union[str, list] = None,
        use_cloud: bool = False,
        # metric_name: Union[str, None] = None,
        # cv: Union[int, None] = None
):
    """
    Прогноз для линейной регрессии СХД

    :code_assign: users
    :code_type: Машинное обучение/Регрессия
    :imports: train_regression, DataLogs

    :packages:
    import pandas as pd
    import numpy as np
    from sklearn.linear_model import LinearRegression
    from datetime import timedelta, datetime
    from scipy.signal import find_peaks

    :param_block pd.DataFrame df Union[DataSet, TimeSeries, DataLogs]: датасет или временной ряд или Даталог
    :param_block pd.DataFrame df_levels: датасет содержащий уровни
    :param_block dict vars_dict Logs: словарь переменных

    :param bool sp_flag: использовать sp для прогноза
    :param str select_window_type: тип выбора интервала окна
    :param dict dropdown_block: dropdown_block
    :param list levels_list: список выбранных уровней
    :param bool use_cloud: использовать облако точек

    :returns: fitted_model, result_df, error
    :rtype: type, pd.DataFrame, str
    :semrtype: Model, Dataset,
    """

    error = ''
    result = {'time': [], 'object': [], 'Capacity usage(%)': [], 'is_cloud': False}
    levels_list = [l for l in levels_list if l in df_levels.columns]

    result_df = pd.DataFrame(result)
    if not isinstance(df, pd.DataFrame):
        df = df.df_log
    array_number = df.iloc[0]['array_num']

    object_levels = {
        'System': df_levels[df_levels['object'] == array_number],
        'StoragePool001': df_levels[df_levels['object'] == array_number + ' SP1'],
        'StoragePool002': df_levels[df_levels['object'] == array_number + ' SP2']
    }

    all_predictions = {
        'time': [],
        'StoragePool001': [],
        'StoragePool002': [],
    }
    all_predictions_for_main = {}
    if df.shape[0] == 1:
        return None, df, error


    extra = []
    for name, group in df.groupby('object'):
        extra.append(name)
        group['time'] = pd.to_datetime(group['time'])

        # Выбор интервала (ручной/автоматический)
        if select_window_type == 'advanced_interval':
            interval, interval_num = dropdown_block['interval'], dropdown_block['interval_num']
            offsets = {
                'День': pd.tseries.offsets.DateOffset(days=int(interval_num)),
                'Неделя': pd.tseries.offsets.DateOffset(weeks=int(interval_num)),
                'Месяц': pd.tseries.offsets.DateOffset(months=int(interval_num)),
                'Год': pd.tseries.offsets.DateOffset(years=int(interval_num))
            }
            last_date = group['time'].max()
            start_date = last_date - offsets[interval]
            date_from = start_date
            group = group[(group['time'] >= start_date) & (group['time'] <= last_date)]
        else:
            find_global = dropdown_block['find_global']
            if find_global:
                prominence = 2
            else:
                prominence = None
            last_date = group['time'].max()
            peaks_filtered, _ = find_peaks(group['Capacity usage(%)'], prominence=prominence)
            corresponding_index = group.iloc[peaks_filtered].index
            troughs_filtered, _ = find_peaks(-group['Capacity usage(%)'], prominence=prominence)
            if len(troughs_filtered) != 0:
                last_trough_time = group['time'].iloc[troughs_filtered[-1]]
            else:
                troughs_filtered = np.array([0])
                last_trough_time = group['time'].iloc[troughs_filtered[-1]]

            group = group[group['time'] >= last_trough_time]

            if len(peaks_filtered) != 0 and peaks_filtered[-1] > troughs_filtered[-1]:
                try:
                    last_peak_time = group['time'].loc[peaks_filtered[-1]]
                    group = group[group['time'] <= last_peak_time]
                except:
                    last_peak_time = group['time'].loc[corresponding_index[-1]]
                    group = group[group['time'] <= last_peak_time]

        group_length = len(group)

        # Формируем датасеты для прогнозов (в случае облака точек - их несколько)
        group_datasets = []
        if use_cloud is False:
            group_datasets.append(group)
        else:
            for i in range(group_length // 2, group_length + 1):
                new_df = group.head(i)
                group_datasets.append(new_df)
        extra.append(len(group_datasets))

        # цикл для облака точек по датафреймам
        for dataset in group_datasets:
            if len(dataset) == group_length:
                this_is_cloud = False
            else:
                this_is_cloud = True
            transformed_group = dataset.copy()
            transformed_group['time'] = transformed_group['time'].apply(lambda x: x.timestamp())
            fitted_model, df1, gui_dict, vars_dict1, error = train_regression(LinearRegression, transformed_group, vars_dict)

            # Считаем до уровней
            # Коэффициент наклона прямой
            k_coef = abs(fitted_model.coef_[0])
            # Параметр сдвига прямой
            bias = fitted_model.intercept_
            if k_coef == 0.0:
                continue
            prediction_dates = []
            predictions = []
            for lvl in levels_list:
                fill_level = object_levels[name].iloc[0][lvl]
                prediction_scaled = (fill_level - bias) / k_coef
                prediction_timestamp = abs(round(prediction_scaled))
                prediction_dates.append(datetime.fromtimestamp(prediction_timestamp).strftime('%Y-%m-%d %H:%M:%S.%f'))
                predictions.append(fill_level)

            fill_level = 100
            prediction_scaled = (fill_level - bias) / k_coef
            prediction_timestamp = abs(round(prediction_scaled))
            prediction_dates.append(datetime.fromtimestamp(prediction_timestamp).strftime('%Y-%m-%d %H:%M:%S.%f'))
            predictions.append(fill_level)

            days_difference = (pd.to_datetime(prediction_dates[-1]) - last_date).days

            prediction_dates_all = [last_date + timedelta(days=i) for i in range(1, days_difference+1)]
            future_dates_as_features_all = np.array([[date.timestamp()] for date in prediction_dates_all])
            predictions_all = fitted_model.predict(future_dates_as_features_all)


            all_predictions[name] = predictions_all
            if len(all_predictions['time']) < len(prediction_dates_all):
                all_predictions['time'] = prediction_dates_all
            if this_is_cloud is False:
                all_predictions_for_main = all_predictions
            interim_result = pd.DataFrame({'time': prediction_dates,
                                           'object': name,
                                           'Capacity usage(%)': predictions,
                                           'is_cloud': this_is_cloud})
            result_df = pd.concat([result_df, interim_result], ignore_index=True)


    # if sp_flag and len(all_predictions['StoragePool001']) != 0 and len(all_predictions['StoragePool002']) != 0:
    #
    #     no_cloud_results = result_df[(result_df['is_cloud'] == False) & (result_df['Capacity usage(%)'] == 100)]
    #
    #     min_time_sp1_sp2 = no_cloud_results[(no_cloud_results['object'] == 'StoragePool001') | (no_cloud_results['object'] == 'StoragePool002')]['time'].min()
    #     result_df = result_df[~((result_df['object'] == 'System') & (result_df['time'] > min_time_sp1_sp2))]
    #
    #     new_system_row = pd.DataFrame({'time': [min_time_sp1_sp2],
    #                                    'object': ['System'],
    #                                    'Capacity usage(%)': [100.0]})
    #
    #     result_df = pd.concat([result_df, new_system_row], ignore_index=True)
    def pad_dict_list(dict_list, padel):

        sp_s = ['StoragePool001', 'StoragePool002', 'time']
        result_dict_list = {
            'time': [],
            sp_s[0]: [],
            sp_s[1]: []
        }
        if len(dict_list[sp_s[0]]) < len(dict_list[sp_s[1]]):
            lmin = len(dict_list[sp_s[0]]) - 1
            lmax = len(dict_list[sp_s[1]]) - 1
            lminname = sp_s[0]
        else:
            lmin = len(dict_list[sp_s[1]]) - 1
            lmax = len(dict_list[sp_s[0]]) - 1
            lminname = sp_s[1]
        for n in sp_s:
            result_dict_list[n].append(dict_list[n][lmin])
            if n != 'time':
                result_dict_list[n].append(100)
            else:
                result_dict_list[n].append(dict_list[n][lmax])

        return result_dict_list


    if sp_flag and len(all_predictions['StoragePool001']) != 0 and len(all_predictions['StoragePool002']) != 0 :
        all_predictions = pad_dict_list(all_predictions_for_main, 100)

        result_df = pd.DataFrame.from_dict(all_predictions)

        result_df['time'] = pd.to_datetime(result_df['time']).dt.date

        result_df['System'] = (( result_df['StoragePool001'] + result_df['StoragePool002']).div(2)).astype(float)

        result_df['time'] = result_df['time'].apply(lambda x: x.strftime('%Y-%m-%d'))

        result_df = result_df.melt(id_vars=['time'], var_name='object', value_name='Capacity usage(%)')


        system_100_index = result_df[(result_df['object'] == 'System') & (result_df['Capacity usage(%)'] == 100)].index
        filtered_df = result_df[(result_df['object'] == 'System') & (result_df['Capacity usage(%)'] != 100)]
        last_index = filtered_df.sort_values(by='Capacity usage(%)')['Capacity usage(%)'].index[-1]
        result_df.loc[system_100_index, 'time'] = result_df.loc[last_index, 'time']

        result_df['is_cloud'] = False

    return fitted_model, result_df, error
