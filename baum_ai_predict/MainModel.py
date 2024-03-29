class MainModel():
    """
    Класс Основаная Модель
    
    :code_assign: service
    :code_type: Машинное обучение

    Параметры:
    model: type
        Модель
    vars_dict: dict
        Словарь переменных

    Атрибуты:
    model: type
        Модель
    vars_dict: dict
        Словарь переменных
    """

    def __init__(
        self,
        model: type,
        vars_dict: dict,
    ) -> None:
        
        self.vars_dict = vars_dict
        self.model = model

    def __str__(self) -> str:
        # для вывода инфо о модели после загрузки с инфо из vars_dict
        return str(self.model)

