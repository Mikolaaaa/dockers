from canvas import Canvas
from typing import Union, List
import plotly.graph_objects as go
import copy
from lineplot import LinePlot
import numpy as np


class Window():
    """
    Стандартное окно с полотнами
    Количество subplots в окне не может превышать 100.
    Если окно содержит subplots, то добавляем subplots в fig.
    !Важно! Полотно с subplots должно быть в отдельном окне,
    либо в данном окне должны быть полотна с одинкаковым количеством subplots.

    :code_assign: service
    :code_type: Визуализация
    
    :packages:
    import plotly.graph_objects as go
    import copy

    Параметры:
    window_title: str
        Заголовок для окна
    realtime: bool
        Флаг real time
    make_subplots: bool
        Флаг subplots
    rows: int
        Количество строк для subplots
    cols: int
        Количество столбцов для subplots
    specs: Union[List[List[Union[dict, None]]], None]
        Свойства для 3d axis
    row_titles: list
        Названия для строк в subplots
    column_titles: list
        Названия для столбцов в subplots
    subplot_titles: list
        Названия для subplots
    shared_xaxes: bool
        Делаиться xaxes в subplots
    shared_yaxes: bool
        Делаиться yaxes в subplots
    canvases: list
        Список полотен
    """

    def __init__(
        self,
        window_title: str = '',
        realtime: bool = False,
        make_subplots: bool = False,
        rows: int = 1,
        cols: int = 1,
        specs: Union[List[List[Union[dict, None]]], None] = None,
        row_titles: list = [],
        column_titles: list = [],
        subplot_titles: list = [],
        shared_xaxes: bool = False,
        shared_yaxes: bool = False,
        canvases: list = []
    ):

        self.window_title = window_title
        self.realtime = realtime

        # создаем figure plotly
        self.fig = go.Figure(layout=go.Layout(height=500, width=800, template='plotly_white'))

        # счетчик графиков в окне
        self.amount_plots = 0
        # счетчик фигур в окне
        self.amount_shapes = 0
        self.canvases = []

        # если установлен флаг создаем subplots
        if make_subplots:
            # если общее количество больше 100
            if rows * cols > 100:
                self.make_subplots = False
                # выводим пустой график с ошибкой
                canvases = [Canvas(
                    x_title='Количество графиков в одном окне не может превышать 100',
                    plots = [LinePlot(x=np.array([]), y=np.array([]))]
                )]              
            
            else:
                # создаем subplots
                self._make_subplots(
                    rows=rows,
                    cols=cols,
                    specs=specs,                  
                    row_titles=row_titles,
                    column_titles=column_titles,
                    subplot_titles=subplot_titles,
                    shared_yaxes=shared_yaxes,
                    shared_xaxes=shared_xaxes)
        else: self.make_subplots = False
            
        # если передан список полотен, добавляем его в окно
        if canvases: self._add_canvases(canvases)

    def _make_subplots(
        self,
        rows: int,
        cols: int,
        specs: Union[List[List[Union[dict, None]]], None] = None,
        row_titles: list = [],
        column_titles: list = [],
        subplot_titles: list = [],
        shared_xaxes = False,
        shared_yaxes = False
    ):

        self.make_subplots = True
        # создаем subplots
        self.fig.set_subplots(
                rows=rows,
                cols=cols,
                specs=specs,                  
                row_titles=row_titles,
                column_titles=column_titles,
                subplot_titles=subplot_titles,
                shared_yaxes=shared_yaxes,
                shared_xaxes=shared_xaxes)
        self.rows = rows
        self.cols = cols            

    def _add_canvases(
        self,
        canvases: list):
        
        """ Добавление полотна в окно """
        
        # идем по полотнам окна
        for canvas in canvases:
            self.fig = canvas._add_plots(canvas.plots, self.fig)
            self.fig = canvas._add_shapes(canvas.shapes, self.fig)

            # увеличиваем счетчик графиков на кол-во графиков на полотне
            self.amount_plots += canvas.amount_plots
            # увеличиваем счетчик фигур на кол-во фигур на полотне
            self.amount_shapes += canvas.amount_shapes
            # сохраняем число графиков и число фигур для данного полотна
            self.canvases.append([canvas.amount_plots, canvas.amount_shapes])
        
        # --- LAYOUT ---
        
        # если в окне есть фигуры
        if self.amount_shapes > 1:
            # собираем список фигур по всем полотнам
            all_shapes = [shape.to_dict() for canvas in canvases for shape in canvas.shapes]
        else: all_shapes = []
        
        # инициализируем список свойств для выпадающего меню
        dropdown_buttons = []
        
        # идем по полотнам в window
        for ind_canvas, canvas in enumerate(canvases):
            # массив видимости фигур
            visibility_shapes = np.zeros(self.amount_shapes).astype('bool')
            # устанавливаем visible = True для фигур данного полотна
            visibility_shapes[ind_canvas * canvas.amount_shapes : ind_canvas * canvas.amount_shapes + canvas.amount_shapes] = True

            # идем по фигурам окна
            for i in range(self.amount_shapes):
                # обновляем свойство visible у всех фигур в соответствии с visibility_shapes для данного полотна
                all_shapes[i]['visible'] = visibility_shapes[i]

            # если создавали subplots
            if self.make_subplots:
                # словарь с аргументами для dropdown_buttons
                args = {
                    #'title': canvas.title,
                    'showlegend': canvas.showlegend,
                    # shapes?
                }                         
            # иначе, если в окне нет subplots
            else:
                args = {
                    #'title': canvas.title,
                    **canvas.xaxis,
                    **canvas.yaxis,
                    'scene': canvas.scene,
                    'showlegend': canvas.showlegend,
                    'shapes': copy.deepcopy(all_shapes)
                }

            # массив видимости для всех графиков всех полотен
            visibility_array = np.zeros(self.amount_plots).astype('bool')
            # устанавливаем visible = True для графиков данного полотна
            visibility_array[ind_canvas * canvas.amount_plots : ind_canvas * canvas.amount_plots + canvas.amount_plots] = True

            # добавляем dropdown_buttons для полотна
            dropdown_buttons.append({
                'label': canvas.title,
                'method': "update",
                'args': [{'visible': visibility_array}, args]
            })

        # для начального отображения берем оформление для первого полотна окна
        self.fig.update_layout(
            #title_text=canvases[0].title,
            title_x = 0,
            **canvases[0].xaxis,
            **canvases[0].yaxis,
            scene = canvases[0].scene,
            showlegend=canvases[0].showlegend,
            updatemenus=[{
                'type': 'dropdown',
                'active': 0,
                'buttons': dropdown_buttons,
                'showactive': True,
                'x': 0.5,
                'xanchor': "center",
                'y': 1.2,
                'yanchor': "top",
            }]
        )

        # если не realtime
        if not self.realtime:
            # берем число графиков первого полотна
            len_plots = canvases[0].amount_plots
            # берем число фигур первого полотна
            len_shapes = canvases[0].amount_shapes
            
            #делаем видимыми графики первого полотна
            for i in range(len_plots):
                self.fig['data'][i].visible = True
            
            #делаем видимыми фигуры первого полотна
            for i in range(len_shapes):
                self.fig['layout']['shapes'][i].visible = True
        
    def fig_json(self):
        """ Сохраняет go.Figure в json"""
        return self.fig.to_json().encode().decode('unicode-escape')

    def to_dict(self):
        """ Сохраняет окно в словарь """
        window_dict = self.__dict__
        window_dict['fig'] = self.fig_json()
        return window_dict

