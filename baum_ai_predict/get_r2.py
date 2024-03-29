import numpy as np
from sklearn.metrics import r2_score


def get_r2(targets: np.array, predictions: np.array, multioutput: str='raw_values'):
    """
    Возвращает r2 (коэффициент детерминации)
    
    :code_assign: service
    :code_type: Машинное обучение/Метрики
    
    :packages:
    from sklearn.metrics import r2_score
    
    параметры: целевые значения, прогнозные значения,
               флаг вывода метрики для каждого признака в виде массива или одним значением:
               raw_values - массивом, uniform_average - одним значением
    """
    
    return np.round(r2_score(targets, predictions,
                                       multioutput=multioutput), 3)

