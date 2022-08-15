import io
import os
import requests
import zipfile_deflate64 as zipfile


urls = [
    # Output Area boundaries
    ("https://borders.ukdataservice.ac.uk/ukborders/easy_download/prebuilt/shape/infuse_oa_lyr_2011_clipped.zip", "boundaries"),
    # England and Wales: qualifications
    ("https://www.nomisweb.co.uk/output/census/2011/ks501ew_2011_oa.zip", "england_wales_qualifications"),
    # Northern Ireland: all
    ("http://www.ninis2.nisra.gov.uk/Download/Census%202011/Quick%20Statistics%20Tables%20(statistical%20geographies).zip", "northern_ireland"),
    # Scotland: all
    ("https://nrscensusprodumb.blob.core.windows.net/downloads/Output Area blk.zip", "scotland"),
]


def download_files(data_dir):
    for url, parent_dir in urls:
        download_dir = os.path.join(data_dir, parent_dir)
        if os.path.exists(download_dir):
            print(f"Download dir {download_dir} already exists")
            continue

        print(f"Downloading {url}")

        r = requests.get(url)
        if r.status_code != 200:
            raise RuntimeError(f"Error downloading {url}")

        print(f"Extracting to directory {download_dir}")
        z = zipfile.ZipFile(io.BytesIO(r.content))
        z.extractall(download_dir)
