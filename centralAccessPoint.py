from ollamaClient import OllamaClient
from killSwitch import KillSwitch
import time

class MainLoop:

    client = OllamaClient()
    killSwitch = KillSwitch()
    killSwitch.arm()

    runMainLoop = True
    tries = 3

    if client.check_model():
        client.generate("qwen2.5:7b-instruct", "Read Welcome.md first and follow the instructions inside it.")
        client.generate("qwen2.5:7b-instruct", "Read Current Context")
        
    while runMainLoop:
        isClientActive = client.check_model()
        if isClientActive:
            if tries != 0:
                print("Sentinel: [INFO] Client is online.")
                tries = 0
            prompt = input("User: ")
            if prompt == "quit":
                print("Sentinel: [INFO] Exiting.")
                runMainLoop = False
            else:
                response = client.generate("qwen2.5:7b-instruct", prompt)
                print(f"Sentinel: {response}")
        else:
            print("Sentinel: [ERROR] Client is offline.")
            print("Sentinel: [INFO] Trying to reconnect.")
            tries += 1
            if tries >= 3:
                print("Sentinel: [ERROR] Client is offline. Exiting.")
                runMainLoop = False
            time.sleep(1)

if __name__ == "__main__":
    MainLoop()