import json
import os
import openai
from llama_index.llms.openai import OpenAI
from unstructured_client import UnstructuredClient
from unstructured_client.models import shared
from dotenv import load_dotenv

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


def generate_summary_breakdown(letter_parsed: str) -> str:
    response = llm.complete(
        f"\
You are an expert at extracting a summary breakdown of all policy elements from a healthcare all plan letter containing a policy. \
You are given this letter in the form of a JSON array. \
This letter may contain one or more policy elements. \
If the letter contains multiple policy elements, each policy element usually has a heading numbered with a roman numeral. \
If the letter only contains a single policy element, then only include that single policy element. \
Some policy elements may include sub-elements, each of which usually starts with a numbered heading. \
Whenever you see sub-elements of a policy element, always consider them fully as part of the policy element. \
Note that page number headers in the letter are at the start of each page. Extract a breakdown of all the policy elements in the letter. \
Ensure that every policy element is extracted fully and entirely. \
Continue extracting every policy element until way past its end and then look back to ensure you have correctly identified its end. \
For every policy element, include all portions of its sub-elements and their headings. \
Look out for footnotes, which are generally prefixed with running numbers and appear at the end of a page. \
Whenever you encounter a footnote, continue reading past it because the policy element probably continues. \
Output an object of `policy_elements` in JSON, containing an array with each element representing summary data pertaining to a single policy element. \
Include all policy elements in your output. \
For each policy element, always include all sub-elements. \
Every policy element object must have the following keys: `serial_number`, `heading`, `page_numbers` and `boundary_reasoning`. \
Use standard integers for the policy element serial numbers and ensure that serial numbering begins at 1. \
Capture full headings of every policy element and do not shorten them. \
Include every page number for which any part of the policy element appears. \
In your boundary reasonings, explain why you are sure the respective policy element starts and ends on the page numbers you have included. \
Ensure that you have extracted ALL the policy elements from the letter. \
Finally, go back and extract the policy element summary breakdown again to ensure that you have included all policy elements fully and correctly.\
\n\n\
Here is the all plan letter parsed to a JSON array:\
\n\n\
{json.dumps(json.loads(letter_parsed), separators=(',', ':'))}\
",
        response_format={
            "type": "json_object",
        },
    )

    return response.text


def generate_policy_elements(letter_parsed: str, summary_breakdown: str) -> str:
    letter = json.loads(letter_parsed)
    summary = json.loads(summary_breakdown)["policy_elements"]

    summary_extract = [
        {
            "serial_number": element["serial_number"],
            "heading": element["heading"],
            "boundary_reasoning": element["boundary_reasoning"],
        }
        for element in summary
    ]

    policy_elements = []

    for i in range(len(summary)):
        page_numbers = summary[i]["page_numbers"] + [
            max(summary[i]["page_numbers"]) + 1
        ]  # summary breakdown sometimes misses final page
        letter_extract = [
            {
                "text": paragraph["text"],
                "type": paragraph["type"],
                "element_id": paragraph["element_id"],
                "parent_id": paragraph["parent_id"],
            }
            for paragraph in letter
            if (paragraph["page_number"] in page_numbers)
        ]

        serial_number = i + 1

        response = llm.complete(
            f"\
You are an expert at extracting the entirety of a single policy element from a healthcare all plan letter containing a policy. \
You are given the relevant pages of this letter in the form of a JSON array. \
This letter may contain one or more policy elements. \
If it contains multiple policy elements, each policy element usually has a heading numbered with a roman numeral. \
Some policy elements may include sub-elements, each of which usually starts with a numbered heading. \
Whenever you see sub-elements of a policy element, always consider them fully as part of the policy element. \
Note that page number headers in the letter are at the start of each page. \
You are also given a breakdown of the policy elements in JSON format. \
Extract the policy element with serial number {serial_number} from the letter using the provided breakdown as a guide. \
When extracting text, look out for footnote references. \
Every time you encounter a numeric reference to a footnote, look up the footnote itself and extract it to the footnotes field of the output. \
Footnotes themselves are generally prefixed with running numbers and appear at the end of the page where they are referenced. \
Keep extracting the policy element until you are absolutely sure you have extracted all of it including all its sub-elements! \
Output an object in JSON. \
Your extracted policy element object must have the following keys: `serial_number`, `heading`, `text` and `footnotes`. \
Use standard integers for the policy element serial number. \
Capture the full heading of the extracted policy element and do not shorten it. \
Extract all text from all list items and narratives that share parent IDs with other policy element texts. \
Include all policy element and sub-element headings as part of the extracted text. \
Make sure you do not miss any final text at the end! \
The footnotes field should be a map of numeric keys to their respective footnote texts. \
Now, go back and extract the policy element again to ensure that you have extracted it and its sub-elements fully and correctly.\
\n\n\
Here are the relevant pages of the all plan letter parsed to a JSON array:\
\n\n\
{json.dumps(letter_extract, separators=(',', ':'))}\
\n\n\
And here is the breakdown of policy elements in JSON format:\
\n\n\
{json.dumps(summary_extract, separators=(',', ':'))}\
\n\n\
Now extract the policy element with serial number {serial_number} COMPLETELY!\
",
            response_format={
                "type": "json_object",
            },
        )

        policy_elememnt = json.loads(response.text)
        policy_elements += [policy_elememnt]

    return json.dumps(policy_elements, indent=4)


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

    summary_breakdown = generate_summary_breakdown(letter_parsed)
    with open(
        f"{letter_path.resolve()}_{timestamp}_2.json", "w", encoding="utf-8"
    ) as output:
        output.write(summary_breakdown)

    policy_elements = generate_policy_elements(letter_parsed, summary_breakdown)
    with open(
        f"{letter_path.resolve()}_{timestamp}_3.json", "w", encoding="utf-8"
    ) as output:
        output.write(policy_elements)
