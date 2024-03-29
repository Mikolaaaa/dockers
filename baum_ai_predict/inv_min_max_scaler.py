from sklearn.preprocessing import MinMaxScaler
import numpy as np

def inv_min_max_scaler(
    arr: np.ndarray,
    scaler: MinMaxScaler,
    **kwargs
):
    """
    Проводит обратное преобразование MinMaxScaler
    
    :code_assign: service
    :code_type: Анализ данных/Препроцессинг

    :packages:
    from sklearn.preprocessing import MinMaxScaler
    
    Параметры:
    arr: np.ndarray
        2D массив
    scaler: MinMaxScaler
        Трансформер
    """

    # Инициализируем текст ошибки
    error = None

    # Обратное трансформирование
    try:
        inv_arr_transformed = scaler.inverse_transform(arr)
    # Ошибка - передаем во фронт
    except Exception as err:
        error = 'Ошибка обратного преобразования inv_min_max_scaler: {:s}'.format(repr(err))
        return None, error    
    
    # Возвращаем массив и ошибку
    return inv_arr_transformed, error

