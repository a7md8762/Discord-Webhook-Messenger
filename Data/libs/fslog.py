from datetime import datetime
import getpass

def Loginfo(message) -> None:
    time = datetime.now().strftime("%H:%M:%S")
    print(f"\033[1;30;40m[\033[1;34;40m{time}\033[1;30;40m]\033[0m \033[1;30;40m[\033[1;34;40mINFO\033[1;30;40m]\033[0m {message}")

def Logwarn(message) -> None:
    time = datetime.now().strftime("%H:%M:%S")
    print(f"\033[1;30;40m[\033[38;5;214m{time}\033[1;30;40m]\033[0m \033[1;30;40m[\033[38;5;214mWARN\033[1;30;40m]\033[0m {message}")

def Logerror(message) -> None:
    time = datetime.now().strftime("%H:%M:%S")
    print(f"\033[1;30;40m[\033[38;5;88m{time}\033[1;30;40m]\033[0m \033[1;30;40m[\033[38;5;88mERROR\033[1;30;40m]\033[0m {message}")
  
def Loginput(message, hidden: bool = False, withsignal: bool = False) -> str:
    time = datetime.now().strftime("%H:%M:%S")
    if hidden and withsignal:
        return getpass.getpass(f"\033[1;30;40m[\033[1;97;40m~\033[1;30;40m]\033[0m \033[1;30;40m[\033[1;32;92m{time}\033[0m\033[1;30;40m]\033[0m \033[1;30;40m[\033[5;32;92mINPUT\033[0m\033[1;30;40m]\033[0m {message}")
    if hidden:
        return getpass.getpass(f"\033[1;30;40m[\033[1;32;92m{time}\033[0m\033[1;30;40m]\033[0m \033[1;30;40m[\033[5;32;92mINPUT\033[0m\033[1;30;40m]\033[0m {message}")
    if withsignal:
        return input(f"\033[1;30;40m[\033[1;97;40m~\033[1;30;40m]\033[0m \033[1;30;40m[\033[1;32;92m{time}\033[0m\033[1;30;40m]\033[0m \033[1;30;40m[\033[5;32;92mINPUT\033[0m\033[1;30;40m]\033[0m {message}")
    return input(f"\033[1;30;40m[\033[1;32;92m{time}\033[0m\033[1;30;40m]\033[0m \033[1;30;40m[\033[5;32;92mINPUT\033[0m\033[1;30;40m]\033[0m {message}")

def Logcustom(message, logtype="log", color="1;34;40m") -> None:
    logcolor = ("\033[" + color)
    time = datetime.now().strftime("%H:%M:%S")
    print(f"\033[1;30;40m[{logcolor}{time}\033[0m\033[1;30;40m]\033[0m \033[1;30;40m[{logcolor}{logtype.upper()}\033[0m\033[1;30;40m]\033[0m {message}")
    
if __name__ == '__main__':
    Loginfo("aaaa")
    Logwarn("aa")
    Logerror("eee")
    Logcustom("custom test")
    Logcustom("custom test", "test")
    Logcustom("custom test", "test2", "5;37;40m")
