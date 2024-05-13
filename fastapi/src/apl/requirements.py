import json
import os

import openai
from dotenv import load_dotenv
from llama_index.llms.openai import OpenAI
from unstructured_client import UnstructuredClient
from unstructured_client.models import shared

load_dotenv()

openai.api_key = os.environ["OPENAI_API_KEY"]

pdf = UnstructuredClient(
    api_key_auth=os.environ["UNSTRUCTURED_API_KEY"],
    server_url=os.environ["UNSTRUCTURED_SERVER_URL"],
)

llm = OpenAI(
    model="gpt-4-turbo",
    temperature=0,
    max_tokens=4096,
    timeout=600,
)


def parse_with_unstructured(letter: str) -> str:
    return json.dumps(
        pdf.general.partition(
            shared.PartitionParameters(
                files=shared.Files(
                    content=letter,
                    file_name="apl.pdf",
                ),
                strategy="hi_res",
            )
        ).elements,
        indent=4,
    )


def restructure_parsed_letter(letter_parsed: str) -> str:
    return json.dumps(
        [
            {
                "text": element.get("text"),
                "type": element.get("type"),
                "element_id": element.get("element_id"),
                "parent_id": element.get("metadata").get("parent_id", None),
                "page_number": element.get("metadata").get("page_number"),
            }
            for element in json.loads(letter_parsed)
        ],
        indent=4,
    )


def locate_policy_boundary(letter_parsed: str) -> str:
    response = llm.complete(
        f'\
You are an expert at locating the policy section within a healthcare all plan letter. \
You are given this letter in the form of a JSON array. \
The policy section starts with a header resembling "POLICY". \
Return the element ID of this policy header in a JSON object with a single key `element_id`.\
\n\n\
Here is the all plan letter parsed to a JSON array:\
\n\n\
{json.dumps(json.loads(letter_parsed), separators=(",", ":"))}\
',
        response_format={
            "type": "json_object",
        },
    )

    return json.dumps(
        json.loads(
            response.text,
        ),
        indent=4,
    )


def extract_letter_policy(letter_parsed: str, policy_boundary: str) -> str:
    letter = json.loads(letter_parsed)
    for i, element in enumerate(letter):
        if element["element_id"] == policy_boundary:
            return json.dumps(
                letter[i:],
                indent=4,
            )


def locate_subpolicy_boundaries(letter_policy: str) -> str:
    response = llm.complete(
        f"\
You are an expert at locating all sub-policy boundaries within a healthcare all plan letter containing a policy. \
You are given this letter in the form of a JSON array. \
This letter contains either a single policy or multiple sub-policies. \
If the letter contains multiple sub-policies, each sub-policy may be numbered with a numeral or roman numeral. \
Some sub-policies may themselves include sub-sub-policies, each of which may itself start with a numbered heading. \
Whenever you see sub-sub-policies, consider them part of the respective sub-policy. \
Output an object of `boundaries` in JSON, containing an array with each element representing summary data pertaining to a single sub-policy boundary. \
Every sub-policy boundary object must have the following keys: `serial_number`, `heading` and `element_id`. \
Use standard integers for the sub-policy serial numbers and ensure that serial numbering begins at 1. \
Capture full headings of every sub-policy and do not shorten them. \
`element_id` must be the element ID of the final element that is part of the respective sub_policy. \
If the letter only contains a single policy, then `boundaries` should be an empty array. \
\n\n\
Here is the all plan letter parsed to a JSON array:\
\n\n\
{json.dumps(json.loads(letter_policy), separators=(',', ':'))}\
",
        response_format={
            "type": "json_object",
        },
    )

    return json.dumps(
        json.loads(
            response.text,
        ),
        indent=4,
    )


def extract_letter_subpolicies(letter_policy: str, subpolicy_boundaries: str) -> str:
    letter = json.loads(letter_policy)
    boundaries = json.loads(subpolicy_boundaries)["boundaries"]

    if not boundaries:
        return letter_policy

    subpolicies = []

    elements = []
    subpolicy_index = 0
    subpolicy_boundary = boundaries[subpolicy_index]["element_id"]
    for element in letter:
        elements += [element]
        if element["element_id"] == subpolicy_boundary:
            subpolicies += [
                {
                    "serial_number": boundaries[subpolicy_index]["serial_number"],
                    "heading": boundaries[subpolicy_index]["heading"],
                    "elements": elements,
                },
            ]
            elements = []
            subpolicy_index += 1
            if subpolicy_index >= len(boundaries):
                break
            subpolicy_boundary = boundaries[subpolicy_index]["element_id"]

    return json.dumps(subpolicies, indent=4)


def extract_subpolicy_texts(letter_subpolicies: str) -> str:
    subpolicies = json.loads(letter_subpolicies)

    subpolicy_texts = []

    for subpolicy in subpolicies:
        response = llm.complete(
            f"\
You are an expert at extracting the entire text of a single sub-policy extracted from a healthcare all plan letter containing a policy. \
You are given the relevant elements of this sub-policy in the form of a JSON array. \
Extract the entire text of this sub-policy. \
Output an object in JSON with the following keys: `serial_number`, `heading` and `text`. \
Capture the full heading of the sub-policy and do not shorten it. \
Extract all text for the sub-policy. \
Here is the sub-policy extracted from the all-plan letter in the format of a JSON object:\
\n\n\
{json.dumps(subpolicy, separators=(',', ':'))}\
\n\n\
Now extract all the text for this sub-policy.\
",
            response_format={
                "type": "json_object",
            },
        )

        policy_elememnt = json.loads(response.text)
        subpolicy_texts += [policy_elememnt]

    return json.dumps(subpolicy_texts, indent=4)


if __name__ == "__main__":
    import argparse
    from datetime import datetime
    from pathlib import Path

    cli = argparse.ArgumentParser()
    cli.add_argument("letter")
    args = cli.parse_args()
    letter_path = Path(args.letter)

    timestamp = datetime.now().isoformat("-", "seconds").replace(":", "-")

    if not letter_path.is_file():
        print("Specified all plan letter does not exist")
        raise SystemExit(1)
    elif letter_path.as_posix().endswith(".json"):
        print("Using specified parsed all plan letter")
        with open(letter_path, "r") as input:
            letter_parsed = input.read()
    elif Path(letter_path.as_posix() + ".json").is_file():
        print("Re-using parsed all plan letter")
        with open(letter_path.as_posix() + ".json", "r") as input:
            letter_parsed = input.read()
    else:
        print("Parsing all plan letter")
        with open(letter_path, "rb") as input:
            letter = input.read()
            letter_parsed = parse_with_unstructured(letter)
            with open(f"{letter_path.resolve()}.json", "w", encoding="utf-8") as output:
                output.write(letter_parsed)

    letter_parsed = restructure_parsed_letter(letter_parsed)
    with open(
        f"{letter_path.resolve()}_{timestamp}_1.json", "w", encoding="utf-8"
    ) as output:
        output.write(letter_parsed)

    policy_boundary = locate_policy_boundary(letter_parsed)
    with open(
        f"{letter_path.resolve()}_{timestamp}_2.json", "w", encoding="utf-8"
    ) as output:
        output.write(policy_boundary)

    letter_policy = extract_letter_policy(
        letter_parsed, json.loads(policy_boundary)["element_id"]
    )
    with open(
        f"{letter_path.resolve()}_{timestamp}_3.json", "w", encoding="utf-8"
    ) as output:
        output.write(letter_policy)

    subpolicy_boundaries = locate_subpolicy_boundaries(letter_policy)
    with open(
        f"{letter_path.resolve()}_{timestamp}_4.json", "w", encoding="utf-8"
    ) as output:
        output.write(subpolicy_boundaries)

    subpolicies = extract_letter_subpolicies(letter_policy, subpolicy_boundaries)
    with open(
        f"{letter_path.resolve()}_{timestamp}_5.json", "w", encoding="utf-8"
    ) as output:
        output.write(subpolicies)

    subpolicy_texts = extract_subpolicy_texts(subpolicies)
    with open(
        f"{letter_path.resolve()}_{timestamp}_6.json", "w", encoding="utf-8"
    ) as output:
        output.write(subpolicy_texts)
