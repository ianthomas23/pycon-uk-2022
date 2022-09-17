# Visualising large datasets: everyone in the UK Census

## Ian Thomas

### PyCon UK 2022 talk, 18th September 2022

To run jupyter notebooks, first obtain the prepared parquet data files and put them in a directory called `parq` in the top level of this repository.

The parquet datafiles can be downloaded from

If you want to create the data files yourself, which is not advised as the process is slow:

  - `cd data-prep`
  - Set the `data_dir` in `data-prep.py` to be the directory to download and extract the data files into.
  - Run `python data-prep.py` and wait a long time for it to finish.

Census data is available for reuse under the Open Government Licence.
Required source accreditation: Office for National Statistics

The contents of this repository are available under the BSD 3-Clause License specified in the `LICENSE` file.
