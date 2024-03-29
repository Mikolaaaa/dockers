import numpy as np
from MainModel import MainModel
from WrongPredsArrShape import WrongPredsArrShape
from set_labels import set_labels

def classifier_predict(
    values: np.ndarray,
    model: MainModel
) -> np.ndarray:
    """
    Прогнозирует с помощью модели классификации,
    поддерживает классификацию binary, multiclass, multilabel (из 0 и 1)
    
    :code_assign: service
    :code_type: Машинное обучение
    :imports: MainModel, set_labels, WrongPredsArrShape
        
    Параметры:
    values: np.ndarray
        Признаки для прогноза
    model: MainModel
        Модель
    """

    # получаем вероятности отнесения к классам
    probabilities = model.model.predict_proba(values)
    
    # если это бинарная классификация
    if model.vars_dict['class_type'] == 'binary':
        
        # если нужно вернуть вероятности
        if model.vars_dict['p_return']:
            # получаем вероятности отнесения к классу 1    
            predictions = probabilities[:, 1]
        # если нужно вернуть метки
        else:
            # получаем метки классов
            labels = probabilities[:, 1] > model.vars_dict['threshold']
            predictions = labels.astype('int')
    
    # если multiclass
    elif model.vars_dict['class_type'] == 'multiclass':
        # если вероятности отнесения к классам - одномерный массив
        if probabilities.ndim == 1:
            # выдаем ошибку
            raise WrongPredsArrShape(probabilities.shape, 'multiclass')
        if model.vars_dict.get('p_return', None):
            predictions = probabilities
        else:
            predictions = probabilities.argmax(axis=1)
    
    # если multilabel
    elif model.vars_dict['class_type'] == 'multilabel':
        if model.vars_dict.get('p_return', None):
            predictions = probabilities
        else:
            predictions = np.array([*map(set_labels, probabilities)])
    
    # возвращаем предсказания
    return predictions

