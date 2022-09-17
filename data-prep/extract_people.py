import datetime as dt
import geopandas as gpd
from glob import glob
import numpy as np
import os
import pandas as pd
from shapely import speedups
from shapely.geometry import Point


lookup = dict(
    E=dict(
        target="england.parq",
        input_dir=["england_wales_population", "ks101ew_2011oa", "KS101EW_2011STATH_NAT_OA_REL_1.1.1"],
        input_file="KS101EWDATA01_*.CSV",
        index="GeographyCode",
        column="KS101EW0001",
    ),
    N=dict(
        target="northern_ireland.parq",
        input_dir=["northern_ireland", "SMALL AREAS"],
        input_file="KS101NIDATA0.CSV",
        index="GeographyCode",
        column="KS101NI0001",
    ),
    S=dict(
        target="scotland.parq",
        input_dir=["scotland"],
        input_file="QS101SC.csv",
        index="",
        column="All people",
    ),
    W=dict(
        target="wales.parq",
        input_dir=["england_wales_population", "ks101ew_2011oa", "KS101EW_2011STATH_NAT_OA_REL_1.1.1"],
        input_file="KS101EWDATA01_W.CSV",
        index="GeographyCode",
        column="KS101EW0001",
    ),
)

limit_areas = None
#limit_areas = 10

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
    if "*" in counts_filename:
        filenames = glob(counts_filename)
        filenames.sort()
        counts_df = pd.concat((pd.read_csv(f) for f in filenames))
    else:
        counts_df = pd.read_csv(counts_filename)

    column = lookup[letter]["column"]
    index = lookup[letter]["index"]
    if index == '':
        counts_df = counts_df[counts_df.iloc[:, 0].str[:2] == f"{letter}0"]  # This nation only.
    else:
        counts_df = counts_df[counts_df[index].str[0] == letter]  # This nation only.
    if len(counts_df) != len(boundaries_df):
        raise RuntimeError(f"Mismatch in number of output areas: {len(boundaries_df)}, {len(counts_df)}")

    # Use predictable seed for reproducibility.
    rng = np.random.default_rng(5912 + ord(letter))

    x = []
    y = []
    output_area = []

    start = dt.datetime.now()
    i = 0
    for _, row in boundaries_df.iterrows():
        geo_code = row.geo_code

        if index == '':
            count_row = counts_df[counts_df.iloc[:, 0] == geo_code]
        else:
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
        if limit_areas is not None and i > limit_areas:
            break

    end = dt.datetime.now()
    print("Calculation time", (end-start).total_seconds(), "s")

    x = np.concatenate(x)
    y = np.concatenate(y)
    output_area = np.concatenate(output_area)

    print("Total people", len(x))
    df = pd.DataFrame(dict(x=x, y=y))
    output_area = pd.Series(output_area, dtype="category")
    df["area_code"] = output_area
    print(df)
    print("Writing file", target_file)
    df.to_parquet(target_file)


def extract_people(data_dir):
    for letter in lookup.keys():
        target_file = os.path.join("..", "parq", lookup[letter]["target"])
        if os.path.exists(target_file):
            print(f"File {target_file} already exists")
        else:
            _single_nation(letter, target_file, data_dir)
