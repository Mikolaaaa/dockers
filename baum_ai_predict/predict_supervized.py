from DataLogs import DataLogs
import pandas as pd
from MainModel import MainModel
from inverse_transformation import inverse_transformation

def predict_supervised(
        model: MainModel,
        data_logs: DataLogs
) -> (DataLogs, None, str):
    """
    Делает прогноз с помощью модели, обученной с учителем, и записывает значения в датасет логирования

    :code_assign: service
    :code_type: Машинное обучение
    :imports: MainModel, DataLogs, inverse_transformation, classifier_predict, keras_reshape

    Параметры:
    model: MainModel
        Модель
    data_logs: DataLogs
        Датасет логирования
    """

    # инициализируем ошибку
    error = None

    # если временной ряд и не авторегрессия
    if model.vars_dict['flag_ts'] and not model.vars_dict.get('steps_auto_regr', None):

        # если создавали признаки-лаги для ряда, сохраняем величину лагов
        try:
            # сохраняем n_lags из списка преобразований
            nlags = model.vars_dict['features_methods'][model.vars_dict['ind_features_ts']]['args_meth']['nlags']
        # если ошибка, то nlags = 0
        except:
            nlags = 0

        # если высоты датасета недостаточно для дифференцирования и создания лагов
        if len(data_logs.df_log) <= (model.vars_dict['max_diff_step'] + nlags):
            # накапливаем данные и выходим без прогноза
            return data_logs, None, error

    # прогнозируем
    try:
        predictions = model.vars_dict['predict_fun'](
            values=data_logs.df_log.iloc[-data_logs.vars_dict['data_height']:][
                model.vars_dict['features_columns']].values,
            model=model)

    except Exception as err:
        error = 'Ошибка predict: {:s}'.format(repr(err))
        return data_logs, None, error

    # проводим обратные трансформации над прогнозом
    predictions, error = inverse_transformation(
        predictions,
        model.vars_dict['targets_methods'],
        data_logs.df_log.iloc[-model.vars_dict['max_diff_step'] - data_logs.vars_dict['data_height']:],
        data_logs.df_log.iloc[-data_logs.vars_dict['data_height']:].index)

    # если были ошибки при обратном преобразовании
    if error:
        return data_logs, None, error

    # Записываем прогноз в датасет логирования
    # Прогноз приводим к float, так как int от numpy не записывается, если в столбце есть NaN
    try:
        data_logs.df_log.update(
            pd.DataFrame(
                data=predictions.astype('float'),
                columns=data_logs.vars_dict['predictions_columns'],
                index=data_logs.df_log.iloc[-data_logs.vars_dict['data_height']:].index
            )
        )
    except:
        data_logs.df_log.iloc[-data_logs.vars_dict['data_height']:][
            data_logs.vars_dict['predictions_columns']] = predictions

    #
    if model.vars_dict['init_features_columns'] == ['text']:
        data_logs.df_log[data_logs.vars_dict['predictions_columns']] = predictions.astype('float')

    # возвращаем датасет логирования, None, ошибку
    return data_logs, None, error