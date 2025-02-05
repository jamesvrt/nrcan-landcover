import json
import os
import shutil
from tempfile import mkdtemp
from typing import Any, Dict
from zipfile import ZipFile

import requests


def _unzip_dir(zip_path: str, unzip_dir: str) -> str:
    with ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(unzip_dir)
        return unzip_dir


def download_asset_package(metadata: Dict[str, Any]) -> str:

    access_url = metadata["tiff_metadata"]["dcat:accessURL"].get("@id")

    tmp_dir = mkdtemp()

    if access_url.startswith("http"):
        tmp_path = os.path.join(tmp_dir, 'file.zip')
        resp = requests.get(access_url)

        with open(tmp_path, 'wb') as f:
            f.write(resp.content)

        asset_package_path = _unzip_dir(tmp_path, tmp_dir)
    else:
        asset_package_path = _unzip_dir(access_url, tmp_dir)

    return asset_package_path


def remove_asset_package(dirpath: str) -> None:
    shutil.rmtree(dirpath)


def get_metadata(metadata_url: str) -> Dict[str, Any]:
    """Gets metadata from the various formats published by NRCan.

    Args:
        metadata_url (str): url to get metadata from.

    Returns:
        dict: Land Cover Metadata.
    """
    if metadata_url.endswith(".jsonld"):
        if metadata_url.startswith("http"):
            metadata_response = requests.get(metadata_url)
            jsonld_response = metadata_response.json()
        else:
            with open(metadata_url) as f:
                jsonld_response = json.load(f)

        tiff_metadata = [
            i for i in jsonld_response.get("@graph")
            if i.get("dct:format") == "TIFF"
        ][0]

        geom_obj = next(
            (x["locn:geometry"] for x in jsonld_response["@graph"]
             if "locn:geometry" in x.keys()),
            [],
        )  # type: Any
        geom_metadata = next(
            (json.loads(x["@value"])
             for x in geom_obj if x["@type"].startswith("http")),
            None,
        )
        if not geom_metadata:
            raise ValueError("Unable to parse geometry metadata from jsonld")

        description_metadata = [
            i for i in jsonld_response.get("@graph")
            if "dct:description" in i.keys()
        ][0]

        metadata = {
            "tiff_metadata": tiff_metadata,
            "geom_metadata": geom_metadata,
            "description_metadata": description_metadata
        }

        return metadata
    else:
        # only jsonld support.
        raise NotImplementedError()
