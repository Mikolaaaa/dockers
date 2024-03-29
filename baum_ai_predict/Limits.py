import numpy as np
from MainValidationErr import MainValidationErr

class Limits():
    """
    Класс Интервалы [min, max]
    
    :code_assign: service
    :code_type: Шлюзы
    :imports: MainValidationErr

    :packages:
    from typing import List, Union

    Атрибуты:
    indexes: dict
        Словарь индексов для каждого интервала по ключу
    ver_arr: List[np.ndarray]
        Cписок массивов по принадлежности к интервалу
        В массиве:
        True: значение в пределах интервала
        False: за пределами
    columns: List[List[str]]
        Список списков столбцов, по которым проверяется принадлежность к интервалу
    min: List[List[Union[int, float]]
        Список массивов min значений интервала для каждого столбца
    max: List[List[Union[int, float]]
        Список массивов max значений интервала для каждого столбца
    min_max_dict: List[dict]
        Список словарей
        В словаре:
        ключ - название столбца
        value - (min, max) для данного столбца
        пример, {'Tq': (40, 50), 'Tw': (100, 50)}
    amount_limits: int
        Число созданных интервалов в рамках класса Limits
    """

    def __init__(
        self
    ):

        self. indexes = {}
        self.ver_arr = []
        self.columns = []
        self.min = []
        self.max = []
        self.min_max_dict = []
        self.amount_limits = 0

    def add_limits(
        self,
        key: str,
        values: np.ndarray,
        min_values: list,
        max_values: list,
        columns: list
    ):
        """ Добавляет интервал в класс """

        # переводим списки min_values и max_values в массив
        min_values = np.array(min_values)
        max_values = np.array(max_values)   

        # проверяем на соответствие количество указанных столбцов, количество max и min значений
        if (len(min_values) != len(columns)) or (len(max_values) != len(columns)):
            raise MainValidationErr('Проверьте на соответствие введенное количество столбцов, min и max значений')
        # проверяем, чтобы все min значения были меньше max
        if (min_values >= max_values).sum() > 0:
            raise MainValidationErr('Проверьте значения min и max значений')
    
        self.indexes[key] = self.amount_limits
        self.amount_limits += 1
        self.min.append(min_values)
        self.max.append(max_values)
        self.columns.append(columns)
        
        # объединяем min и max значения для каждого столбца
        min_max_values = [*zip(min_values, max_values)]
        # формируем словарь с min и max значением для каждого признака
        min_max_dict = {col: min_max_values[i]  for i, col in enumerate(columns)}
        self.min_max_dict.append(min_max_dict)

        # получаем bool массив выхода за пределы интервала
        not_in_limits = self._get_not_in_limits(key, values)
        self.ver_arr.append(~not_in_limits)

        return not_in_limits

    def update_limits(
        self,
        key: str,
        values: np.ndarray,
    ):
        
        # получаем массив выхода за пределы интервала
        not_in_limits = self._get_not_in_limits(key, values)
        # добавляем not_in_limits в массив self.ver_arr по индексу indexes[key]
        self.ver_arr[self.indexes[key]] = np.vstack((
            self.ver_arr[self.indexes[key]],
            ~not_in_limits))

        return not_in_limits

    def _get_not_in_limits(
        self,
        key: str,
        values: np.ndarray,
    ):
        """
        Возвращает bool массив по выходу значений values за пределы интервала min-max
        True - значение вышло за пределы
        False - не вышло
        """

        # создаем массив из 1 по размеру values
        np_ones = np.ones(values.shape)
        # создаем массив выхода за пределы интервала
        not_in_limits = (values < np_ones * self.min[self.indexes[key]]) + (values > np_ones * self.max[self.indexes[key]])

        return not_in_limits

