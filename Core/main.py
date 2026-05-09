from urllib3 import connection
import time
from Cognition.localModels import OllamaClient
from Safety.killSwitch import KillSwitch

def main():
    client = OllamaClient()
    killSwitch = KillSwitch()

    killSwitch.arm()
    
    print("Sentinel Core running...")

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
            response = client.generate_response(prompt)
            if (response):
                print(f"Sentinel: {response}")
            else:
                print("[Error] Failed to get response")

if __name__ == "__main__":
    main()