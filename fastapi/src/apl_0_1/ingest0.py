import json
import os
from unstructured_client import UnstructuredClient
from unstructured_client.models import shared
from unstructured_client.models.errors import SDKError

from dotenv import load_dotenv

load_dotenv()


with open("src/apl_0_1/parse.json", "r") as input:
    data = json.load(input)

    data = [
        {
            "type": datum.get("type"),
            "element_id": datum.get("element_id"),
            "text": datum.get("text"),
            "page_number": datum.get("metadata").get("page_number"),
            "parent_id": datum.get("metadata").get("parent_id", None),
        }
        for datum in data
    ]

    with open("src/apl_0_1/ingest0.json", "w", encoding="utf-8") as ouput:
        json.dump(data, ouput, ensure_ascii=False, indent=4)
