import numpy as np
import pandas as pd

def inv_differentiation(ts_for_transform: np.array, last_values: np.array, origin_columns: list, diff_step: list,
                        ts: pd.DataFrame, diff_indexes: pd.DatetimeIndex, **kwargs):
    """
    проводит обратное дифференцирование при зачениях diff_step > 0
    если в переданном датасете есть оригинальные столбцы для сдвига, то используем их значения,
    иначе (то есть при авторегрессии) используем последние сохраненные значения в ряде,
    свои предыдущие значения и кумулятивную сумму
    
    
    :code_assign: service
    :code_type: Анализ данных/Препроцессинг
    
    параметры: многомерный массив для обратного дифференцирования (array)
               последние значения из ряда по высоте max(diff_step) (array)
               список названий оригинальных столбцов (list), 
               шаг дифференцирования для каждого признака (list)
               многомерный ряд (датасет),
               список индексов (datetimeindex)
    """
    
    # если есть оригинальная колонка в датасете для получения сдвига и обратного дифференцирования
    if set(origin_columns) & set(ts.columns) == set(origin_columns):
    
        # обратное дифференцирование, если для ряда diff_step > 0
        ts_transformed = [ts_for_transform[:,ind] + np.array(ts[orig_col].shift(diff_step[ind])[diff_indexes])
                          if diff_step[ind] > 0 else ts_for_transform[:,ind]
                          for ind, orig_col in enumerate(origin_columns)]
   
        # транспонируем массив
        ts_transformed = np.array(ts_transformed).T
    
    # если нет оригинальных столбцов, то есть имеем дело с авторегрессией, то для обратного диф-я
    # используем предыдущие значения и сумму нарастающим итогом
    else:
        
        # добавляем первыми строками последние значения из ряда
        tmp_arr = np.vstack((last_values, ts_for_transform))

        # создаем пустой массив для записи в него трансформированных значений
        ts_transformed = np.empty(ts_for_transform.shape)

        # идем по списку шагов дифференцирования для каждого целевого признака
        for ind in range(len(diff_step)):
            # если шаг дифференцирования больше 0, то есть нужно проводить обратное диф-е
            if diff_step[ind] > 0:

                # из последних значений ряда, которые находятся в начале массива tmp_arr,
                # оставляем только соответствующие diff_step
                tmp_arr_ind = tmp_arr[(last_values.shape[0] - diff_step[ind]):, ind]

                # создаем пустой итоговый массив по длине tmp_arr_ind
                arr_all_cumsums = np.empty(len(tmp_arr_ind))
                # заполняем его нулями
                arr_all_cumsums.fill(0)

                # итерируем diff_step и идем по циклу
                for step in range(diff_step[ind]):

                    # создаем массив с маской из 1
                    arr_mask = np.ones(len(tmp_arr_ind))
                    # создаем список из индексов массива с маской
                    slice_list = [*range(len(arr_mask))]
                    # нарезаем список индексов по шагу diff_step
                    slice_list = slice_list[step:len(arr_mask):diff_step[ind]]
                    # устаналиваем маску в этих индксах = 0
                    arr_mask[slice_list] = 0
                    # создаем MaskedArray с маской arr_mask
                    arr_masked = np.ma.MaskedArray(tmp_arr_ind, mask=arr_mask)
                    # считаем сумму нарастающим итогом, замаскированные значения заполняем нулем
                    arr_masked_cumsum = np.ma.filled(arr_masked.cumsum(0), 0)
                    # прибавляем значения к итоговому массиву
                    arr_all_cumsums += arr_masked_cumsum

                # в ts_transformed записываем значения из arr_all_cumsums
                ts_transformed[:,ind] = arr_all_cumsums[diff_step[ind]:]

            # иначе если diff_step == 0, оставляем значения как есть
            else: ts_transformed[:,ind] = ts_for_transform[:,ind]
        
    # возвращаем массив и пустой текст ошибки
    return ts_transformed, None

