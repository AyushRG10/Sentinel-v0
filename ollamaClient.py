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
            You are Sentinel, a highly capable, autonomous, and professional personal AI assistant.
            
            When given a task, follow these steps strictly:
            1. THINK about the objective and what information or action is needed.
            2. To retrieve or write note data, choose the appropriate tool:
               - If you already know the exact filename (such as Welcome.md, Current_Context.md, Sentinel_Control_Center.md, or any specific memory note), call read_note or write_note DIRECTLY. Do NOT waste time searching for its filename first.
               - If you do not know the exact filename, use search_filenames to locate the file, or use search_notes to search for keywords within note content.
            3. Once you get the tool output, EVALUATE if you have enough information to fulfill the request.
            4. If more information is needed, call other tools. Repeat until you are fully prepared.
            5. Provide a complete, helpful, and correct response. Do NOT output raw JSON format in your final response to the user.
            6. At the end of every user-triggered task or interaction, you MUST update Current_Context.md (using write_note with overwrite=True) to summarize what you accomplished, your current understanding of the mission, and any future actions.
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
                    else:
                        res = "Tool not found."
                except Exception as e:
                    res = f"Error: {str(e)}"

                # Feed the tool result back to history, mapping to the specific function call name
                self.history.append({"role": "tool", "name": fn_name, "content": str(res)})
        
        # After the loop breaks, we have the final assistant response
        ai_message = response.message.content
        self.history.append({"role": "assistant", "content": ai_message})
        return ai_message