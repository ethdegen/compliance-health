import json
import os
from unstructured_client import UnstructuredClient
from unstructured_client.models import shared
from unstructured_client.models.errors import SDKError

from dotenv import load_dotenv

load_dotenv()

s = UnstructuredClient(
    api_key_auth=os.environ["UNSTRUCTURED_API_KEY"],
    server_url=os.environ["UNSTRUCTURED_SERVER_URL"],
)

with open("src/kka/parse.pdf", "rb") as parse:
    req = shared.PartitionParameters(
        # Note that this currently only supports a single file
        files=shared.Files(
            content=parse.read(),
            file_name="parse.pdf",
        ),
        # Other partition params
        strategy="hi_res",
    )

    try:
        res = s.general.partition(req)

        with open("src/kka/ingest0.json", "w", encoding="utf-8") as output:
            json.dump(res.elements, output, ensure_ascii=False, indent=4)

    except SDKError as e:
        print(e)