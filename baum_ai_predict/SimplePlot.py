from abc import ABC, abstractmethod
from typing import List, Union, Any
import numpy as np
import pandas as pd
import plotly.graph_objects as go


class SimplePlot(ABC):
    """
    Простой график или группа простых однотипных графиков

    :code_assign: service
    :code_type: Визуализация

    :packages:
    from abc import ABC, abstractmethod
    from typing import List, Union, Any

    Параметры:
    x: координаты X
    y: координаты Y
    names: список названий графиков для легенды
    row: строка в subplots
    col: столбец в subplots
    showlegend: показвать легенду
    legendgroup: группа легенды
    """

    def __init__(
        self,
        x: Union[np.ndarray, pd.DatetimeIndex, None] = None,
        y: Union[np.ndarray, None] = None,
        names: Union[List[str], None] = None,
        row: Union[int, None] = None,
        col: Union[int, None] = None,
        showlegend: Union[bool, None] = None,
        legendgroup: Union[str, None] = None
    ):
        
        self.x = self.check_arr(x)
        self.y = self.check_arr(y)
        self.names = names
        self.row = row
        self.col = col
        self.showlegend = showlegend
        self.legendgroup = legendgroup

    @staticmethod
    def check_arr(arr: np.ndarray):
        """ Проверка массива на размерность и NaN """
        
        # Если массив не пустой и это не DatetimeIndex
        if (arr is not None) and (type(arr) is not pd.DatetimeIndex):
            
            # Если тип столбца float или int
            # (object и datetime не берем, так как
            # np.where переводит время datetime в формат unix,
            # а на типе object выдает ошибку)
            if arr.dtype in (int, float):

                # Если тип столбца int
                if arr.dtype == int:
                    # Приводим к типу float перед обработкой
                    arr = arr.astype('float')
            
                # Заменяем NaN на None для фронта
                arr = np.where(np.isnan(arr), None, arr)
            
            # Если 2D массив с одним столбцом, делаем ravel
            if arr.ndim == 2 and arr.shape[1] == 1: arr = arr.ravel()
            
        return arr
    
    @staticmethod
    def get_value(value: Union[List[Any], Any], k: int):
        """ Если value - список, берет k-е значение, иначе value """
        if type(value) is list: value = value[k]
        else: value = value
        return value

    @property
    @abstractmethod
    def amount_plots(self):
        """
        Считает количество однотипных графиков,
        которые передаются одним массивом как один график
        """
        pass

    @abstractmethod
    def draw(self, fig: go.Figure):
        """ Добавляет графики в go.Figure """
        pass

