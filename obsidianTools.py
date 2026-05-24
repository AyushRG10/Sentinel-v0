import os

class ObsidianTools:
    def __init__(self, writable_folder: str = ""):
        """
        vault_path: Path to your Sentinel Vault.
        writable_folder: Optional subfolder within the vault where Sentinel is allowed to write/modify notes.
        """
        base_dir = os.path.dirname(os.path.abspath(__file__))
        vault_path = os.path.join(base_dir, "informationVault") 
        self.vault_path = os.path.expanduser(vault_path)
        
        # If writable_folder is "informationVault" or empty, default to the entire vault path.
        # Otherwise, point to the specific subfolder inside the vault.
        if writable_folder and writable_folder != "informationVault":
            self.writable_folder = os.path.join(self.vault_path, writable_folder)
        else:
            self.writable_folder = self.vault_path

    def _normalize_name(self, name: str) -> str:
        """Helper to normalize filename for matching (removes extension, lowers, converts underscores/hyphens to spaces)."""
        if not name:
            return ""
        name_clean = name.lower()
        if name_clean.endswith(".md"):
            name_clean = name_clean[:-3]
        return name_clean.replace("_", " ").replace("-", " ").strip()

    def search_notes(self, keyword: str):
        """Reads from EVERY file in the vault, including your personal thoughts."""
        results = []
        for root, dirs, files in os.walk(self.vault_path):
            # Exclude hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            for file in files:
                if file.endswith(".md"):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            if keyword.lower() in f.read().lower():
                                results.append(file)
                    except Exception:
                        pass
        return results

    def search_filenames(self, keyword: str):
        """Searches for a keyword in the filenames of the vault."""
        results = []
        for root, dirs, files in os.walk(self.vault_path):
            # Exclude hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            for file in files:
                if keyword.lower() in file.lower() and file.endswith(".md"):
                    results.append(file)
        return results

    def read_note(self, note_name: str):
        """Reads note from the vault, supporting robust resolution of filename/paths."""
        if not note_name:
            return None
            
        # Standardize .md extension
        if not note_name.lower().endswith(".md"):
            note_name_md = note_name + ".md"
        else:
            note_name_md = note_name

        # 1. Try exact match relative to vault root
        direct_path = os.path.join(self.vault_path, note_name_md)
        if os.path.exists(direct_path) and os.path.isfile(direct_path):
            with open(direct_path, "r", encoding="utf-8") as f:
                return f.read()

        # 2. Try recursive search for the base name with normalization
        base_name_norm = self._normalize_name(os.path.basename(note_name_md))
        for root, dirs, files in os.walk(self.vault_path):
            # Exclude hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            for file in files:
                if self._normalize_name(file) == base_name_norm:
                    with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                        return f.read()

        # 3. Fallback: try raw input directly
        direct_path_raw = os.path.join(self.vault_path, note_name)
        if os.path.exists(direct_path_raw) and os.path.isfile(direct_path_raw):
            with open(direct_path_raw, "r", encoding="utf-8") as f:
                return f.read()

        base_name_raw_norm = self._normalize_name(os.path.basename(note_name))
        for root, dirs, files in os.walk(self.vault_path):
            # Exclude hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            for file in files:
                if self._normalize_name(file) == base_name_raw_norm:
                    with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                        return f.read()

        return None

    def write_note(self, note_name: str, content: str, overwrite: bool = False):
        """
        Writes content to a note. If the note exists, modifies it.
        If it does not exist, creates it with sensible folder defaults.
        """
        if not note_name:
            raise ValueError("note_name cannot be empty")

        # Standardize .md extension
        if not note_name.lower().endswith(".md"):
            note_name_md = note_name + ".md"
        else:
            note_name_md = note_name

        target_path = None

        # 1. Check if the file already exists directly or recursively in the writable folder/vault
        direct_path = os.path.join(self.writable_folder, note_name_md)
        if os.path.exists(direct_path) and os.path.isfile(direct_path):
            target_path = direct_path
        else:
            base_name_norm = self._normalize_name(os.path.basename(note_name_md))
            for root, dirs, files in os.walk(self.writable_folder):
                # Exclude hidden directories
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                found = False
                for file in files:
                    if self._normalize_name(file) == base_name_norm:
                        target_path = os.path.join(root, file)
                        found = True
                        break
                if found:
                    break

        # 2. If it does not exist, determine creation path
        if not target_path:
            # If the user passed a relative subfolder path, preserve it
            if "/" in note_name_md or "\\" in note_name_md:
                target_path = os.path.join(self.writable_folder, note_name_md)
            else:
                # Default to memories or topics depending on keyword
                base_name = os.path.basename(note_name_md)
                if "topic" in base_name.lower():
                    target_path = os.path.join(self.writable_folder, "topics", base_name)
                else:
                    target_path = os.path.join(self.writable_folder, "memories", base_name)

        # Create directory if it does not exist
        os.makedirs(os.path.dirname(target_path), exist_ok=True)

        mode = "w" if overwrite else "a"
        with open(target_path, mode, encoding="utf-8") as f:
            f.write(content + "\n")
            
        return f"Successfully wrote to {os.path.relpath(target_path, self.vault_path)}"