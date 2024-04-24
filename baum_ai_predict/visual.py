from DataLogs import DataLogs
import pandas as pd
from lineplot import LinePlot
from Scatter2DPlot import Scatter2DPlot
from window import Window
from canvas import Canvas
from init_gui_dict import init_gui_dict


def vis_overload_realtime(
        data_logs: DataLogs,
        prediction_logs: DataLogs,
        df_levels: pd.DataFrame
):
    """
    Визуализация прогнозов превышения заданного значения в реальном времени

    :code_assign: users
    :code_type: Пользовательские функции

    :imports: init_gui_dict, DataLogs, Window, Canvas, LinePlot, Scatter2DPlot
    :packages:
    import pandas as pd

    :param_block DataLogs data_logs DFLog: датасет логирования с временным рядом
    :param_block DataLogs prediction_logs DFLog: датасет логирования с прогнозами
    :param_block pd.DataFrame df_levels: датасет, содержащий уровни

    :returns: gui_dict, error
    :rtype: dict, str
    :semrtype: ,
    """
    # инициализируем текст ошибки
    error = None
    gui_dict = init_gui_dict()

    colors = iter(['blue', 'red', 'green'])

    colors_dict = {}

    if data_logs.df_log.shape[0] == 1:
        return gui_dict, error
    grouped = data_logs.df_log.groupby('object')

    plots = []
    load_values_x = {}
    load_values_y = {}

    full_x = pd.Series()
    for name, group in grouped:
        group = group.sort_values(by=['time'])
        load_value_x = pd.to_datetime(group['time'])
        full_x = pd.concat([full_x, load_value_x])
        load_values_x[name] = load_value_x

        colors_dict[name] = next(colors)
        # ось значений нагрузки
        load_value_y = group['Capacity usage(%)']
        load_values_y[name] = load_value_y
        # создание экземпляра графика
        load_value_trace = LinePlot(
            x=load_value_x,
            y=load_value_y,
            names=[f'Нагрузка {name}'],
            marker=[dict(color=colors_dict[name])]
        )

        plots.append(load_value_trace)

    if prediction_logs:
        df = prediction_logs.df_log

        dots_predictions = df['object']
        dots_predictions_x = df['time']
        dots_predictions_y = df['Capacity usage(%)']

        grouped = df.groupby('object')

        plots_levels = []
        plots_predictions = []
        for name, group in grouped:
            predictions_x = pd.to_datetime(group['time'])
            full_x = pd.concat([full_x, predictions_x])

            predictions_y = group['Capacity usage(%)']

            predict_trace = Scatter2DPlot(
                x=predictions_x,
                y=predictions_y,
                names=[f'Прогнозирование уровня загруженности {name}'],
                marker=[dict(color=colors_dict[name])]
            )

            group = group[group['is_cloud'] == False]
            predictions_x = pd.to_datetime(group['time'])
            predictions_y = group['Capacity usage(%)']

            extrapolation_trace = LinePlot(
                x=pd.concat([
                    load_values_x[name].tail(1),
                    predictions_x
                ]).values,
                y=pd.concat([
                    load_values_y[name].tail(1),
                    predictions_y
                ]).values,
                line=[{'dash': 'dot'}],
                names=[f'Прогноз динамики заполнения {name}'],
                marker=[dict(color=colors_dict[name], size=1, sizemin=1)]
            )
            plots_predictions.append(extrapolation_trace)
            plots_levels.append(predict_trace)

    if isinstance(df_levels, pd.DataFrame) and not df_levels.empty:

        min_date = min(full_x)
        max_date = max(full_x)

        level_x = pd.Series([min_date, max_date])

        lvl_plots = []
        lvl_plots.append(
            LinePlot(
                x=level_x,
                y=pd.Series([100, 100]),
                names=[f'Максимальная загрузка'],
                line=[{'dash': 'dot'}],
                marker=[dict(color="black")]
            )
        )
        for idx, value in df_levels.iterrows():
            name = value['object']
            try:
                l0 = value['LEVEL0']
                level0 = LinePlot(
                    x=level_x,
                    y=pd.Series([l0, l0]),
                    names=[f'{name}: уровень 0'],
                    line=[{'dash': 'dot'}],
                    marker=[dict(color="black")]
                )
                lvl_plots.extend([level0])

            except:
                pass
            l1 = value['LEVEL1']
            l2 = value['LEVEL2']

            level1 = LinePlot(
                x=level_x,
                y=pd.Series([l1, l1]),
                names=[f'{name}: уровень 1'],
                line=[{'dash': 'dot'}],
                marker=[dict(color="black")]
            )

            level2 = LinePlot(
                x=level_x,
                y=pd.Series([l2, l2]),
                names=[f'{name}: уровень 2'],
                line=[{'dash': 'dot'}],
                marker=[dict(color="black")]
            )

            lvl_plots.extend([level1, level2])

    final_plots = plots + plots_levels + plots_predictions + lvl_plots

    """
    # Отрисовка прогнозов (точки)
    # ось времени
    predictions_x = pd.to_datetime(prediction_logs.df_log.predicted_timestamp, unit='s')
    # ось значений нагрузки
    predictions_y = pd.Series(np.ones(predictions_x.shape[0]))
    # создание экземпляра графика
    predictions_trace = LinePlot(
        x=predictions_x,
        y=predictions_y.values,
        mode='markers',
        names=['Прогнозы'],
    )

    # Отрисовка экстраполяции нагрузки (пунктир)
    extrapolation_trace = LinePlot(
        x=pd.concat([
            load_value_x.tail(1),
            predictions_x.tail(1)
        ]).values,
        y=pd.concat([
            load_value_y.tail(1),
            predictions_y.tail(1)
        ]).values,
        line=[{'dash': 'dot'}],
        names=['Прогноз динамики заполнения']
    )
"""
    # plots = [load_value_trace]#, predictions_trace, extrapolation_trace]

    xaxis = {'xaxis': {'title': 'Дата'}}
    yaxis = {'yaxis': {'title': 'Процент загрузки'}}

    gui_dict['plot'].append(
        Window(
            window_title='Прогноз динамики загрузки',
            realtime=True,
            canvases=[Canvas(
                title='Прогноз динамики загрузки',
                xaxis=xaxis,
                yaxis=yaxis,
                showlegend=True,
                plots=final_plots
            )]
        ).to_dict()
    )

    # raise Exception(f"{dots_predictions}\n{dots_predictions.values}")
    gui_dict['table'].append({
        'title': 'Достижение уровней загруженности',
        'value':
            {
                'Объект': dots_predictions.to_list(),
                'Уровень загруженности': [int(el) for el in dots_predictions_y.to_list()],
                'Дата': dots_predictions_x.to_list()
            }
    })

    return gui_dict, error