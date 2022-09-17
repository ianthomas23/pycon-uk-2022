from add import add_ethnic_group, add_highest_qualification
from download import download_files
from extract_people import extract_people


data_dir = "/home/data/pycon-uk-2022"


if __name__ == "__main__":
    download_files(data_dir)
    extract_people(data_dir)
    add_highest_qualification(data_dir)
    add_ethnic_group(data_dir)
