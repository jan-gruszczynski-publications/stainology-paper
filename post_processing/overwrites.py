import pandas as pd
from pydantic import BaseModel

from post_processing.pipeline_utils import AbstractDFConverter


class ConditionalOverWrite(BaseModel, AbstractDFConverter):
    conditions: list[dict] = [{
        'cond_field': 'expr_score',  # can i make this into list ['expr_score', 'expr_intenstiy']
        'cond': lambda expr_score: expr_score in ['0', 0],  # and then do lambda expr_score, expr_intensity: ...
        'res_field': 'expr_type',
        'res_value': 'negative'
    }]

    def __call__(self, df: pd.DataFrame, *args, **kwargs) -> pd.DataFrame:
        df = df.copy(deep=True)

        for condition in self.conditions:
            cond_fields = condition['cond_field']
            cond_fn = condition['cond']
            res_field = condition['res_field']
            res_value = condition['res_value']

            if isinstance(cond_fields, list):
                # Apply condition using multiple columns
                def safe_cond(row):
                    # Only call cond_fn if none of the values are NA
                    if any(pd.isna(row[field]) for field in cond_fields):
                        return False
                    return cond_fn(*[row[field] for field in cond_fields])

                mask = df.apply(safe_cond, axis=1)
            else:
                # Single column
                mask = df[cond_fields].apply(lambda val: False if pd.isna(val) else cond_fn(val))

            df.loc[mask, res_field] = res_value
            print("Overwriting", res_field, "with", res_value,
                  "where", cond_fields, "passes condition.", "Mask size", f"{mask.sum()}")

        return df
