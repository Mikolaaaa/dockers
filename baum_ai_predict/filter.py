import pandas as pd
from typing import Union


def filter_shd(
        df: pd.DataFrame,
        df_levels: pd.DataFrame,
        flags: Union[str, list] = None
):
    """
    Функция фильтрации для СХД
    :code_assign: users
    :code_type: Пользовательские функции
    :imports:
    :packages:
    import pandas as pd
    :param_block pd.DataFrame df: датасет
    :param_block pd.DataFrame df_levels: датасет содержащий уровни
    :param list flags: список выбранных параметров для фильтрации
    :returns: df, df_levels, error
    :rtype: pd.DataFrame, pd.DataFrame, str
    :semrtype: DataSet, DataSet,
    """
    error = ''
    if flags is None:
        raise Exception('Invalid parameters')
    if isinstance(flags, str):
        flags = [flags]

    df = df[df['object'].isin(flags)]
    df_last_value_capacity = df['Capacity usage(%)'].max()

    array_number = df.iloc[0]['array_num']
    mapped_flags = {
        'System': array_number,
        'StoragePool001': array_number + ' SP1',
        'StoragePool002': array_number + ' SP2'
    }

    level_flags = []
    for f in flags:
        level_flags.append(mapped_flags[f])

    print(level_flags)

    df_levels = df_levels[df_levels['object'].isin(level_flags)]
    print(df_levels)
    columns_to_drop = [col for col in df_levels.columns if df_levels[col].dtype in ['int64', 'float64'] and df_levels[col].min() < df_last_value_capacity]
    # print(columns_to_drop)
    df_levels.drop(columns=columns_to_drop, inplace=True)

    return df, df_levels, error
