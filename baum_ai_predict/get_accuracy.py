from sklearn.metrics import accuracy_score
import numpy as np

def get_accuracy(targets, predictions, multioutput: bool=True):
    """
    возвращает accuracy
    для binary и multiclass - доля правильных ответов
    для multilabel - доля наблюдений (samples) без ошибок по всем labels
    
    :code_assign: service
    :code_type: Машинное обучение/Метрики
    
    :packages:
    from sklearn.metrics import accuracy_score
    
    параметры: целевые значения, прогнозные значения,
               флаг вывода метрики в виде массива или одним значением:
               True - массивом, False - одним значением
    """
    
    # если нужно вывести массивом
    if multioutput:
        # возвращаем значением массивом
        return [np.round(accuracy_score(targets, predictions), 3)]
    
    return np.round(accuracy_score(targets, predictions), 3)

