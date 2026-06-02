# pyrefly: ignore [missing-import]
import ollama
from ollamaTools import OllamaTools

class OllamaClient:
    def __init__(self):
        self.ollama_tools = OllamaTools()
        self.obsidian = self.ollama_tools.obsidian
        self.read_notes_tracker = set()
        self.tools = self.ollama_tools.tools
        self.history = [{"role": "system", "content": f"""
            You are Sentinel, a highly capable, autonomous, and professional personal AI assistant.
            
            CRITICAL ENFORCEMENT: 
            - You are an agent equipped with tool-calling capabilities. To read, search, create, modify, append to, or overwrite any note/file (including Current_Context.md, Sentinel_Control_Center.md, Summer_Plans.md, or any other note), you MUST call the corresponding tool (e.g., 'read_note', 'write_note').
            - Merely outputting markdown code blocks, writing text like "Updating note...", or statements like "Write_note: memories/Current_Context.md" in your final text response does NOT save or write anything to disk. 
            - You MUST explicitly trigger the tool call first. Once the tool executes and you receive the tool success/failure feedback in your context, you can then summarize what you did in your final text response. Never describe an action or claim a file is updated without having successfully executed the tool call.
            - **Overwrite Guardrail**: To overwrite any existing user note (using overwrite=True), you MUST first read the note using 'read_note' in the current session. If you attempt to overwrite an existing note without reading it first, the tool will return a safety error to enforce context preservation. Always read existing notes before replacing them to merge new information cleanly.
            
            Vault Structure and Existing Notes on Boot:
            {self.obsidian.get_vault_structure()}
            
            When given a task, follow these steps strictly:
            1. THINK about the objective and what information or action is needed.
            2. To retrieve or write note data, choose the appropriate tool:
               - If you already know the exact filename (such as Welcome.md, Current_Context.md, Sentinel_Control_Center.md, or any specific memory note), call read_note or write_note DIRECTLY. Do NOT waste time searching for its filename first.
               - If you do not know the exact filename, use search_filenames to locate the file, or use search_notes to search for keywords within note content.
            3. When creating or writing a note, you MUST specify the correct relative folder path (e.g. "inbox/my_note.md" or "memories/my_note.md" or "topics/my_note.md") to ensure files are placed in their proper folders. Available folders for files are: inbox, memories, topics, operations, directives. Avoid writing files to the root of the vault unless explicitly requested.
            4. When modifying, updating, or adding to an existing note:
               - If you simply want to append a new entry, log, or quick thought to the end of a note, call write_note with overwrite=False.
               - If you need to edit specific sections, restructure, or neatly insert information inside an existing note (e.g. modifying the Summer_Plans or a topic note under specific headers), you MUST first read the note using read_note, perform the edit/merge in your context, and then call write_note with overwrite=True to completely overwrite the file with your cleanly updated version. This prevents duplication and maintains proper note formatting.
            5. Once you get the tool output, EVALUATE if you have enough information to fulfill the request.
            6. If more information is needed, call other tools. Repeat until you are fully prepared.
            7. Provide a complete, helpful, and correct response. Do NOT output raw JSON format in your final response to the user.
            8. At the end of every user-triggered task or interaction, you MUST update Current_Context.md (using write_note with overwrite=True) to summarize what you accomplished, your current understanding of the mission, and any future actions.
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
                
                print(f"Sentinel [TOOL]: {fn_name} | args: {args}")
                
                try:
                    res = self.ollama_tools.execute_tool(fn_name, args, self.read_notes_tracker)
                except Exception as e:
                    res = f"Error: {str(e)}"

                # Feed the tool result back to history, mapping to the specific function call name
                self.history.append({"role": "tool", "name": fn_name, "content": str(res)})
        
        # After the loop breaks, we have the final assistant response
        ai_message = response.message.content
        self.history.append({"role": "assistant", "content": ai_message})
        return ai_message