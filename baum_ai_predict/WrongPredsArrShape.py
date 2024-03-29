from MainValidationErr import MainValidationErr

class WrongPredsArrShape(MainValidationErr):
    """
    :code_assign: service
    :code_type: Общие
    :imports: MainValidationErr
    """    
    
    def __init__(self, shape: tuple, type_class: str):
        # размерность массива
        self.shape = shape
        # тип классификации
        self.type_class = type_class
    
    def __repr__(self):
        return 'Неподходящая размерность массива прогнозных значений {} для типа классификации {}' \
               .format(self.shape, self.type_class)

