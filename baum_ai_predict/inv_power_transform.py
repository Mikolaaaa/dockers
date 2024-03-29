import numpy as np
from sklearn.preprocessing import PowerTransformer


def inv_power_transform(arr: np.array, pt: PowerTransformer, **kwargs):
    """
    проводит обратное преобразование power_transform
    
    :code_assign: service
    :code_type: Анализ данных/Препроцессинг
    
    :packages:
    from sklearn.preprocessing import PowerTransformer
    
    параметры: многомерный массив, трансформер
    массив должен быть с shape = (nrows, ncols)
    и если передается одномерный массив (1 столбец), то до передачи в функцию делать reshape(-1,1)
    
    Внимание! склерновский inverse_transform иногда выдает nan при обратных преобразованиях.
    В этом случае выдаем ошибку.
    Скорее всего, это происходит, когда обучение происходило на НЕ репрезентативной обучающей выборке,
    и на новых данных при прямом и обратном трансформировании возникают аномальные значения
    (особенно на предсказаниях полиномиальной регрессии).
    Возможно в будущем вместо возврата ошибки производить заполнение Nan предыдущим, затем будущим значением.
    """

    # инициализируем текст ошибки
    error = None
    
    # считаем количество пропусков до преобразования
    amount_nan1 = np.isnan(arr).sum()

    # обратное трансформирование
    try:
        inv_arr_transformed = pt.inverse_transform(arr)
    # ошибка - передаем во фронт
    except Exception as err:
        error = 'Ошибка обратного преобразования inv_power_transform: {:s}'.format(repr(err))
        return None, error    
    
    # считаем количество пропусков после преобразования
    amount_nan2 = np.isnan(inv_arr_transformed).sum()
    
    # если количество пропусков увеличилось
    if amount_nan2 > amount_nan1:
        # ошибка
        error = 'При обратном преобразовании PowerTransform возникли дополнительные пропуски NaN в количестве {}.'\
                .format(amount_nan2 - amount_nan1)
    
    # возвращаем преобразованный массив, ошибку
    return inv_arr_transformed, error

