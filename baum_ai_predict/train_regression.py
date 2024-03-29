import pandas as pd
from typing import Union
from train_supervised import train_supervised

def train_regression(
        model: type,
        df: pd.DataFrame,
        vars_dict: dict,
        pars_model: dict = {},
        pars_opt: dict = {},
        pars_fit: dict = {},
        grid_search: bool = False,
        metric_name: Union[str, None] = None,
        cv: Union[int, None] = None
):
    """
    Запускает алгоритм регрессии

    :code_assign: service
    :code_type: Машинное обучение
    :imports: train_supervised

    Параметры:
    model: type
        Модель
    df: pd.DataFrame
        Датасет (обучающая выборка)
    vars_dict: dict
        Cловарь переменных
    pars_model: dict
        Параметры модели
    pars_opt: dict
        Параметры для тюнинга модели
    pars_fit: dict
        Параметры обучения
    grid_search: bool
        Флаг поиска лучших гиперпараметров
    metric_name: str
        Название метрики
    cv: int
        Kоличество фолдов
    """

    # обучение
    model, df, gui_dict, vars_dict, error = train_supervised(model, df, vars_dict,
                                                             pars_model=pars_model, pars_opt=pars_opt,
                                                             pars_fit=pars_fit,
                                                             grid_search=grid_search,
                                                             metric_name=metric_name, cv=cv)
    # ошибка - выходим
    if error: return None, df, None, vars_dict, error

    # функция для прогноза
    vars_dict['predict_fun'] = lambda values, model: model.model.predict(values)

    # возвращаем модель, датасет, словарь для гуи, словарь переменных, ошибка
    return model, df, gui_dict, vars_dict, error