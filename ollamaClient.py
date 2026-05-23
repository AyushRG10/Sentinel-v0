import ollama
import os
from obsidianTools import ObsidianTools

class OllamaClient:
    def __init__(self):
        self.obsidian = ObsidianTools()
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
                            'note_name': {'type': 'string', 'description': 'The exact filename of the note. Not the path. Only say the name of the note, not the folder either.'}
                        },
                        'required': ['note_name'],
                    }
                }
            },
            {
                'type': 'function',
                'function': {
                    'name': 'write_note',
                    'description': 'Append or overwrite content in a note within the 02_Memories folder.',
                    'parameters': {
                        'type': 'object',
                        'properties': {
                            'note_name': {'type': 'string', 'description': 'The filename of the note'},
                            'content': {'type': 'string', 'description': 'The content to write'},
                            'overwrite': {'type': 'boolean', 'description': 'Set to True to clear existing content'}
                        },
                        'required': ['note_name', 'content']
                    }
                }
            }
        ]
        self.history = [{"role": "system", "content": """
            You are Sentinel. When given a task, follow these steps strictly:
            1. THINK about which tool is needed.
            2. If you need data, call the tool.
            3. Once you have the tool output, EVALUATE if you have enough information.
            4. If not, call another tool. 
            5. Provide a final response only when the information is complete.
            6. Read "Welcome.md" first and follow the instructions inside it. Always use the seach_filename tool before trying to read or write a file.
            7. In the Welcome.md file, there are other files mentioned. Read them too.
            8. Always include .md in the filename when calling the read_note tool.
            9. Never use json format. Whenever you do not know something, use the seach_notes tool.
        """}]

    def check_model(self) -> bool:
        try:
            ollama.list()
            return True
        except Exception:
            return False

    def generate(self, model_name: str, user_input: str) -> str:
        self.history.append({"role": "user", "content": user_input})

        # Loop until the model stops requesting tool calls
        while True:
            response = ollama.chat(
                model=model_name,
                messages=self.history,
                tools=self.tools
            )

            # If the model didn't request a tool, break the loop and return content
            if not response.message.tool_calls:
                break

            # Append the tool call to history so it knows what it asked for
            self.history.append(response.message)
            
            # Execute all requested tools
            for tool in response.message.tool_calls:
                fn_name = tool.function.name
                args = tool.function.arguments
                
                print(f"[Sentinel] Executing tool: {fn_name} with {args}")
                
                try:
                    if fn_name == 'search_filenames':
                        res = self.obsidian.search_filenames(args['keyword'])
                    elif fn_name == 'search_notes':
                        res = self.obsidian.search_notes(args['keyword'])
                    elif fn_name == 'read_note':
                        res = self.obsidian.read_note(args['note_name'])
                    elif fn_name == 'write_note':
                        res = self.obsidian.write_note(args['note_name'], args['content'], args.get('overwrite', False))
                        res = "Write successful."
                    else:
                        res = "Tool not found."
                except Exception as e:
                    res = f"Error: {str(e)}"

                # Feed the tool result back to history
                self.history.append({"role": "tool", "content": str(res)})
        
        # After the loop breaks, we have the final assistant response
        ai_message = response.message.content
        self.history.append({"role": "response", "content": ai_message})
        return ai_message