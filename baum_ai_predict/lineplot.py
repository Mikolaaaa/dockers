from SimplePlot import SimplePlot
from typing import Union, List
import plotly.graph_objects as go
import numpy as np
import pandas as pd


class LinePlot(SimplePlot):
    """
    Линейный график

    :code_assign: service
    :code_type: Визуализация
    :imports: SimplePlot

    :packages:
    import plotly.graph_objects as go

    Параметры:
    x: координаты X (1D или 2D)
    y: координаты Y (1D или 2D)
    names: список названий графиков для легенды
    fill: способ заливки между графиками
    marker: свойства для marker
    line: свойства для line
    mode: линии / точки
    row: строка в subplots
    col: столбец в subplots
    showlegend: показвать легенду
    legendgroup: группа легенды
    """

    def __init__(
        self,
        x: Union[np.ndarray, pd.DatetimeIndex],
        y: np.ndarray,
        names: Union[List[str], None] = None,
        fill: Union[List[str], str, None] = None,
        marker: Union[List[Union[dict, None]], dict, None] = None,
        line: Union[List[Union[dict, None]], dict, None] = None,
        mode: Union[str, None] = 'lines',
        row: Union[int, None] = None,
        col: Union[int, None] = None,
        showlegend: Union[bool, None] = None,
        legendgroup: Union[str, None] = None
    ):

        super().__init__(
            x=x,
            y=y,
            names=names,
            row=row,
            col=col,
            showlegend=showlegend,
            legendgroup=legendgroup)
        
        self.fill = fill
        self.marker = marker
        self.line = line
        self.mode = mode
        
    def draw(self, fig: go.Figure):

        # получаем количество графиков
        k = self.amount_plots
        
        # идем по графикам
        for k in range(k):

            try:
                # если пытаемся обратиться к 1d массиву как 2d
                x = self.x[:, k]
            except:
                x = self.x
                
            try:
                # если пытаемся обратиться к 1d массиву как 2d
                y = self.y[:, k]
            except:
                y= self.y
            
            name = self.get_value(self.names, k)
            marker = self.get_value(self.marker, k)
            line = self.get_value(self.line, k)
            fill = self.get_value(self.fill, k)

            fig.add_trace(go.Scatter(
                x=x,
                y=y,
                mode=self.mode,
                name=name,
                fill=fill,
                marker=marker,
                line=line,
                showlegend=self.showlegend,
                legendgroup=self.legendgroup,
                visible=False), row=self.row, col=self.col)

        return fig

    @property
    def amount_plots(self):
        if self.y.ndim == 1: return 1        
        else: return self.y.shape[1]

