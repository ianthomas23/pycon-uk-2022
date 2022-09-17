from glob import glob
import numpy as np
import os
import pandas as pd


qualification_lookup = dict(
    E=dict(
        target="england.parq",
        input_dir=["england_wales_qualifications", "KS501ew_2011_oa", "KS501EW_2011STATH_NAT_OA_REL_1.3.3"],
        input_file="KS501EWDATA01_*.CSV",
        none="KS501EW0002",
        level1="KS501EW0003",
        level2="KS501EW0004",
        level3="KS501EW0006",
        level4="KS501EW0007",
        index="GeographyCode",
    ),
    N=dict(
        target="northern_ireland.parq",
        input_dir=["northern_ireland", "SMALL AREAS"],
        input_file="KS501NIDATA0.CSV",
        none="KS501NI0002",
        level1="KS501NI0003",
        level2="KS501NI0004",
        level3="KS501NI0006",
        level4="KS501NI0007",
        index="GeographyCode",
    ),
    S=dict(
        target="scotland.parq",
        input_dir=["scotland"],
        input_file="KS501SC.csv",
        none="All people aged 16 and over: No qualifications",
        level1="All people aged 16 and over: Highest level of qualification: Level 1 qualifications",
        level2="All people aged 16 and over: Highest level of qualification: Level 2 qualifications",
        level3="All people aged 16 and over: Highest level of qualification: Level 3 qualifications",
        level4="All people aged 16 and over: Highest level of qualification: Level 4 qualifications and above",
        index="",
    ),
    W=dict(
        target="wales.parq",
        input_dir=["england_wales_qualifications", "KS501ew_2011_oa", "KS501EW_2011STATH_NAT_OA_REL_1.3.3"],
        input_file="KS501EWDATA01_W.CSV",
        none="KS501EW0002",
        level1="KS501EW0003",
        level2="KS501EW0004",
        level3="KS501EW0006",
        level4="KS501EW0007",
        index="GeographyCode",
    ),
)

ethnic_group_lookup = dict(
    E=dict(
        target="england.parq",
        input_dir=["england_wales_ethnic_group", "KS201ew_2011_oa", "KS201EW_2011STATH_NAT_OA_REL_1.3.3"],
        input_file="KS201EWDATA01_*.CSV",
        asian=["KS201EW0010", "KS201EW0011", "KS201EW0012", "KS201EW0013", "KS201EW0014"],
        black=["KS201EW0015", "KS201EW0016", "KS201EW0017"],
        mixed=["KS201EW0006", "KS201EW0007", "KS201EW0008", "KS201EW0009"],
        white=["KS201EW0002", "KS201EW0003", "KS201EW0004", "KS201EW0005"],
        index="GeographyCode",
    ),
    N=dict(
        target="northern_ireland.parq",
        input_dir=["northern_ireland", "SMALL AREAS"],
        input_file="KS201NIDATA0.CSV",
        asian=["KS201NI0003", "KS201NI0005", "KS201NI0006", "KS201NI0007", "KS201NI0008"],
        black=["KS201NI0009", "KS201NI0010", "KS201NI0011"],
        mixed="KS201NI0012",
        white=["KS201NI0002", "KS201NI0004"],
        index="GeographyCode",
    ),
    S=dict(
        target="scotland.parq",
        input_dir=["scotland"],
        input_file="KS201SC.csv",
        asian="Asian, Asian Scottish or Asian British",
        black="African",
        mixed="Mixed or multiple ethnic groups",
        white="White",
        index="",
    ),
    W=dict(
        target="wales.parq",
        input_dir=["england_wales_ethnic_group", "KS201ew_2011_oa", "KS201EW_2011STATH_NAT_OA_REL_1.3.3"],
        input_file="KS201EWDATA01_W.CSV",
        asian=["KS201EW0010", "KS201EW0011", "KS201EW0012", "KS201EW0013", "KS201EW0014"],
        black=["KS201EW0015", "KS201EW0016", "KS201EW0017"],
        mixed=["KS201EW0006", "KS201EW0007", "KS201EW0008", "KS201EW0009"],
        white=["KS201EW0002", "KS201EW0003", "KS201EW0004", "KS201EW0005"],
        index="GeographyCode",
     ),
)


def _sanitise_count(count):
    if count == "-":
        return 0
    elif isinstance(count, str):
        return int(count.replace(",", ""))
    else:
        return count


def _single_nation_column(letter, target_file, data_dir, df, column_name, cats, seed, lookup):
    print(f"Adding {column_name} to {target_file}")

    input_dir = lookup[letter]["input_dir"]
    input_file = lookup[letter]["input_file"]
    input_filename = os.path.join(data_dir, *input_dir, input_file)
    if "*" in input_filename:
        filenames = glob(input_filename)
        filenames.sort()
        input_df = pd.concat((pd.read_csv(f) for f in filenames))
    else:
        input_df = pd.read_csv(input_filename)

    # Use predictable seed for reproducibility.
    rng = np.random.default_rng(seed + ord(letter))

    index = lookup[letter]["index"]
    cat_lookups = [lookup[letter][cat] for cat in cats]
    all_new_column = np.full((len(df),), -1)
    nareas = df["area_code"].nunique()

    start_match = f"{letter}0"
    i = 0
    for _, row in input_df.iterrows():
        if index == '':
            area_code = row[0]
        else:
            area_code = row[index]

        if area_code[:2] != start_match:
            continue

        counts = []
        for cat_lookup in cat_lookups:
            if isinstance(cat_lookup, list):
                count = 0
                for c in cat_lookup:
                    count += _sanitise_count(row[c])
            else:
                count = _sanitise_count(row[cat_lookup])
            counts.append(count)
        ntotal = np.sum(counts)

        # Find corresponding rows in df.
        mask = (df["area_code"] == area_code)
        r = df[mask]
        npeople = len(r)
        nother = npeople - ntotal
        print(i, "of", nareas, area_code, npeople)
        if nother < 0:
            print(counts)
            raise RuntimeError(f"Problem with number of people: {npeople} {ntotal} {nother}")

        # Randomly assign categories.
        new_column = np.repeat(-1, npeople)
        offsets = np.concatenate(([0], np.cumsum(counts)))
        for j in range(len(counts)):
            new_column[offsets[j]:offsets[j+1]] = j
        rng.shuffle(new_column)

        df.loc[mask, column_name] = new_column
        all_new_column[mask] = new_column
        i += 1

    # Create dummy new column
    df[column_name] = all_new_column
    df[column_name] = df[column_name].astype("category")
    map = {-1: "other"}
    for j, cat in enumerate(cats):
        map[j] = cat
    df[column_name] = df[column_name].cat.rename_categories(map)
    print(f"Overwriting {target_file}")
    df.to_parquet(target_file)


def add_ethnic_group(data_dir):
    column_name = "ethnic_group"
    lookup = ethnic_group_lookup
    cats = ["asian", "black", "mixed", "white"]
    seed = 29481

    for letter in lookup.keys():
        target_file = os.path.join("..", "parq", lookup[letter]["target"])
        if not os.path.exists(target_file):
            raise RuntimeError(f"File does not exist: {target_file}")
        df = pd.read_parquet(target_file)
        if column_name not in df.columns:
            _single_nation_column(
                letter, target_file, data_dir, df, column_name, cats, seed, lookup)
        else:
            print(f"{target_file} already contains {column_name}")


def add_highest_qualification(data_dir):
    column_name = "highest_qualification"
    lookup = qualification_lookup
    cats = ["none", "level1", "level2", "level3", "level4"]
    seed = 41953

    for letter in lookup.keys():
        target_file = os.path.join("..", "parq", lookup[letter]["target"])
        if not os.path.exists(target_file):
            raise RuntimeError(f"File does not exist: {target_file}")
        df = pd.read_parquet(target_file)
        if column_name not in df.columns:
            _single_nation_column(
                letter, target_file, data_dir, df, column_name, cats, seed, lookup)
        else:
            print(f"{target_file} already contains {column_name}")
