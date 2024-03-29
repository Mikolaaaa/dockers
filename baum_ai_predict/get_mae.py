import numpy as np
from sklearn.metrics import mean_absolute_error

def get_mae(targets: np.array, predictions: np.array, multioutput: str='raw_values'):
    """
    возвращает mae
    
    :code_assign: service
    :code_type: Машинное обучение/Метрики
    
    :packages:
    from sklearn.metrics import mean_absolute_error
    
    параметры: целевые значения, прогнозные значения,
               флаг вывода метрики для каждого признака в виде массива или одним значением:
               raw_values - массивом, uniform_average - одним значением
    """
    
    return np.round(mean_absolute_error(targets, predictions,
                                        multioutput=multioutput), 3)

