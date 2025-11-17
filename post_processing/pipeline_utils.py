import pandas as pd


class SubPipeline:

    def __init__(self, steps: list = None, subset: list[str] = None):
        if steps is None:
            steps = []
        if subset is None:
            subset = []
        self.steps: list[callable] = steps
        self.subset: list[str] = subset

    def __call__(self, data: pd.DataFrame | pd.Series) -> pd.DataFrame | pd.Series:
        if isinstance(data, pd.Series):
            for step in self.steps:
                data = step(data)
        elif isinstance(data, pd.DataFrame):
            for subset in self.subset:
                data[subset] = set(data[subset])
        else:
            raise ValueError(f"Invalid data type: {type(data)}")
        return data


class Pipeline:
    def __init__(self, column_processing_map: dict[str, SubPipeline],
                 df_processing_map: list[SubPipeline] | list[callable]):
        self.column_processing_map: dict[str, SubPipeline] = column_processing_map
        self.df_processing_map: list[SubPipeline] = df_processing_map

    def __call__(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        for col, sub_pipeline in self.column_processing_map.items():
            df[col] = sub_pipeline(df[col])

        for sub_pipeline in self.df_processing_map:
            df = df.copy()
            df = sub_pipeline(df).reset_index(drop=True)
        return df


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class SingletonClass(metaclass=SingletonMeta):
    def __init__(self):
        self.my_dict = {}


class AbstractDFConverter:
    singleton = SingletonClass()
