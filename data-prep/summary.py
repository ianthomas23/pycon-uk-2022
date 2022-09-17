from glob import glob
import os
import pandas as pd


_cat_columns = ["ethnic_group", "highest_qualification"]


def _summary(filename):
    df = pd.read_parquet(filename)
    people = len(df)
    areas = len(df.area_code.unique())
    print(f"{filename}: people {people:,}, areas {areas:,}, people/area {people/areas:.1f}")

    for cat_column in _cat_columns:
        if cat_column in df.columns:
            print("   ", cat_column, df.groupby(cat_column).size().to_dict())

    return people, areas


if __name__ == "__main__":
    pattern = os.path.join("..", "parq", "*.parq")
    total_people = 0
    total_areas = 0
    for filename in glob(pattern):
        people, areas = _summary(filename)
        total_people += people
        total_areas += areas
    print(f"Total people {total_people:,}, total areas {total_areas:,}")
