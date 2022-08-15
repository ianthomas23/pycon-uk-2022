from download import download_files
from extract_people import extract_people


data_dir = "/home/data/pycon-uk-2022"


if __name__ == "__main__":
    download_files(data_dir)
    extract_people(data_dir)
