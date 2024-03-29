import numpy as np


def set_labels(arr):
        """
        вместо значений вероятности ставит 0 или 1 по max значению вероятности
        
        :code_assign: service
        :code_type: Машинное обучение
        """
        
        arg_max = arr.argmax()
        new_arr = np.zeros_like(arr)
        new_arr[arg_max] = 1
        return new_arr


