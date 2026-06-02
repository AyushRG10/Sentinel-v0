import os
from obsidianTools import ObsidianTools
from geminiClient import OnlineLLMsClient

class OllamaTools:
    def __init__(self):
        self.obsidian = ObsidianTools()
        try:
            self.gemini = OnlineLLMsClient()
        except Exception as e:
            print(f"Sentinel [WARNING]: Failed to initialize OnlineLLMsClient: {e}")
            self.gemini = None

        self.tools = [
            {
                'type': 'function',
                'function': {
                    'name': 'search_filenames',
                    'description': 'Search for files by matching a keyword in the filename.',
                    'parameters': {
                        'type': 'object',
                        'properties': {
                            'keyword': {'type': 'string', 'description': 'The keyword to look for in filenames.'}
                        },
                        'required': ['keyword']
                    }
                }
            },
            {
                'type': 'function',
                'function': {
                    'name': 'search_notes',
                    'description': 'Search for files by searching for a keyword within the content of all notes.',
                    'parameters': {
                        'type': 'object',
                        'properties': {
                            'keyword': {'type': 'string', 'description': 'The keyword to look for in file content'}
                        },
                        'required': ['keyword']
                    }
                }
            },
            {
                'type': 'function',
                'function': {
                    'name': 'read_note',
                    'description': 'Read the content of a specific markdown file.',
                    'parameters': {
                        'type': 'object',
                        'properties': {
                            'note_name': {'type': 'string', 'description': 'The filename or path of the note relative to the vault root (e.g., "my_note.md" or "inbox/my_note.md").'}
                        },
                        'required': ['note_name'],
                    }
                }
            },
            {
                'type': 'function',
                'function': {
                    'name': 'write_note',
                    'description': 'Write content to a note. MUST be used whenever you need to create, update, edit, modify, append to, or overwrite any note or file in the vault.',
                    'parameters': {
                        'type': 'object',
                        'properties': {
                            'note_name': {'type': 'string', 'description': 'The filename or relative path of the note from the vault root (e.g., "my_note.md" or "inbox/my_note.md"). Specifying the relative path is highly recommended to place it in the correct folder.'},
                            'content': {'type': 'string', 'description': 'The content to write to the note'},
                            'overwrite': {'type': 'boolean', 'description': 'Set to True to completely replace/overwrite the existing note with your new content. Set to False (default) to append your new content to the end of the note without losing existing content.'}
                        },
                        'required': ['note_name', 'content']
                    }
                }
            },
            {
                'type': 'function',
                'function': {
                    'name': 'delete_note',
                    'description': 'Permanently delete a note from the vault by filename or relative path. Protected system notes (Current_Context, Sentinel_Control_Center, Welcome) cannot be deleted.',
                    'parameters': {
                        'type': 'object',
                        'properties': {
                            'note_name': {'type': 'string', 'description': 'The filename or relative path of the note to delete (e.g., "memories/old_note.md").'}
                        },
                        'required': ['note_name']
                    }
                }
            },
            {
                'type': 'function',
                'function': {
                    'name': 'gemini_generate',
                    'description': 'Generate a response or search online using Gemini. Useful for looking up web information or general knowledge beyond the local vault.',
                    'parameters': {
                        'type': 'object',
                        'properties': {
                            'prompt': {'type': 'string', 'description': 'The prompt to send to Gemini.'},
                            'system_instruction': {'type': 'string', 'description': 'Optional system instruction to guide Gemini.'},
                            'use_grounding': {'type': 'boolean', 'description': 'Set to True (default) to enable Google Search grounding for online/live information, or False for standard generation.'}
                        },
                        'required': ['prompt']
                    }
                }
            }
        ]

    def execute_tool(self, name, args, read_notes_tracker):
        if name == 'search_filenames':
            return self.obsidian.search_filenames(args['keyword'])
        elif name == 'search_notes':
            return self.obsidian.search_notes(args['keyword'])
        elif name == 'read_note':
            res = self.obsidian.read_note(args['note_name'])
            if res:
                norm_base = self.obsidian._normalize_name(os.path.basename(args['note_name']))
                read_notes_tracker.add(norm_base)
            return res
        elif name == 'write_note':
            note_name = args['note_name']
            overwrite = args.get('overwrite', False)
            if isinstance(overwrite, str):
                overwrite = overwrite.lower() in ("true", "1", "yes")
            
            norm_base = self.obsidian._normalize_name(os.path.basename(note_name))
            note_exists = self.obsidian.note_exists(note_name)
            is_system_note = "current context" in norm_base or "sentinel control center" in norm_base
            
            if overwrite and note_exists and not is_system_note and norm_base not in read_notes_tracker:
                return f"Error: You are trying to overwrite existing note '{note_name}' using overwrite=True, but you have NOT read this note's content in this session yet. To prevent losing user context, you MUST first read the note using 'read_note' to retrieve its current content, merge your changes in your context, and then write the full merged note using 'write_note' with overwrite=True."
            else:
                return self.obsidian.write_note(note_name, args['content'], overwrite)
        elif name == 'delete_note':
            return self.obsidian.delete_note(args['note_name'])
        elif name == 'gemini_generate':
            if not self.gemini:
                return "Error: Gemini client not initialized."
            prompt = args['prompt']
            system_instruction = args.get('system_instruction', '')
            use_grounding = args.get('use_grounding', True)
            if isinstance(use_grounding, str):
                use_grounding = use_grounding.lower() in ("true", "1", "yes")
            return self.gemini.generate_response(prompt, system_instruction, use_grounding)
        else:
            raise ValueError(f"Tool {name} not found.")
