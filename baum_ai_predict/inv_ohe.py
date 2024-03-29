import numpy as np
from sklearn.preprocessing import OneHotEncoder

def inv_ohe(arr: np.array, one_hot_encoder: OneHotEncoder, cat_ind: list, others_ind: list, **kwargs):
    """
    проводит обратное преобразование ohe
    
    :code_assign: service
    :code_type: Анализ данных/Препроцессинг
    
    :packages:
    from sklearn.preprocessing import OneHotEncoder
    
    параметры: массив, encoder, индексы категор признаков, индексы остальных признаков
    """

    # инициализируем текст ошибки
    error = None

    # обратное трансформирование
    try:
        # в переданном массиве берем только столбцы, идущие после признаков,
        # которые не являются категориальными
        inv_arr_transformed = one_hot_encoder.inverse_transform(arr[:, len(others_ind):])
    # ошибка - передаем во фронт
    except Exception as err:
        error = 'Ошибка обратного преобразования inv_ohe: {:s}'.format(repr(err))
        return None, error    
    
    # формируем итоговый массив
    final_arr = np.empty((len(arr), len(others_ind) + len(cat_ind)), dtype='object')
    # по индексам others_ind записываем некатегор признкаки
    final_arr[:, others_ind] = arr[:, :len(others_ind)]
    # по индексам cat_ind записываем категор признкаки
    final_arr[:, cat_ind] = inv_arr_transformed
    
    # возвращаем итоговый массив и ошибку
    return final_arr, error
