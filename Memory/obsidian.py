import os

class ObsidianInterface:

    def __init__(self):
        self.vault_path = r"C:\Sentinel v0\Second_Brain\Local Brain"

    def read_obsidian_note(self, note_path: str):
        full_path = os.path.join(self.vault_path, note_path)
        if not full_path.endswith(".md"):
            full_path += ".md"
        try:
            with open(full_path, 'r', encoding='utf-8') as file:
                content = file.read()
                return content
        except FileNotFoundError:
            print(f"[ERROR] Could not read note at: {full_path}")
            return None
        except Exception as e:
            print(f"[ERROR] Unexpected error reading note: {str(e)}")
            return None


    def write_obsidian_note(self, note_path: str, content: str):
        full_path = os.path.join(self.vault_path, note_path)
        if not full_path.endswith(".md"):
            full_path += ".md"
        try:
            with open(full_path, 'a', encoding='utf-8') as file:
                file.write(content + "\n")
                return True
        except Exception as e:
            print(f"[ERROR] Unexpected error writing note: {str(e)}")
            return False

    def search_obsidian_note(self,keyword: str):
        matching_notes = []
        for root, dirs, files in os.walk(self.vault_path):
            for file_name in files:
                if file_name.endswith(".md"):
                    full_path = os.path.join(root, file_name)
                    try:
                        with open(full_path,'r', encoding="utf-8") as file:
                            content = file.read()
                        if keyword.lower() in content.lower():
                            relative_path = os.path.relpath(full_path, self.vault_path)
                            matching_notes.append(relative_path)
                    except Exception:
                        pass

        if (len(matching_notes) > 0):
            return matching_notes
        else:
            return f"Could not find '{keyword}' in the vault."