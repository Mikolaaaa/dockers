from SimplePlot import SimplePlot
import plotly.graph_objects as go
import numpy as np
from typing import Union, List

class Scatter2DPlot(SimplePlot):
    """
    Точечная диаграмма / Пузырьковая диаграмма 2D
    
    :code_assign: service
    :code_type: Визуализация
    :imports: SimplePlot

    :packages:
    import plotly.graph_objects as go
    
    Параметры:
    x: координаты X (1D или 2D)
    y: координаты Y (1D или 2D)
    names: список названий графиков для легенды
    marker: marker
    text: текст для точек
    row: строка в subplots
    col: столбец в subplots
    """

    def __init__(
        self,
        x: np.ndarray,
        y: np.ndarray,
        names: Union[List[str], None] = None,
        marker: Union[List[dict], None] = None,
        text: Union[
            List[
                Union[
                    str,
                    List[str],
                    None
                ]
            ],
            None
        ] = None,
        row: Union[int, None] = None,
        col: Union[int, None] = None
    ):
        
        super().__init__(
            x=x,
            y=y,
            names=names,
            row=row,
            col=col)
        
        self.marker = marker
        self.text = text

        # если передан список словарей marker
        try:
            len_marker =  len(self.marker)
        except:
            len_marker = 0
        
        # идем по словарям marker
        for i in range(len_marker):
            
           # если задан size для marker, и size - это список размеров для каждого объекта,
           # то делаем масштабирование
            if self.marker[i].get('size', None) is not None:    
                self.marker[i]['sizeref'] = 2. * self.marker[i]['size'].max()/(100.**2) if type(self.marker[i]['size']) == np.ndarray else None
                self.marker[i]['sizemode'] = 'area'
                if not self.marker[i]['sizemin']: self.marker[i]['sizemin'] = 3

    def draw(self, fig: go.Figure):

        # получаем количество графиков
        k = self.amount_plots

        # идем по графикам
        for k in range(k):
           
            try:
                x = self.x[:, k]
            except:
                x= self.x
            
            try:
                y = self.y[:, k]
            except:
                y= self.y

            name = self.get_value(self.names, k)
            marker = self.get_value(self.marker, k)
            text = self.get_value(self.text, k)                        
            
            fig.add_trace(go.Scatter(
                x=x,    
                y=y,
                name=name,
                marker=marker,
                text=text,
                mode='markers',
                   visible=False), row=self.row, col=self.col)                                         
        
        return fig

    @property
    def amount_plots(self):
        if self.y.ndim == 1: return 1        
        else: return self.y.shape[1]
