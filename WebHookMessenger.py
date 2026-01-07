import json, os, requests, hashlib
import Data.libs.fslog as log
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path

# Public variables
# <------------------------
WebhooksFolder = "Data/Webhooks" 
SettingsPath = "Data/settings/config.json"
SelectedWebhookName = None
SelectedWebhookURL = None
SelectedWebhookPath = None
MessageSignature = f"\n\n-# Sent using WebHookMessenger - {datetime.now(ZoneInfo("UTC")).strftime("%Y-%m-%d %H:%M:%S")} UTC"
# ------------------------>

# Functions not intended to be ran by the user
# <------------------------
def LoadSettings():
    global SettingsData

    try:
        with open(SettingsPath, "r") as f:
            SettingsData = json.load(f)
            return

    except (FileNotFoundError, json.JSONDecodeError):
        log.Logwarn("Settings file is either missing or corrupted! Recreating defaults...")
        os.makedirs(os.path.dirname(SettingsPath), exist_ok=True)

        SettingsData = DefaultSettings.copy()
        with open(SettingsPath, "w") as f:
            json.dump(SettingsData, f, indent=4)

def ClearTerminal():
    if os.name == 'nt':
        _ = os.system('cls')
    else:
        _ = os.system('clear')

def Terminal():
    try:
        while True:
            CommandPassed = log.Loginput("WHM@term:~$ ").lower()
            for CommandStored, CommandData in AvailableCommands.items():
                if CommandPassed == CommandStored or CommandPassed in CommandData["aliases"]:
                    CommandData["command"]()
                    break
            else:
                log.Logerror("Wrong Command! - Type 'help' for available commands.")
    except SystemExit:
        log.Loginfo("Bye!")

def WelcomeMessage():
    print(r"""
############################################################
#   __      __   _    _             _                      #
#   \ \    / /__| |__| |_  ___  ___| |__                   #
#    \ \/\/ / -_) '_ \ ' \/ _ \/ _ \ / /                   #
#     \_/\_/\___|_.__/_||_\___/\___/_\_\                   #
#               |  \/  |___ ______ ___ _ _  __ _ ___ _ _   #
#               | |\/| / -_|_-<_-</ -_) ' \/ _` / -_) '_|  #
#               |_|  |_\___/__/__/\___|_||_\__, \___|_|    #
#                                         |___/            #
#                                                          #
#     Welcome to Webhook Messenger!                        #
#             Made By: a7md8762 (Discord: lifeislinux)     #
#                     ENJOY!!!                             #
############################################################                    
""")
    log.Loginfo("Type 'help' for available commands.")
# ------------------------>

# Functions intended to be ran by the user
# <------------------------
def Help(): # this is the help command, bascially just gets the shit from this list:
    log.Logcustom("Available Commands: ", "help")
    for CommandStored, CommandData in AvailableCommands.items():
        log.Logcustom(f"Command: {CommandStored}", "help")
        log.Logcustom(f"    Description: {CommandData["description"]}", "help")
        log.Logcustom(f"    Aliases: {', '.join(CommandData['aliases'])}.\n", "help")

def AddWebhook():
    try:
        WebhookStatus = None
        while True:
            WebhookName = log.Loginput("Enter a name for the webhook: ")
            if os.path.isfile(os.path.join(WebhooksFolder, f"{WebhookName}.json")):
                log.Logwarn("A webhook is already added with this name, Do you want to replace it or no?")
                match log.Loginput("Please choose (y/n): ").lower():
                    case "y" | "ye" | "yes":
                        log.Logwarn("Replacing webhook... Please press Ctrl + C in the next step if this was a mistake!")
                        break

                    case "n" | "no":
                        pass

                    case _:
                        log.Logerror("Wrong option, Please try again...")
                        
            else:
                break

        WebhookPath = os.path.join(WebhooksFolder, f"{WebhookName}.json")
        
        WebhookURL = log.Loginput("Enter the Webhook's URL: (hidden)", hidden=True)
        while True:
            if WebhookURL.startswith("https://discord.com/api/webhooks/") and WebhookURL != "https://discord.com/api/webhooks/":
                break
            log.Logerror("Not a valid webhook!")
            WebhookURL = log.Loginput("Please enter a valid one or press Ctrl + C to exit: (hidden)", hidden=True)
        log.Loginfo("Checking if the webhook is valid...")
        try:
            ReqURL = requests.get(WebhookURL, timeout=5)
            match ReqURL.status_code:
                case 200 | 204:
                    WebhookStatus = "success"
                    WebhookData = {"WebhookName":WebhookName, "WebhookURL":WebhookURL, "WebhookStatus":WebhookStatus, "WebhookHash":hashlib.sha256(WebhookURL.encode()).hexdigest(), "DateAdded":datetime.now().isoformat(), "LastChecked":datetime.now().isoformat(), "LastEdited":datetime.now().isoformat()}

                    os.makedirs(WebhooksFolder, exist_ok=True)
                    with open(WebhookPath, "w") as f:
                        json.dump(WebhookData, f, indent=4)
                    log.Logcustom("Added the webhook successfully!", "success", "1;32m")

                case 401 | 403 | 404:
                    WebhookStatus = "fail"
                    log.Logerror("Webhook was not found!")

                case 429:
                    log.Logerror("Rate limit reached, Please try again later!")

                case _:
                    log.Logerror(f"Unknown status code error! (Status Code: {ReqURL.status_code})")

        except requests.Timeout:
            WebhookStatus = "timeout"
            log.Logerror("Checking timed out, Please try again!")

        except requests.ConnectionError:
            WebhookStatus = "conerror"
            log.Logerror("Checking failed, Please check your internet!")

        except requests.RequestException as e:
            WebhookStatus = "fail"
            log.Logerror(f"Checking failed due to an unknown error!\n{e}")
    except KeyboardInterrupt:
        print()
        log.Loginfo("Canceling...")

def DeleteWebhook():
    try:
        WebhookName = log.Loginput("Please enter the name of the webhook you wish to delete: ")
        while True:
            if os.path.isfile(os.path.join(WebhooksFolder, f"{WebhookName}.json")):
                break
            log.Logerror("This webhook does not exist!")
            WebhookName = log.Loginput("Please enter a valid one or press Ctrl + C to exit: ")

        log.Logwarn("Do you really wish to delete this webhook? Deleting a webhook is PERMANENT!")
        match log.Loginput("Please choose (y/n): ").lower():
            case "y" | "ye" | "yes":
                log.Loginfo("Deleting webhook...")
                os.remove(os.path.join(WebhooksFolder, f"{WebhookName}.json"))
                log.Logcustom("Deleted the webhook successfully!", "success", "1;32m")

            case "n" | "no":
                pass
            case _:
                log.Logerror("Unknown option!")
            
    except KeyboardInterrupt:
        print()
        log.Loginfo("Canceling...")

def EditWebhook():
    try:
        ReplaceExistingWebhook = False
        NewWebhookPath = None

        WebhookName = log.Loginput("Please enter the name of the webhook you wish to edit: ")
        while True:
            if os.path.isfile(os.path.join(WebhooksFolder, f"{WebhookName}.json")):
                break
            log.Logerror("This webhook does not exist!")
            WebhookName = log.Loginput("Please enter a valid one or press Ctrl + C to exit: ")

        WebhookPath = os.path.join(WebhooksFolder, f"{WebhookName}.json")
        with open(WebhookPath) as f:
            WebhookData = json.load(f)
        
        log.Loginfo("Here's what you can edit: \n                  1. WebhookName\n                  2. WebhookURL\n                  3. WebhookStatus")
        while True:
            match log.Loginput("Please choose (1/2/3/save/cancel): ").lower():
                case "1" | "webhookname":
                    while True:
                        ReplaceExistingWebhook = False
                        WebhookData["WebhookName"] = log.Loginput("Please enter your new webhook name: ")
                        if os.path.isfile(os.path.join(WebhooksFolder, f"{WebhookData["WebhookName"]}.json")):
                            log.Logwarn("A webhook is already added with this name, Do you want to replace it or no? (Note: If you choose yes, The whole webhook will be replaced with the data of the webhook you are currently editing!)" )
                            match log.Loginput("Please choose (y/n): ").lower():
                                case "y" | "ye" | "yes":
                                    log.Logwarn("Replacing webhook... Please press Ctrl + C in the next step if this was a mistake!")
                                    ReplaceExistingWebhook = True
                                    NewWebhookPath = os.path.join(WebhooksFolder, f"{WebhookData["WebhookName"]}.json")
                                    break

                                case "n" | "no":
                                    pass

                                case _:
                                    log.Logerror("Wrong option, Please try again...")
                                    
                        else:
                            NewWebhookPath = os.path.join(WebhooksFolder, f"{WebhookData["WebhookName"]}.json")
                            break
                    log.Logcustom("Changes saved successfully! (Type 'save' when you are ready to save your edits)", "success", "1;32m")

                case "2" | "webhookurl":
                    WebhookData["WebhookURL"] = log.Loginput("Please enter your new webhook URL: (hidden)", hidden=True)
                    while True:
                        if WebhookData["WebhookURL"].startswith("https://discord.com/api/webhooks/") and WebhookData["WebhookURL"] != "https://discord.com/api/webhooks/":
                            break
                        log.Logerror("Not a valid webhook!")
                        WebhookData["WebhookURL"] = log.Loginput("Please enter a valid one or press Ctrl + C to exit: (hidden)", hidden=True)
                    log.Loginfo("Checking if the webhook is valid...")
                    try:
                        ReqURL = requests.get(WebhookData["WebhookURL"], timeout=5)
                        match ReqURL.status_code:
                            case 200 | 204:
                                WebhookData["WebhookHash"] = hashlib.sha256(WebhookData["WebhookURL"].encode()).hexdigest()
                                log.Logcustom("Changes saved successfully! (Type 'save' when you are ready to save your edits)", "success", "1;32m")

                            case 401 | 403 | 404:
                                log.Logerror("Webhook was not found!")

                            case 429:
                                log.Logerror("Rate limit reached, Please try again later!")

                            case _:
                                log.Logerror(f"Unknown status code error! (Status Code: {ReqURL.status_code})")

                    except requests.Timeout:
                        log.Logerror("Checking timed out, Please try again!")

                    except requests.ConnectionError:
                        log.Logerror("Checking failed, Please check your internet!")

                    except requests.RequestException as e:
                        log.Logerror(f"Checking failed due to an unknown error!\n{e}")

                case "3" | "webhookstatus":
                    WebhookData["WebhookStatus"] = log.Loginput("Please enter your new webhook status: ").lower()
                    log.Logcustom("Changes saved successfully! (Type 'save' when you are ready to save your edits)", "success", "1;32m")

                case "4" | "s" | "save":
                    break

                case "5" | "c" | "cancel":
                    raise KeyboardInterrupt

                case _:
                    log.Logerror("Unknown option!")

        log.Loginfo("Applying changes...")
        if NewWebhookPath == None:
            NewWebhookPath = WebhookPath

        WebhookData["LastEdited"] = datetime.now().isoformat()
        with open(WebhookPath, "w") as f:
            json.dump(WebhookData, f, indent=4)
        if NewWebhookPath != WebhookPath:
            if os.path.exists(NewWebhookPath) and ReplaceExistingWebhook:
                os.remove(NewWebhookPath)
            os.rename(WebhookPath, NewWebhookPath)

        log.Logcustom("Applied changes successfully!", "success", "1;32m")

    except KeyboardInterrupt:
        print()
        log.Loginfo("Canceling...")

def RequestConnection():
    global SelectedWebhookName
    global SelectedWebhookPath
    global SelectedWebhookURL

    try:
        if any(f.suffix == ".json" for f in Path(WebhooksFolder).iterdir() if f.is_file()):
            WebhookName = log.Loginput("Please enter the webhook you wish to connect to: ")
            while True:
                if os.path.isfile(os.path.join(WebhooksFolder, f"{WebhookName}.json")):
                    break
                log.Logerror("This webhook does not exist!")
                WebhookName = log.Loginput("Please enter a valid one or press Ctrl + C to exit: ")

            WebhookPath = os.path.join(WebhooksFolder, f"{WebhookName}.json")
            with open(WebhookPath) as f:
                WebhookData = json.load(f)
            if WebhookData["WebhookURL"].startswith("https://discord.com/api/webhooks/") and WebhookData["WebhookURL"] != "https://discord.com/api/webhooks/":
                match WebhookData["WebhookStatus"]:
                    case "success" | "ratelimit" | "conerror" | "timeout" | "unknown":
                        if not WebhookData["WebhookStatus"] == "success":
                            log.Logwarn(f"The webhook was not checked correctly due to connection errors (Status: {WebhookData["WebhookStatus"]}).")
                            while True:
                                match log.Loginput("Do you wish to continue and check anyways? Please Choose (y/n): ").lower():
                                    case "y" | "ye" | "yes":
                                        break
                                    case "n" | "no":
                                        log.Loginfo("Canceling...")
                                        Terminal()
                                    case _:
                                        log.Logerror("Wrong option! Please choose again...")
                                    
                        log.Loginfo("Checking if the webhook is still valid...")
                        try:
                            ReqURL = requests.get(WebhookData["WebhookURL"], timeout=5)
                            match ReqURL.status_code:
                                case 200 | 204:
                                    SelectedWebhookName = WebhookData["WebhookName"]
                                    SelectedWebhookPath = WebhookPath
                                    SelectedWebhookURL = WebhookData["WebhookURL"]
                                    WebhookData["LastChecked"] = datetime.now().isoformat()
                                    WebhookData["WebhookStatus"] = "success"
                                    log.Logcustom("Selected the webhook successfully! You may send messages through it now.", "success", "1;32m")

                                case 401 | 403 | 404:
                                    WebhookData["LastChecked"] = datetime.now().isoformat()
                                    WebhookData["WebhookStatus"] = "fail"
                                    log.Logerror("Webhook was not found!")

                                case 429:
                                    WebhookData["LastChecked"] = datetime.now().isoformat()
                                    WebhookData["WebhookStatus"] = "ratelimit"
                                    log.Logerror("Rate limit reached, Please try again later!")

                                case _:
                                    WebhookData["LastChecked"] = datetime.now().isoformat()
                                    WebhookData["WebhookStatus"] = "unknown"
                                    log.Logerror(f"Unknown status code error! (Status Code: {ReqURL.status_code})")

                        except requests.Timeout:
                            WebhookData["LastChecked"] = datetime.now().isoformat()
                            WebhookData["WebhookStatus"] = "timeout"
                            log.Logerror("Checking timed out, Please try again!")

                        except requests.ConnectionError:
                            WebhookData["LastChecked"] = datetime.now().isoformat()
                            WebhookData["WebhookStatus"] = "conerror"
                            log.Logerror("Checking failed, Please check your internet!")

                        except requests.RequestException as e:
                            WebhookData["LastChecked"] = datetime.now().isoformat()
                            WebhookData["WebhookStatus"] = "unknown"
                            log.Logerror(f"Checking failed due to an unknown error!\n{e}")
                    
                    case _:
                        WebhookData["LastChecked"] = datetime.now().isoformat()
                        log.Logerror(f"This webhook does not seem to be working! Please check its status! (Status: {WebhookData["WebhookStatus"]})")
            else:
                WebhookData["LastChecked"] = datetime.now().isoformat()
                WebhookData["WebhookStatus"] = "invalid"
                log.Logerror("Not a valid webhook!")
            
            with open(WebhookPath, "w") as f:
                json.dump(WebhookData, f, indent=4)
        else:
            log.Logerror("No webhooks available to connect to! Make sure you add atleast one webhook using 'addwebhook' command!")

    except KeyboardInterrupt:
        print()
        log.Loginfo("Canceling...")

def ExitConnection():
    global SelectedWebhookName
    global SelectedWebhookPath
    global SelectedWebhookURL

    if not SelectedWebhookPath == None:
        log.Logwarn("Are you sure you want to exit from the connection?")
        while True:
            match log.Loginput("Please choose (y/n): ").lower():
                case "y" | "ye" | "yes":                   
                    SelectedWebhookPath = None
                    SelectedWebhookURL = None
                    log.Logcustom(f"Exited from the '{SelectedWebhookName}' webhook successfully!", "success", "1;32m")
                    SelectedWebhookName = None
                    break

                case "n" | "no":
                    break

                case _:
                    log.Logerror("Wrong option! Please choose again...")

    else:
        log.Logerror("Nothing is connected to exit from!")

def ExitCommand():
    log.Loginfo("Exiting...")
    raise SystemExit

def SendMessage():
    global SelectedWebhookName
    global SelectedWebhookPath
    global SelectedWebhookURL

    try:
        if not SelectedWebhookPath == None:
            with open(SelectedWebhookPath) as f:
                WebhookData = json.load(f)
            match WebhookData["WebhookStatus"]:
                case "success" | "ratelimit" | "conerror" | "timeout" | "unknown":
                    if not WebhookData["WebhookStatus"] == "success":
                        log.Logwarn(f"The webhook was not checked correctly due to connection errors! (Status: {WebhookData["WebhookStatus"]}).")
                        while True:
                            match log.Loginput("Do you wish to continue and send a message anyways? Please Choose (y/n): ").lower():
                                case "y" | "ye" | "yes":
                                    break
                                case "n" | "no":
                                    log.Loginfo("Canceling...")
                                    Terminal()
                                case _:
                                    log.Logerror("Wrong option! Please choose again...")

                    data = {"content": log.Loginput("Message to send: ") + MessageSignature}
                    try:
                        ReqURL = requests.post(SelectedWebhookURL, json=data)
                        match ReqURL.status_code:
                            case 200 | 204:
                                WebhookData["LastChecked"] = datetime.now().isoformat()
                                WebhookData["WebhookStatus"] = "success"
                                log.Logcustom(f"Sent message to '{SelectedWebhookName}' successfully!", "success", "1;32m")
                            
                            case 401 | 403 | 404:
                                WebhookData["LastChecked"] = datetime.now().isoformat()
                                WebhookData["WebhookStatus"] = "fail"
                                log.Logerror("Webhook was not found!")

                            case 429:
                                WebhookData["LastChecked"] = datetime.now().isoformat()
                                WebhookData["WebhookStatus"] = "ratelimit"
                                log.Logerror("Rate limit reached, Please try again later!")

                            case _:
                                WebhookData["LastChecked"] = datetime.now().isoformat()
                                WebhookData["WebhookStatus"] = "unknown"
                                log.Logerror(f"Unknown status code error! (Status Code: {ReqURL.status_code})")

                    except requests.Timeout:
                        WebhookData["LastChecked"] = datetime.now().isoformat()
                        WebhookData["WebhookStatus"] = "timeout"
                        log.Logerror("Sending message timed out, Please try again!")

                    except requests.ConnectionError:
                        WebhookData["LastChecked"] = datetime.now().isoformat()
                        WebhookData["WebhookStatus"] = "conerror"
                        log.Logerror("Sending message failed, Please check your internet!")

                    except requests.RequestException as e:
                        WebhookData["LastChecked"] = datetime.now().isoformat()
                        WebhookData["WebhookStatus"] = "unknown"
                        log.Logerror(f"Sending message failed due to an unknown error!\n{e}")

                case _:
                    WebhookData["LastChecked"] = datetime.now().isoformat()
                    log.Logerror(f"This webhook does not seem to be working! Please check its status! (Status: {WebhookData["WebhookStatus"]})")

            with open(SelectedWebhookPath, "w") as f:
                json.dump(WebhookData, f, indent=4)

        else:
            log.Logerror("Please connect to a webhook first using 'requestconnection' command!")
    except KeyboardInterrupt:
        print()
        log.Loginfo("Canceling...")

def EnterChatMode():
    global SelectedWebhookName
    global SelectedWebhookPath
    global SelectedWebhookURL

    try:
        if not SelectedWebhookPath == None:
            with open(SelectedWebhookPath) as f:
                WebhookData = json.load(f)

            ClearTerminal()
            log.Loginfo("You have entered chat mode, Press Ctrl + C to exit from here.\n")
            while True:
                match WebhookData["WebhookStatus"]:
                    case "success" | "ratelimit" | "conerror" | "timeout" | "unknown":
                        if not WebhookData["WebhookStatus"] == "success":
                            log.Logwarn(f"The webhook was not checked correctly due to connection errors! (Status: {WebhookData["WebhookStatus"]}).")
                            while True:
                                match log.Loginput("Do you wish to continue and send a message anyways? Please Choose (y/n): ").lower():
                                    case "y" | "ye" | "yes":
                                        break
                                    case "n" | "no":
                                        log.Loginfo("Canceling...")
                                        Terminal()
                                    case _:
                                        log.Logerror("Wrong option! Please choose again...")

                        data = {"content": log.Loginput(": ", withsignal=True) + MessageSignature}
                        try:
                            ReqURL = requests.post(SelectedWebhookURL, json=data)
                            match ReqURL.status_code:
                                case 200 | 204:
                                    WebhookData["LastChecked"] = datetime.now().isoformat()
                                    WebhookData["WebhookStatus"] = "success"
                                    print(f"\033[1A\033[1;30;40m[\033[1;32mS\033[1;30;40m]\033[0m")
                                
                                case 401 | 403 | 404:
                                    WebhookData["LastChecked"] = datetime.now().isoformat()
                                    WebhookData["WebhookStatus"] = "fail"
                                    print(f"\033[1A\033[1;30;40m[\033[1;31mF\033[1;30;40m]\033[0m")
                                    log.Logerror("Webhook was not found!")
                                    break

                                case 429:
                                    WebhookData["LastChecked"] = datetime.now().isoformat()
                                    WebhookData["WebhookStatus"] = "ratelimit"
                                    print(f"\033[1A\033[1;30;40m[\033[1;31mF\033[1;30;40m]\033[0m")
                                    log.Logerror("Rate limit reached, Please try again later!")
                                    break

                                case _:
                                    WebhookData["LastChecked"] = datetime.now().isoformat()
                                    WebhookData["WebhookStatus"] = "unknown"
                                    print(f"\033[1A\033[1;30;40m[\033[1;31mF\033[1;30;40m]\033[0m")
                                    log.Logerror(f"Unknown status code error! (Status Code: {ReqURL.status_code})")
                                    break

                        except requests.Timeout:
                            WebhookData["LastChecked"] = datetime.now().isoformat()
                            WebhookData["WebhookStatus"] = "timeout"
                            print(f"\033[1A\033[1;30;40m[\033[1;31mF\033[1;30;40m]\033[0m")
                            log.Logerror("Sending message timed out, Please try again!")
                            break

                        except requests.ConnectionError:
                            WebhookData["LastChecked"] = datetime.now().isoformat()
                            WebhookData["WebhookStatus"] = "conerror"
                            print(f"\033[1A\033[1;30;40m[\033[1;31mF\033[1;30;40m]\033[0m")
                            log.Logerror("Sending message failed, Please check your internet!")
                            break

                        except requests.RequestException as e:
                            WebhookData["LastChecked"] = datetime.now().isoformat()
                            WebhookData["WebhookStatus"] = "unknown"
                            print(f"\033[1A\033[1;30;40m[\033[1;31mF\033[1;30;40m]\033[0m")
                            log.Logerror(f"Sending message failed due to an unknown error!\n{e}")
                            break

                    case _:
                        WebhookData["LastChecked"] = datetime.now().isoformat()
                        log.Logerror(f"This webhook does not seem to be working! Please check its status! (Status: {WebhookData["WebhookStatus"]})")

                with open(SelectedWebhookPath, "w") as f:
                    json.dump(WebhookData, f, indent=4)

            with open(SelectedWebhookPath, "w") as f:
                json.dump(WebhookData, f, indent=4) 
        else:
            log.Logerror("Please connect to a webhook first using 'requestconnection' command!")
    except KeyboardInterrupt:
        print("\n")
        log.Loginfo("Exiting chat mode...")

def Settings():
    global SettingsData

    try:
        log.Loginfo("Available options: \n                  1. View settings\n                  2. Edit settings\n                  3. Reset settings to default")
        while True:
            match log.Loginput("Please choose (1/2/3): ").lower():
                case "1":
                    for SettingsItem, SettingsValue in SettingsData.items():
                        log.Logcustom(f"'{SettingsItem}': '{SettingsValue}'", "cfg")
                    print()
                    break

                case "2":
                    log.Logcustom(f"Available settings to edit: {', '.join(SettingsData)}.\n", "cfg")

                    log.Loginfo("Type the name of the setting you want to edit. \n                  Type 'save' to save changes. \n                  Type 'cancel' to exit without saving.")
                    while True:
                        match log.Loginput("Please choose (name of setting/save/cancel): ").lower():
                            case "developermode" | "devmode":
                                log.Loginfo("Would you like to (d)isable or (e)nable?")
                                while True:
                                    match log.Loginput("Please choose (d/e): ").lower():
                                        case "disable" | "d":
                                            SettingsData["developermode"] = False
                                            log.Logcustom("Changes saved successfully! (Type 'save' when you are ready to save your edits)", "success", "1;32m")
                                            break

                                        case "enable" | "e":
                                            SettingsData["developermode"] = True
                                            log.Logcustom("Changes saved successfully! (Type 'save' when you are ready to save your edits)", "success", "1;32m")
                                            break

                            case "save" | "s":
                                log.Loginfo("Applying changes...")
                                with open(SettingsPath, "w") as f:
                                    json.dump(SettingsData, f, indent=4)

                                log.Logcustom("Applied changes successfully!", "success", "1;32m")
                                break

                            case "cancel" | "c":
                                raise KeyboardInterrupt

                            case _:
                                log.Logerror("Wrong option! Please choose again...")
                    break

                case "3":
                    log.Logwarn("Are you sure you want to reset settings to default?")
                    while True:
                        match log.Loginput("Please choose (y/n): ").lower():
                            case "yes" | "ye" | "y":
                                with open(SettingsPath, "w") as f:
                                    json.dump(DefaultSettings, f, indent=4)
                                log.Logcustom(f"Reset settings to default successfully!", "success", "1;32m")
                                break                         

                            case "no" | "n":
                                log.Loginfo("Canceling...")
                                break

                            case _:
                                log.Logerror("Wrong option! Please choose again...")
                    break

                case _:
                    log.Logerror("Wrong option! Please choose again...")
    except KeyboardInterrupt:
        print()
        log.Loginfo("Canceling...")

def TestCommand():
    if SettingsData["developermode"]:
        print("yes")
    else:
        print("no")

# Lists
# <------------------------
AvailableCommands = {
    # Commands Implemented: help, addwebhook, deletewebhook, editwebhook, requestconnection, exitconnection, exit, sendmessage, enterchatmode, settings, testcommand.

    "help": {"aliases":["help", "h"], "command":Help, "description":"Displays the available commands to run."}, 
    "addwebhook": {"aliases":["addwebhook", "addwh"], "command":AddWebhook, "description":"Let's you add a new webhook."},
    "deletewebhook": {"aliases":["deletewebhook", "delwh"], "command":DeleteWebhook, "description":"Let's you delete a saved webhook."},
    "editwebhook": {"aliases":["editwebhook", "editwh"], "command":EditWebhook, "description":"Let's you edit a saved webhook."}, 
    "requestconnection": {"aliases":["requestconnection", "reqcon"], "command":RequestConnection, "description":"Tries to connect with a saved webhook."},
    "exitconnection": {"aliases":["exitconnection", "exitcon"], "command":ExitConnection, "description":"Exits the connection established with a webhook."},
    "exit": {"aliases":["exit"], "command":ExitCommand, "description":"Exits the program."},
    "sendmessage": {"aliases":["sendmessage", "sendmsg", "msg"], "command":SendMessage, "description":"Sends a single message to the established connection."},
    "enterchatmode": {"aliases":["enterchatmode", "enterchat", "chatmode"], "command":EnterChatMode, "description":"Let's you enter a field to message the webhook established with freely."},
    "settings": {"aliases":["settings", "config", "cfg"], "command":Settings, "description":"Let's you edit the settings of the program."},
    "testcommand": {"aliases":["testcommand", "test"], "command":TestCommand, "description":"Code test."}
    }

DefaultSettings = {
    # Settings Implemented: developermode.

    "developermode": False
    }
# ------------------------>

# ------------------------>

# Main
# <------------------------
def main():
    LoadSettings()
    WelcomeMessage()
    Terminal()
# ------------------------>

# Runner
# <------------------------
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print()
        log.Loginfo("Exiting... Bye!")

    except Exception as e:
        log.Logcustom("Something went REALLY wrong!!!", "critical", "1;31m")
        print(f"\n{e}")
# ------------------------>