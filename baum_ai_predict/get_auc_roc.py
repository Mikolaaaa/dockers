import numpy as np
from sklearn.metrics import roc_auc_score


def get_auc_roc(targets, predictions_prob, average: str=None, multi_class: str='raise'):
    """
    возвращает auc_roc
    
    :code_assign: service
    :code_type: Машинное обучение/Метрики
    
    :packages:
    from sklearn.metrics import roc_auc_score

    параметры: целевые значения, прогнозные значения - вероятности (если бинарная, то вероятность класса 1),
               способ расчета метрики, признак multi_class
    """
    
    # считаем auc_roc
    metric = np.round(roc_auc_score(targets, predictions_prob, average=average, multi_class=multi_class), 3)
    
    # если average == None
    if not average:
        # если 1 label
        if targets.shape[1] == 1: return [metric]
    
    return metric

