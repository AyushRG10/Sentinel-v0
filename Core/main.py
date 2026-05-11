from urllib3 import connection
import time
from Cognition.localModels import OllamaClient
from Safety.killSwitch import KillSwitch
from Memory.obsidian import ObsidianInterface

def main():
    client = OllamaClient()
    killSwitch = KillSwitch()
    obsidian = ObsidianInterface()

    killSwitch.arm()
    
    print("Sentinel Core running...")

    messages = []

    runLoop = False
    if (client.check_health()):
        print("[INFO] LLM connection established.")
        runLoop = True
    else:
        print("[ERROR] LLM connection failed.")
        runLoop = False
        killSwitch.disarm()

    while runLoop:
        connectionRecentlyEstablished = False

        if not client.check_health():
            print("[CRITICAL] LLM connection lost. Attempting reconnection...")
            connectionRecentlyEstablished = True
        elif connectionRecentlyEstablished == True:
            print("Connection recently established.")
            connectionRecentlyEstablished = False
        else:
            prompt = input("Prompt: ")
            messages.append({"role": "user", "content": prompt})
            response = client.generate_response(messages)
            if response:
                if "tool_calls" in response and response["tool_calls"]:
                    tool_call = response["tool_calls"][0]
                    function_name = tool_call["function"]["name"]
                    arguements = tool_call["function"]["arguments"]
                    print(f"[System] Sentinel is using tool: {function_name} with arguments: {arguements}")

                    result = None
                    if function_name == "search_obsidian_note":
                        result = obsidian.search_obsidian_note(arguements.get("keyword"))
                    elif function_name == "read_obsidian_note":
                        result = obsidian.read_obsidian_note(arguements.get("note_path"))
                    elif function_name == "write_obsidian_note":
                        result = obsidian.write_obsidian_note(arguements.get("note_path"), arguements.get("content"))

                    messages.append(response)
                    messages.append({"role": "tool", "content": str(result)})

                    print("[System] Waiting for Sentinel to process data...")
                    final_response = client.generate_response(messages)
                    if final_response and "content" in final_response:
                        print(f"Sentinel: {final_response['content']}")
                        messages.append(final_response)
                
                elif "content" in response:
                    print(f"Sentinel: {response['content']}")
                    messages.append(response)
                else:
                    print("[ERROR] No content or tool calls found in response.")

if __name__ == "__main__":
    main()