import numpy as np


def get_wmape(targets, predictions, multioutput: bool=True):
    """
    возвращает wmape
    
    :code_assign: service
    :code_type: Машинное обучение/Метрики
    
    параметры: целевые значения, прогнозные значения,
               флаг вывода метрики для каждого признака в виде массива или одним значением:
               True - массивом, False - одним значением
    """
   
    # если нужно вывести метрику для каждого признака в виде массива метрик
    if multioutput:
        return np.round(sum(abs(targets - predictions)) / sum(abs(targets)), 3)
    # если одним значением (среднее значение метрики по всем признакам)
    else:
        return np.round(sum(abs(targets - predictions)) / sum(abs(targets)), 3).mean()

