import numpy as np
import pandas as pd
from inv_power_transform import inv_power_transform
from inv_standard_scaler import inv_standard_scaler
from inv_min_max_scaler import inv_min_max_scaler
from inv_differentiation import inv_differentiation
from inv_ohe import inv_ohe
from inv_label_encoder import inv_label_encoder
from inv_vectorizer import inv_vectorizer

def inverse_transformation(
        arr_for_transform: np.array,
        list_method: list,
        ts: pd.DataFrame = None,
        diff_indexes: pd.DatetimeIndex = None
):
    """
    проводит обратное преобразование по переданному списку
    примененных трансформаций list_method

    :code_assign: service
    :code_type: Анализ данных/Препроцессинг
    :imports: inv_power_transform, inv_standard_scaler, inv_min_max_scaler, inv_differentiation, inv_ohe, inv_label_encoder, inv_vectorizer

    параметры: многомерный массив для обратной трансформации,
               список примененных трансформций,
               датасет (временной ряд) для обратного дифференцирования,
               индексы (datetimeindex) для обратного дифференцирования
    """

    # инициализируем ошибку
    error = None

    # если ts_for_transform - одномерный массив размера (_,)
    if len(arr_for_transform.shape) == 1:
        # преобразуем в массив размера (_,_)
        arr_for_transform = arr_for_transform.reshape(-1, 1)

    # создаем словарь функций обратного преобразования
    # с функцией-объектом и параметрами для передачи в функцию
    funs = {
        'power_transform': {'fun': inv_power_transform, 'args': {}},
        'standard_scaler': {'fun': inv_standard_scaler, 'args': {}},
        'min_max_scaler': {'fun': inv_min_max_scaler, 'args': {}},
        'differentiation': {'fun': inv_differentiation, 'args': {'ts': ts, 'diff_indexes': diff_indexes}},
        'ohe': {'fun': inv_ohe, 'args': {}},
        'label_encoder': {'fun': inv_label_encoder, 'args': {}},
        'vectorizer': {'fun': inv_vectorizer, 'args': {}},
    }

    # мелко копируем list_method, так как далее идет reverse
    lm = list_method.copy()

    # реверсируем список трансформаций, чтобы начать с последнего преобразования
    lm.reverse()

    # идем по списку трансформаций и делаем преобразование
    for meth in lm:

        # meth - это словарь из списка примененных трансформаций
        # meth['meth'] - название метода = ключ в словаре funs, например, 'power_transform',
        # funs[meth['meth']]['fun'] - функция для преобразования, например, inv_power_transform
        # funs[meth['meth']]['args'] - аргументы для передачи в функцию
        # meth['args_meth'] - аргументы метода из list_method

        # проводим преобразование
        # передаем аргументы метода из list_method и аргуметны для функции из словаря funs
        arr_for_transform, error = funs[meth['meth']]['fun'](arr_for_transform,
                                                             **meth['args_meth'], **funs[meth['meth']]['args'])

        # если при обратной трансформации возникла ошибка,
        if error:
            return None, error

    # возвращаем трансформированный массив и ошибку
    return arr_for_transform, error

