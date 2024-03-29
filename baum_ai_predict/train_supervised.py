from typing import Union
from init_gui_dict import init_gui_dict
from get_metric import get_metric
from sklearn.model_selection import TimeSeriesSplit, GridSearchCV
from sklearn.metrics import make_scorer
import numpy as np
from predict_supervized import predict_supervised
import pandas as pd


def train_supervised(
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
    Обучение с учителем с подбором гиперпараметров и без

    :code_assign: service
    :code_type: Машинное обучение
    :imports: init_gui_dict, get_metric, predict_supervised

    :packages:
    from sklearn.model_selection import TimeSeriesSplit, GridSearchCV
    from sklearn.metrics import make_scorer

    Параметры:
    model: type
        Модель
    df: pd.DataFrame
        Датасет (обучающая выборка)
    vars_dict: dict
        Словарь переменных
    pars_model: dict
        Параметры модели
    pars_opt: dict
        Параметры для тюнинга модели
    pars_fit: dict
        Параметры обучения
    grid_search: bool
        Флаг поиска лучших гиперпараметров
    metric_name: Union[str, None]
        Название метрики
    cv: Union[int, None]
        Количество фолдов
    """

    # инициализируем ошибку
    error = None

    # инициализируем словарь для гуи
    gui_dict = init_gui_dict()

    # матрица признаков
    train_X = df[vars_dict['features_columns']].values
    # матрица целевых признаков
    train_y = df[vars_dict['targets_columns']].values

    # если train_y - одномерный массив размера (_,1)
    if train_y.shape[1] == 1:
        # преобразуем в массив размера (_,)
        train_y = train_y.ravel()

    # если нужно подобрать гиперпараметры
    if grid_search:

        # инициализируем модель
        try:
            model = model(**pars_model)
        # ошибка
        except Exception as err:
            error = 'Ошибка инициализации модели {}: {:s}'.format(model, repr(err))
            return None, df, None, vars_dict, error

        # получаем инфо по расчету метрики (функция + аргументы для make_scorer и функции метрики)
        metric = get_metric(metric_name, vars_dict)

        # инициализируем make_scorer
        score = make_scorer(metric['fun'], **metric['args_make_scorer'], **metric['args_score'])

        # идем по гиперпараметрам, значения которых нужно подобрать
        for key, value in pars_opt.items():
            # если это tuple, добавялем к нему генератор
            if type(value) == tuple:
                pars_opt[key] = np.arange(*value)

        # если наш датасет - временной ряд
        if vars_dict['flag_ts']:
            # указываем, что при создании фолдов датасет не нужно перемешивать
            cv = TimeSeriesSplit(n_splits=cv)

        # запускаем GridSearchCV
        try:
            grid = GridSearchCV(model, pars_opt, scoring=score, cv=cv)
        # ошибка
        except Exception as err:
            error = 'Ошибка GridSearchCV: {:s}'.format(repr(err))
            return None, df, None, vars_dict, error
            # обучаем и подбираем гиперпараметры
        try:
            grid.fit(train_X, train_y, **pars_fit)
        # ошибка
        except Exception as err:
            error = 'Ошибка подбора гиперпараметров и обучения модели {}: {:s}'.format(model, repr(err))
            return None, df, None, vars_dict, error

        # сохраняем лучшую модель
        model = grid.best_estimator_

        # обнолвяем словарь для гуи
        # лучшие гиперпараметры
        gui_dict['text'].append({'title': 'Лучшие гиперпараметры при кросс-валидации:',
                                 'value': grid.best_params_})
        # лучшая метрика
        gui_dict['text'].append({'title': 'Лучшая метрика {} при кросс-валидации:'.format(metric_name),
                                 'value': abs(round(grid.best_score_, 3))})
        # время обучения
        gui_dict['text'].append({'title': 'Время обучения полной обучающей выборки в сек:',
                                 'value': round(grid.refit_time_, 3)})

        # если обучаем модель с указанными гиперпараметрами
    else:

        # инициализируем модель
        try:
            model = model(**pars_model, **pars_opt)
        # ошибка
        except Exception as err:
            error = 'Ошибка инициализации модели {}: {:s}'.format(model, repr(err))
            return None, df, None, vars_dict, error

        # обучаем
        try:
            model.fit(train_X, train_y, **pars_fit)
        # ошибка - передаем во фронт
        except Exception as err:
            error = 'Ошибка обучения модели {}: {:s}'.format(model, repr(err))
            return None, df, None, vars_dict, error

        # обновляем словарь переменных
        # главная функция для прогноза
    vars_dict['main_predict_fun'] = predict_supervised
    # модель
    gui_dict['text'].append({'title': 'Модель', 'value': str(model)})

    # возвращаем обученную модель, обучающий датасет, словарь для гуи, словарь переменных, ошибку
    return model, df, gui_dict, vars_dict, error