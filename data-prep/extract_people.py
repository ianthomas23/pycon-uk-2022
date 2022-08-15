import datetime as dt
import geopandas as gpd
import numpy as np
import os
import pandas as pd
from shapely import speedups
from shapely.geometry import Point


lookup = dict(
    #"E": "england.parq",
    #"N": "northern_ireland.parq",
    W=dict(
        target="wales.parq",
        input_dir=["england_wales_qualifications", "KS501ew_2011_oa", "KS501EW_2011STATH_NAT_OA_REL_1.3.3"],
        input_file="KS501EWDATA01_W.CSV",
        index="GeographyCode",
        column="KS501EW0001",
    ),
    #"S": "scotland.parq",
)

speedups.enable()


# Function called once per polygon.
def _get_points_in_geom(rng, geom, npoints):
    ret_xy = np.empty((npoints, 2), dtype=np.float32)
    found = 0

    xmin, ymin, xmax, ymax = geom.bounds
    while found < npoints:
        xys = rng.random((npoints, 2))*(xmax-xmin, ymax-ymin) + (xmin, ymin)
        for i in range(npoints):
            xy = xys[i]
            if geom.contains(Point(xy)):
                ret_xy[found] = xy
                found += 1
                if found == npoints:
                    break
    return ret_xy


def _single_nation(letter, target_file, data_dir):
    # Load boundary geometries.
    boundary_file = os.path.join(data_dir, "boundaries", "infuse_oa_lyr_2011_clipped.shp")
    boundaries_df = gpd.read_file(boundary_file)
    boundaries_df = boundaries_df[boundaries_df.geo_code.str[0] == letter]  # This nation only.
    print(f"{letter} boundaries {len(boundaries_df)}")

    # Load counts per boundary.
    input_dir = lookup[letter]["input_dir"]
    input_file = lookup[letter]["input_file"]
    counts_filename = os.path.join(data_dir, *input_dir, input_file)
    counts_df = pd.read_csv(counts_filename)
    if len(counts_df) != len(boundaries_df):
        raise RuntimeError(f"Mismatch in number of output areas: {len(boundaries_df)}, {len(counts_df)}")

    index = lookup[letter]["index"]
    column = lookup[letter]["column"]
    rng = np.random.default_rng(5912 + ord(letter))

    x = []
    y = []
    output_area = []

    start = dt.datetime.now()
    i = 0
    for _, row in boundaries_df.iterrows():
        geo_code = row.geo_code

        count_row = counts_df[counts_df[index] == geo_code]
        if len(count_row) != 1:
            raise RuntimeError(f"Expected 1 row matching geo_code {geo_code}, found {len(count_row)}")

        count = count_row[column].values[0]
        if isinstance(count, str):
            count = int(count.replace(",", ""))

        print(i, geo_code, count)
        xy = _get_points_in_geom(rng, row.geometry, count)

        x.append(xy[:, 0])
        y.append(xy[:, 1])
        output_area.append(np.repeat(geo_code, count))

        i += 1
        if i > 10:
            break

    end = dt.datetime.now()
    print("Calculation time", (end-start).total_seconds(), "s")

    x = np.concatenate(x)
    y = np.concatenate(y)
    output_area = np.concatenate(output_area)

    print("Total people", len(x))
    df = pd.DataFrame(dict(x=x, y=y))
    output_area = pd.Series(output_area, dtype="category")
    df["output_area"] = output_area
    print(df)
    print("Writing file", target_file)
    df.to_parquet(target_file)


def extract_people(data_dir):
    for letter in lookup.keys():
        target_file = os.path.join("..", lookup[letter]["target"])
        if os.path.exists(target_file):
            print(f"File {target_file} already exists")
        else:
            _single_nation(letter, target_file, data_dir)
