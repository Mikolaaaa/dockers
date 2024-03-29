import plotly.graph_objects as go

class Canvas():
    """
    Стандартное полотно с простыми графиками
    LinePlot, все графики добавить импорты

    :code_assign: service
    :code_type: Визуализация

    :packages:
    import plotly.graph_objects as go

    Параметры:
    title: str
        Название полотна
    x_title: str
        Название для оси X
    y_title: str
        Название для оси Y
    xaxis: dict
        Cловарь со свойствами для оси X
    yaxis: dict
        Cловарь со свойствами для оси Y
    scene: dict
        Словарь для xaxis, yaxis, zaxis (3d axis)
    showlegend: bool
        Показывать ли легенду
    plots: list
        Список графиков
    shapes: list
        Список фигур
    """

    def __init__(
        self,
        title: str = '',
        x_title: str = '',
        y_title: str = '',
        xaxis: dict = {},
        yaxis: dict = {},
        scene : dict = {},
        showlegend: bool = False,
        plots: list = [],
        shapes: list = [],
    ):

        self.title = title

        # если передан словарь для 3D axis
        if scene:
            self.scene = scene
            self.xaxis = {}
            self.yaxis = {}

        else:
            # если передан словарь для xaxis
            if xaxis:
                self.xaxis = xaxis
            else:
                # берем только название xaxis_title из параметра x_title
                self.xaxis = {'xaxis': {'title': x_title}}
            # если передан словарь для yaxis
            if yaxis:
                self.yaxis = yaxis
            else:
                # берем тольк название yaxis_title из параметра y_title
                self.yaxis = {'yaxis': {'title': y_title}}
            
            self.scene = scene

        self.showlegend = showlegend
        self.amount_plots = 0
        self.amount_shapes = 0
        
        self.plots = plots
        self.shapes = shapes

    def _add_plots(self, plots: list, fig: go.Figure):
        """ Добавляет графики в fig """
        for plot in plots:
            fig = plot.draw(fig)
            self.amount_plots += plot.amount_plots
        return fig

    def _add_shapes(self, shapes: list, fig: go.Figure):
        """ Добавляет фигуры в fig """
        for shape in shapes:
            fig = shape.draw(fig)
            self.amount_shapes += shape.amount_shapes
        return fig

    def to_dict(self):
        return {'amount_plots': self.amount_plots,
                'amount_shapes': self.amount_shapes,
                **self.__dict__}

    def __repr__(self):
        return f'{self.__class__.__name__}(' + \
               f'title={self.title}, ' + \
               f'showlegend={self.showlegend}, ' + \
               f'xaxis={self.xaxis}, ' + \
               f'yaxis={self.yaxis}) ' + \
               f'amount_plots={self.amount_plots} ' + \
               f'amount_shapes={self.amount_shapes})'

