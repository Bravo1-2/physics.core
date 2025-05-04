import re
import json
import os

def parse_markdown(md_content: str) -> dict:
    """Parse markdown content into a structured JSON format."""
    structured_data = {"Chapters": []}
    current_chapter = None
    current_topic = None
    current_subtopic = None

    for line in md_content.split("\n"):
        line = line.strip()

        # -------- Header Detection --------
        # Chapter detection (e.g., "# [Chapter] Motion")
        if re.match(r"^# \[Chapter\]", line):
            current_chapter = {
                "title": re.sub(r"^# \[Chapter\] ", "", line).strip(),
                "topics": []
            }
            structured_data["Chapters"].append(current_chapter)
            current_topic = None
            current_subtopic = None

        # Topic detection (e.g., "## [Topic] Introduction")
        elif re.match(r"^## \[Topic\]", line) and current_chapter:
            current_topic = {
                "title": re.sub(r"^## \[Topic\] ", "", line).strip(),
                "content": [],
                "subtopics": []
            }
            current_chapter["topics"].append(current_topic)
            current_subtopic = None

        # Subtopic detection (e.g., "### [Subtopic] Distance")
        elif re.match(r"^### \[Subtopic\]", line) and current_topic:
            current_subtopic = {
                "title": re.sub(r"^### \[Subtopic\] ", "", line).strip(),
                "content": []
            }
            current_topic["subtopics"].append(current_subtopic)

        # -------- Content Detection --------
        # Bullet points (e.g., "- [Definition] ...")
        elif line.startswith("- [") and (current_topic or current_subtopic):
            match = re.match(r"- \[(.*?)\] (.*)", line)
            if match:
                entry = {
                    "type": match.group(1).lower(),
                    "text": match.group(2).strip()
                }
                if current_subtopic:
                    current_subtopic["content"].append(entry)
                else:
                    current_topic["content"].append(entry)

        # Plain text lines
        elif line and (current_topic or current_subtopic):
            entry = {"type": "text", "text": line}
            if current_subtopic:
                current_subtopic["content"].append(entry)
            else:
                current_topic["content"].append(entry)

    return structured_data

def save_to_downloads(data: dict, filename: str) -> None:
    """Save JSON file to Mac Downloads folder."""
    downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
    filepath = os.path.join(downloads_path, filename)
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    
    print(f"\n✅ File saved to: {filepath}")

if __name__ == "__main__":
    # Get input file path
    md_file = input("Enter path to your markdown file: ").strip()
    
    try:
        with open(md_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Parse and save
        parsed_data = parse_markdown(content)
        save_to_downloads(parsed_data, "physics_notes.json")
        
    except FileNotFoundError:
        print(f"❌ Error: File not found at {md_file}")
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
