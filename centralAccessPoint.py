from ollamaClient import OllamaClient

class MainLoop:

    client = OllamaClient()

    runMainLoop = True
    tries = 0
    while runMainLoop:
        isClientActive = client.check_model()
        if isClientActive:
            tries = 0
            print("Sentinel: [INFO] Client is online.")
            prompt = input("User: ")
            if prompt == "quit":
                print("Sentinel: [INFO] Exiting.")
                runMainLoop = False
            else:
                response = client.generate("llama3", prompt)
                print(f"Sentinel: {response}")
        else:
            print("Sentinel: [ERROR] Client is offline.")
            print("Sentinel: [INFO] Trying to reconnect.")
            tries += 1
            if tries >= 3:
                print("Sentinel: [ERROR] Client is offline. Exiting.")
                runMainLoop = False

if __name__ == "__main__":
    MainLoop()