from ollamaClient import OllamaClient
from killSwitch import KillSwitch
import time
import datetime

class MainLoop:
    def __init__(self):
        self.client = OllamaClient()
        self.killSwitch = KillSwitch()
        self.killSwitch.arm()

        self.runMainLoop = True
        self.tries = 3

        if self.client.check_model():
            self.initialize_sentinel()
            
        while self.runMainLoop:
            isClientActive = self.client.check_model()
            if isClientActive:
                if self.tries != 0:
                    print("Sentinel: [INFO] Client is online.")
                    self.tries = 0
                
                try:
                    prompt = input("User: ").strip()
                except (KeyboardInterrupt, EOFError):
                    print("\nSentinel: [INFO] Exiting.")
                    self.runMainLoop = False
                    break

                if prompt.lower() == "quit":
                    print("Sentinel: [INFO] Exiting.")
                    self.runMainLoop = False
                elif prompt.lower() == "end":
                    print("Sentinel: [INFO] Executing end-of-session archiving...")
                    today_str = datetime.date.today().strftime("%m.%d.%Y")
                    archive_prompt = f"""[System Notice: Archive Command]
                    Take everything from memories/Current_Context.md and archive it:
                    1. Create a new memory file inside the memories folder (e.g. memories/Memory_Name_{today_str}.md) with today's date and the main topics of Current_Context.md as the header, containing the content of Current_Context.md.
                    2. For each main topic, check if a topic note exists in the topics folder. If not, create it. Update the topic note to link to the new memory using [[Memory_Name_{today_str}]] and add any relevant information.
                    3. Link the topic in the memory note using [[Topic_Name]].
                    4. Finally, update memories/Current_Context.md to be very simple, linking only the new memory (e.g. [[Memory_Name_{today_str}]]), so you can reaccess the information quickly.
                    
                    Perform all these operations now using your tools.
                    """
                    response = self.client.generate("qwen3.5:9b", archive_prompt)
                    print(f"Sentinel: {response}")
                else:
                    # Retrieve the latest Current_Context.md to prep the agent's short-term memory
                    current_context = self.client.obsidian.read_note("Current_Context.md")
                    if current_context:
                        full_prompt = f"[Current Context from Current_Context.md]\n{current_context}\n[End of Current Context]\n\nUser: {prompt}"
                    else:
                        full_prompt = prompt

                    response = self.client.generate("qwen3.5:9b", full_prompt)
                    print(f"Sentinel: {response}")
            else:
                print("Sentinel: [ERROR] Client is offline.")
                print("Sentinel: [INFO] Trying to reconnect.")
                self.tries += 1
                if self.tries >= 3:
                    print("Sentinel: [ERROR] Client is offline. Exiting.")
                    self.runMainLoop = False
                time.sleep(1)

    def initialize_sentinel(self):
        print("Sentinel: [INFO] Booting up. Reading Welcome.md...")
        welcome_content = self.client.obsidian.read_note("Welcome.md")
        if welcome_content:
            print("Sentinel: [INFO] Executing initialization tasks...")
            init_prompt = f"""[System Notice: Initialization Mode]
            Read Welcome.md below and execute the startup tasks:
            1. Read the listed directive files: Operational Directives, Core_Identity_and_Persona, PC_Information, Sentinel_Specifications.
            2. Update Sentinel_Control_Center.md based off your current status:
               - Status:
                 - Core Loops (STATE): Active
                 - Ollama Connection: Online
                 - KillSwitch: Armed
            3. Update memories/Current_Context.md with a summary of your mission.
            
            Welcome.md contents:
            {welcome_content}
            
            Confirm once initialization is complete.
            """
            response = self.client.generate("qwen3.5:9b", init_prompt)
            print(f"Sentinel: {response}")
        else:
            print("Sentinel: [WARNING] Welcome.md not found. Booting with default state.")

if __name__ == "__main__":
    MainLoop()