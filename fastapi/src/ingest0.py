import json
import os
from unstructured_client import UnstructuredClient
from unstructured_client.models import shared
from unstructured_client.models.errors import SDKError

from dotenv import load_dotenv

load_dotenv()


with open("src/ingest.json", "rb") as ingest:
    data = json.load(ingest)

    # remove left-hand footer
    data = [datum for datum in data if not datum["type"] == "Footer"]

    # remove right-hand footer
    data = [
        datum
        for datum in data
        if not (
            datum["type"] == "Title"
            and datum["text"].startswith("State of California ")
            and datum["text"].endswith(", Governor")
        )
    ]

    # remove footnotes
    data = [
        datum
        for datum in data
        if not (
            datum["type"] == "NarrativeText" and datum["text"].split(" ")[0].isnumeric()
        )
    ]

    # remove headers
    data = [
        datum
        for datum in data
        if not (
            datum["type"] == "Title"
            and datum["text"].startswith("ALL PLAN LETTER ")
            and " Page " in datum["text"]
        )
    ]

    with open("src/ingest0.json", "w", encoding="utf-8") as ingest0:
        json.dump(data, ingest0, ensure_ascii=False, indent=4)
