import re
import json
from typing import Dict, List
from dataExtractor import read_markdown_file # Importing the function from dataExtractor.py

def parse_markdown(md_content):
    # Parses Markdown content into a structured JSON format
    structured_data = {"Chapters": []}
    current_chapter = None
    current_topic = None

    lines = md_content.split("\n")

    for line in lines:
        line = line.strip()

        if line.startswith("[Chapter]"):
            current_chapter = {"title" : line.replace("[Chapter]", "").strip(), "topics": []}
            structured_data["Chapters"].append(current_chapter)

        elif line.startswith("[Topic]") and current_chapter is not None:
            current_topic = {"title": line.replace("[Topic]", "").strip(), "content": []}
            current_chapter["topics"].append(current_topic)

        elif any(tag in line for tag in ["[Definition]", "[Formula]", "[Example]"]) and current_topic is not None:
            match = re.match(r"\[.*?]", line)
            if match:
                tag, content = match.groups()
                current_topic["content"].append({"type": tag, "text": content.strip()})

        elif line and current_topic is not None:
            current_topic["content"].append({"type": "Text", "text": line})

    return structured_data

def write_json(file_path: str, data: Dict[str, List[Dict[str, str]]]) -> None:
    # Writes the structured data to a JSON file
    with open(file_path, "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, indent=4, ensure_ascii=False)
    print(f"JSON data successfully written to {file_path}")

if __name__ == "__main__":
    md_path = input("Enter the path to the Markdown file: ")
    md_content = read_markdown_file(md_path) # Use imported function

    structured_data = parse_markdown(md_content)

    if structured_data["Chapters"]:
        write_json("structured_data.json", structured_data)
    else:
        print("Error: No data extracted from the Markdown file!")
