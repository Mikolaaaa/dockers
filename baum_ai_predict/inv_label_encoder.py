from sklearn.preprocessing import LabelEncoder
import numpy as np

def inv_label_encoder(arr: np.array, label_encoder: LabelEncoder, **kwargs):
    """
    проводит обратное преобразование label_encoder
    
    :code_assign: service
    :code_type: Анализ данных/Препроцессинг
    
    :packages:
    from sklearn.preprocessing import LabelEncoder
    
    параметры: массив, encoder
    """

    # инициализируем текст ошибки
    error = None

    # обратное трансформирование
    try:
        inv_arr_transformed = label_encoder.inverse_transform(arr.ravel())
    # ошибка - передаем во фронт
    except Exception as err:
        error = f'Ошибка обратного преобразования label_encoder: {repr(err)}'
        return None, error    
    
    # возвращаем итоговый массив и ошибку
    return inv_arr_transformed.reshape(-1, 1), error

