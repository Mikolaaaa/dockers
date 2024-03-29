import numpy as np
from sklearn.metrics import mean_squared_error


def get_rmse(targets: np.array, predictions: np.array, multioutput: str='raw_values'):
    """
    возвращает rmse
    
    :code_assign: service
    :code_type: Машинное обучение/Метрики
    
    :packages:
    from sklearn.metrics import mean_squared_error
    
    параметры: целевые значения, прогнозные значения,
               флаг вывода метрики для каждого признака в виде массива или одним значением:
               raw_values - массивом, uniform_average - одним значением
    """
    
    return np.round(mean_squared_error(targets, predictions,
                                       multioutput=multioutput) ** 0.5, 3)

