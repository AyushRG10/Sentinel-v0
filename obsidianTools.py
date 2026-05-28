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

        # Normalize overwrite parameter if it's passed as a string
        if isinstance(overwrite, str):
            overwrite = overwrite.lower() in ("true", "1", "yes")

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

        # If appending, ensure we start on a new line if the file doesn't end with one
        if not overwrite and os.path.exists(target_path) and os.path.getsize(target_path) > 0:
            try:
                with open(target_path, "r", encoding="utf-8") as f:
                    last_char = f.read()[-1:]
                if last_char and last_char != "\n":
                    content = "\n" + content
            except Exception:
                pass

        mode = "w" if overwrite else "a"
        with open(target_path, mode, encoding="utf-8") as f:
            f.write(content + "\n")
            
        return f"Successfully wrote to {os.path.relpath(target_path, self.vault_path)}"

    def get_vault_structure(self) -> str:
        """Returns a string representation of the vault's directories and markdown files."""
        folders = []
        notes = []
        for root, dirs, files in os.walk(self.vault_path):
            # Exclude hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            for d in dirs:
                rel_dir = os.path.relpath(os.path.join(root, d), self.vault_path)
                folders.append(rel_dir)
            for f in files:
                if f.endswith(".md"):
                    rel_file = os.path.relpath(os.path.join(root, f), self.vault_path)
                    notes.append(rel_file)
        
        # Format the output beautifully
        output = "Available Folders inside Vault:\n"
        if folders:
            for folder in sorted(folders):
                output += f"- {folder}/\n"
        else:
            output += "- (None)\n"
            
        output += "\nExisting Markdown Notes in Vault:\n"
        if notes:
            for note in sorted(notes):
                output += f"- {note}\n"
        else:
            output += "- (None)\n"
            
        return output

    def note_exists(self, note_name: str) -> bool:
        """Checks if a note exists anywhere in the vault (either directly or recursively)."""
        if not note_name:
            return False
            
        if not note_name.lower().endswith(".md"):
            note_name_md = note_name + ".md"
        else:
            note_name_md = note_name

        # 1. Try exact match relative to vault root
        direct_path = os.path.join(self.vault_path, note_name_md)
        if os.path.exists(direct_path) and os.path.isfile(direct_path):
            return True

        # 2. Try recursive search for the base name with normalization
        base_name_norm = self._normalize_name(os.path.basename(note_name_md))
        for root, dirs, files in os.walk(self.vault_path):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            for file in files:
                if self._normalize_name(file) == base_name_norm:
                    return True
                    
        return False

    def delete_note(self, note_name: str) -> str:
        """
        Permanently deletes a note from the vault.
        Uses the same multi-step path resolution as read_note.
        Returns a success message or an error string.
        """
        if not note_name:
            return "Error: note_name cannot be empty."

        # Safety guard: protect critical system notes
        PROTECTED_NOTES = {"current context", "sentinel control center", "welcome"}
        if self._normalize_name(os.path.basename(note_name)) in PROTECTED_NOTES:
            return f"Error: '{note_name}' is a protected system note and cannot be deleted."

        # Standardize .md extension
        if not note_name.lower().endswith(".md"):
            note_name_md = note_name + ".md"
        else:
            note_name_md = note_name

        target_path = None

        # 1. Exact match relative to vault root
        direct_path = os.path.join(self.vault_path, note_name_md)
        if os.path.exists(direct_path) and os.path.isfile(direct_path):
            target_path = direct_path

        # 2. Recursive normalized search
        if not target_path:
            base_name_norm = self._normalize_name(os.path.basename(note_name_md))
            for root, dirs, files in os.walk(self.vault_path):
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                for file in files:
                    if self._normalize_name(file) == base_name_norm:
                        target_path = os.path.join(root, file)
                        break
                if target_path:
                    break

        # 3. Raw fallback
        if not target_path:
            raw_path = os.path.join(self.vault_path, note_name)
            if os.path.exists(raw_path) and os.path.isfile(raw_path):
                target_path = raw_path

        if not target_path:
            return f"Error: Note '{note_name}' not found in the vault."

        try:
            os.remove(target_path)
            rel_path = os.path.relpath(target_path, self.vault_path)
            return f"Successfully deleted '{rel_path}'."
        except Exception as e:
            return f"Error deleting '{note_name}': {str(e)}"