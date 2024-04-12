import json
import os
import openai

from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.environ["OPENAI_API_KEY"]

from llama_index.llms.openai import OpenAI

llm = OpenAI(
    model="gpt-4-turbo",
    temperature=0,
    max_tokens=4096,
    timeout=600,
)

with open("src/apl_0_1/ingest0.json", "r") as ingest0:
    with open("src/apl_0_1/ingest1.json", "r") as ingest1:
        letter = json.loads(ingest0.read())
        breakdown = json.loads(ingest1.read())["policy_elements"]

        policy_elements = []

        for i in range(len(breakdown)):
            serial_number = i + 1
            letter_extract = [
                {
                    "type": clause["type"],
                    "element_id": clause["element_id"],
                    "text": clause["text"],
                    "parent_id": clause["parent_id"],
                }
                for clause in letter
                if clause["page_number"] in breakdown[i]["page_numbers"]
            ]

            response = llm.complete(
                f""""You are an expert at extracting the entirety of a single policy element from a healthcare all plan letter containing a policy. You are given the relevant pages of this letter in the form of a JSON array. This letter may contain one or more policy elements. If it contains multiple policy elements, each policy element usually has a heading numbered with a roman numeral. Some policy elements may include sub-elements, each of which usually starts with a numbered heading. Whenever you see sub-elements of a policy element, always consider them fully as part of the policy element. Note that page number headers in the letter are at the start of each page. You are also given a breakdown of the policy elements in JSON format. Extract the policy element with serial number {serial_number} from the letter using the provided breakdown as a guide. When extracting text, look out for footnote references. Every time you encounter a numeric reference to a footnote, look up the footnote itself and extract it to the footnotes field of the output. Footnotes themselves are generally prefixed with running numbers and appear at the end of the page where they are referenced. Keep extracting the policy element until you are absolutely sure you have extracted all of it including all its sub-elements! Output an object in JSON. Your extracted policy element object must have the following keys: `serial_number`, `heading`, `text` and `footnotes`. Use standard integers for the policy element serial number. Capture the full heading of the extracted policy element and do not shorten it. Extract all text from all list items and narratives that share parent IDs with other policy element texts. Include all policy element and sub-element headings as part of the extracted text. Make sure you do not miss any final text at the end! The footnotes field should be a map of numeric keys to their respective footnote texts. Now, go back and extract the policy element again to ensure that you have extracted it and its sub-elements fully and correctly.

Here are the relevant pages of the all plan letter parsed to a JSON array:
                
{json.dumps(letter_extract, separators=(',', ':'))}

And here is the breakdown of policy elements in JSON format:
                
{json.dumps(breakdown, separators=(',', ':'))}

Now extract the policy element with serial number {serial_number} COMPLETELY!""",
                response_format={
                    "type": "json_object",
                },
            )
            print(response.text)
            policy_elements += [json.loads(response.text)]

        with open("src/apl_0_1/ingest2.json", "w", encoding="utf-8") as output:
            json.dump(policy_elements, output, ensure_ascii=False, indent=4)
