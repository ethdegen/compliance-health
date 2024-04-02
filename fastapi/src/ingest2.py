import json
import os
from unstructured_client import UnstructuredClient
from unstructured_client.models import shared
from unstructured_client.models.errors import SDKError

from dotenv import load_dotenv

load_dotenv()


with open("src/ingest1.json", "rb") as ingest2:
    data = json.load(ingest2)

    # extract only the policy section
    for i, datum in enumerate(data):
        if datum["type"] == "UncategorizedText" and datum["text"] == "POLICY:":
            data = data[i + 1 :]
            break
    for i, datum in enumerate(data):
        if datum["type"] == "NarrativeText" and datum["text"].startswith(
            "If you have any questions regarding this APL"
        ):
            data = data[:i]
            break

    # parse the policy section
    policies = []
    policy_current = []
    for datum in data:
        if datum["type"] == "Title":
            if policy_current:
                policies += [policy_current]
                policy_current = []

        policy_current += [datum]
    policies += [policy_current]

    # neatify policy data model
    for i, policy in enumerate(policies):
        policy_identifier = policy[0]["text"]
        policy_page_numbers = sorted(
            list(
                {
                    policy_fragment["metadata"]["page_number"]
                    for policy_fragment in policy
                }
            )
        )

        policy_text = "\n\n".join(
            [policy_fragment["text"] for policy_fragment in policy]
        )

        policies[i] = {
            "identifier": policy_identifier,
            "page_numbers": policy_page_numbers,
            "text": policy_text,
        }

    with open("src/ingest2.json", "w", encoding="utf-8") as ingest2:
        json.dump(policies, ingest2, ensure_ascii=False, indent=4)
