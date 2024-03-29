import numpy as np
from sklearn.preprocessing import StandardScaler


def inv_standard_scaler(arr: np.array, scaler: StandardScaler, **kwargs):
    """
    проводит обратное преобразование standard_scale
    
    :code_assign: service
    :code_type: Анализ данных/Препроцессинг

    :packages:
    from sklearn.preprocessing import StandardScaler
    
    параметры: многомерный массив, трансформер
    """

    # инициализируем текст ошибки
    error = None

    # обратное трансформирование
    try:
        inv_arr_transformed = scaler.inverse_transform(arr)
    # ошибка - передаем во фронт
    except Exception as err:
        error = 'Ошибка обратного преобразования inv_standard_scaler: {:s}'.format(repr(err))
        return None, error    
    
    # возвращаем массив и ошибку
    return inv_arr_transformed, error

