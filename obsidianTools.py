import os

class ObsidianTools:
    def __init__(self, writable_folder: str = "informationVault"):
        """
        vault_path: Path to your Sentinel Vault.
        writable_folder: The folder name where Sentinel is allowed to write/modify notes.
        """
        base_dir = os.path.dirname(os.path.abspath(__file__))
        vault_path = os.path.join(base_dir, "informationVault") 
        self.vault_path = os.path.expanduser(vault_path)
        self.writable_folder = os.path.join(self.vault_path, writable_folder)

    def search_notes(self, keyword: str):
        """Reads from EVERY file in the vault, including your personal thoughts."""
        results = []
        for root, _, files in os.walk(self.vault_path):
            for file in files:
                if file.endswith(".md"):
                    file_path = os.path.join(root, file)
                    with open(file_path, "r", encoding="utf-8") as f:
                        if keyword.lower() in f.read().lower():
                            results.append(file_path)
        return results

    def search_filenames(self, keyword: str):
        """Searches for a keyword in the filenames of the vault."""
        results = []
        for root, _, files in os.walk(self.vault_path):
            for file in files:
                if keyword.lower() in file.lower() and file.endswith(".md"):
                    file_path = os.path.join(root, file)
                    results.append(file_path)
        return results

    def read_note(self, note_name: str):
        """Reads from EVERY file in the vault."""
        for root, _, files in os.walk(self.vault_path):
            if note_name in files:
                with open(os.path.join(root, note_name), "r", encoding="utf-8") as f:
                    return f.read()
        return None

    def write_note(self, note_name: str, content: str, overwrite: bool = False):
        """
        Writes ONLY if the file exists and is located within the writable_folder.
        Otherwise, throws an FileNotFoundError.
        """
        target_path = None
        
        # Look for the file ONLY within the writable_folder
        for root, _, files in os.walk(self.writable_folder):
            if note_name in files:
                target_path = os.path.join(root, note_name)
                break
        
        # If the file wasn't found in the writable area, raise an error
        if not target_path:
            raise FileNotFoundError(f"Access Denied or File Not Found: '{note_name}' must exist in {self.writable_folder}")

        mode = "w" if overwrite else "a"
        with open(target_path, mode, encoding="utf-8") as f:
            f.write(content + "\n")