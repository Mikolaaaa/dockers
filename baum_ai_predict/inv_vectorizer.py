import numpy as np
import pandas as pd
from typing import Union
from gensim.models import KeyedVectors, Doc2Vec
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer


def inv_vectorizer(
        arr: np.array,
        vectorizer: Union[TfidfVectorizer, KeyedVectors, Doc2Vec, CountVectorizer],
        **kwargs
):
    """
    Функция для проведения обратной векторизации

    :code_assign: service
    :code_type: Анализ данных/Препроцессинг

    :packages:
    from typing import Union
    from gensim.models import KeyedVectors, Doc2Vec
    from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer

    arr: многомерный массив
    vectorizer: модель эмбэддинга
    """
    # инициализируем текст ошибки
    error = None

    # прямое преобразование
    try:
        if isinstance(vectorizer, (TfidfVectorizer, CountVectorizer)):
            if vectorizer.cls_mode:
                try:
                    inv_arr_transformed = pd.DataFrame(
                        " ".join(row)
                        for row in vectorizer.inverse_transform(arr.reshape(vectorizer.initial_shape[0], -1))
                    )
                except ValueError:
                    inv_arr_transformed = arr
            else:
                inv_arr_transformed = vectorizer.inverse_transform(arr.reshape(vectorizer.initial_shape[0], -1))
        else:
            inv_arr_transformed = np.array([' '.join(
                vectorizer.similar_by_vector(word_vector)[0][0]
                for word_vector in arr
            )])

    # ошибка - передаем во фронт
    except Exception as err:
        error = 'Ошибка обратного преобразования inv_vectorizer: {:s}'.format(repr(err))
        return None, error

    # возвращаем массив и ошибку
    return inv_arr_transformed, error

