import numpy as np

def keras_reshape(arr: np.array, diff_dimension: int):
    """
    изменение размерности тензора в соответствии с первым слоем
    
    :code_assign: service
    :code_type: Глубокое обучение
    
    параметры: массив (array), флаг изменения размерности (int)
    """
    
    if diff_dimension == 1:
        # увеличиваем размерность
        arr =  arr.reshape(*arr.shape, 1)
    elif diff_dimension == -1:
        # уменьшаем размерность (перемножаем последние 2 измерения)
        arr =  arr.reshape(*arr.shape[:-2], arr.shape[1] * arr.shape[2])
    
    return arr
