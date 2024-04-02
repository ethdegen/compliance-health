import json
import roman

from dotenv import load_dotenv

load_dotenv()


with open("src/ingest0.json", "rb") as ingest0:
    data = json.load(ingest0)

    # re-parent orphaned elements to their immediate ancestors' parents
    parents = set()
    for datum in data:
        parents.add(datum["element_id"])
    for i, datum in enumerate(data):
        if (
            "parent_id" in datum["metadata"]
            and datum["metadata"]["parent_id"] not in parents
        ):
            if datum["text"].split(" ")[0].endswith("."):
                roman_numeral_candidate = datum["text"].split(" ")[0]
                roman_numeral_candidate = roman_numeral_candidate[
                    0 : len(roman_numeral_candidate) - 1
                ]
                try:
                    roman.fromRoman(roman_numeral_candidate)
                    datum["type"] = "Title"
                    del datum["metadata"]["parent_id"]
                except roman.RomanError:
                    pass
            elif "parent_id" in data[i - 1]["metadata"]:
                datum["metadata"]["parent_id"] = data[i - 1]["metadata"]["parent_id"]
            else:
                del datum["metadata"]["parent_id"]

    with open("src/ingest1.json", "w", encoding="utf-8") as ingest1:
        json.dump(data, ingest1, ensure_ascii=False, indent=4)
