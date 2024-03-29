from get_f1 import get_f1
from get_auc_roc import get_auc_roc
from get_precision import get_precision
from get_recall import get_recall
from get_accuracy import get_accuracy
from get_rmse import get_rmse
from get_r2 import get_r2
from get_mae import get_mae
from get_wmape import get_wmape

def get_metric(metric_name: str, vars_dict: dict):
    """
    возвращает данные для расчета метрики по ее названию

    :code_assign: service
    :code_type: Машинное обучение/Метрики
    :imports: get_f1, get_auc_roc, get_precision, get_recall, get_accuracy, get_rmse, get_r2, get_mae, get_wmape

    параметры: название метрики, словарь переменных
    """

    # получаем значение для average (метрики классификации)
    average = lambda: 'binary' if vars_dict.get('class_type', None) == 'binary' else None
    # получаем значение для multi_class (AUC_ROC)
    multi_class = lambda: 'ovo' if vars_dict.get('class_type', None) == 'multiclass' else 'raise'

    # словарь функций расчета метрики в соответствии с названием метрики
    metric_dict = {
        'F1': {'fun': get_f1, 'args_make_scorer': {'multioutput': False},
               'args_score': {'average': average()}},
        'AUC_ROC': {'fun': get_auc_roc, 'args_make_scorer': {'average': 'macro', 'needs_proba': True},
                    'args_score': {'multi_class': multi_class()}},
        'Precision': {'fun': get_precision, 'args_make_scorer': {'multioutput': False},
                      'args_score': {'average': average()}},
        'Recall': {'fun': get_recall, 'args_make_scorer': {'multioutput': False},
                   'args_score': {'average': average()}},
        'Accuracy': {'fun': get_accuracy, 'args_make_scorer': {'multioutput': False},
                     'args_score': {}},
        'RMSE': {'fun': get_rmse,
                 'args_make_scorer': {'greater_is_better': False, 'multioutput': 'uniform_average'},
                 'args_score': {}},
        'MAE': {'fun': get_mae,
                'args_make_scorer': {'greater_is_better': False, 'multioutput': 'uniform_average'},
                'args_score': {}},
        'WMAPE': {'fun': get_wmape,
                  'args_make_scorer': {'greater_is_better': False, 'multioutput': False},
                  'args_score': {}},
        'R2': {'fun': get_r2,
               'args_make_scorer': {'greater_is_better': True, 'multioutput': 'uniform_average'},
               'args_score': {}},
    }

    return metric_dict[metric_name]