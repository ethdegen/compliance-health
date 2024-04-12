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

with open("src/apl_1_1/ingest0.json", "r") as ingest0:
    context = json.loads(ingest0.read())
    letter = [
        {
            "page_number": clause["page_number"],
            "type": clause["type"],
            "element_id": clause["element_id"],
            "parent_id": clause["parent_id"],
            "text": clause["text"],
        }
        for clause in context
    ]

    response = llm.complete(
        f""""You are an expert at extracting a summary breakdown of all policy elements from a healthcare all plan letter containing a policy. You are given this letter in the form of a JSON array. This letter may contain one or more policy elements. If it contains multiple policy elements, each policy element usually has a heading numbered with a roman numeral. Some policy elements may include sub-elements, each of which usually starts with a numbered heading. Whenever you see sub-elements of a policy element, always consider them fully as part of the policy element. Note that page number headers in the letter are at the start of each page. Extract a breakdown of all the policy elements in the letter. Ensure that every policy element is extracted fully and entirely. Continue extracting every policy element until way past its end and then look back to ensure you have correctly identified its end. For every policy element, include all portions of its sub-elements and their headings. Look out for footnotes, which are generally prefixed with running numbers and appear at the end of a page. Whenever you encounter a footnote, continue reading past it because the policy element probably continues. Output an object of `policy_elements` in JSON, containing an array with each element representing summary data pertaining to a single policy element. Include all policy elements in your output. For each policy element, always include all sub-elements. Every policy element object must have the following keys: `serial_number`, `heading`, `final_sentence_reasoning` and `page_numbers`. Use standard integers for the policy element serial numbers and ensure that serial numbering begins at 1. Capture full headings of every policy element and do not shorten them. In your final sentence reasonings, cite the final sentence of the respective policy element and why you are sure this sentence is final for the policy element. Include every page number for which any part of the policy element appears and all page numbers cited in your final sentence reasoning. Ensure that you have extracted ALL the policy elements from the letter. Finally, go back and extract the policy element summary breakdown again to ensure that you have included all policy elements fully and correctly.
 
Here is the all plan letter parsed to a JSON array:
        
{json.dumps(letter, separators=(",", ":"))}""",
        response_format={
            "type": "json_object",
        },
    )

    with open("src/apl_1_1/ingest1.json", "w", encoding="utf-8") as output:
        output.write(response.text)
