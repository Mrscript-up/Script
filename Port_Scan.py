import socket
import time
import threading
import sys


BLUE, RED, WHITE, YELLOW, MAGENTA, GREEN, END = '\33[94m', '\033[91m', '\33[97m', '\33[93m', '\033[1;35m', '\033[1;32m', '\033[0m'

class start:

    def __init__(self,tartget):
        self.tartget = tartget
        self.connect = None
        
        
    def connecting(self):
        try:
            self.connect = socket.socket(socket.AF_INET,socket.SOCK_STREAM,socket.setdefaulttimeout(1))
            for sock in range(1,200):
                RES = self.connect.connect_ex((self.tartget,sock))
                time.sleep(1)
                if RES == 0:
                    print(f'port {sock} {GREEN}Open{END}')
        except KeyboardInterrupt:
          sys.exit()
        except Exception as E:
            print(f'{RED}Error{END} --> {E}')
        except ConnectionError as con:
            print(f'connection Error -->\n{con}') 

if __name__ == '__main__':

    try:
        A = start('111.111.111.111')
        A.connecting()
    except KeyboardInterrupt:
        sys.exit()
    except Exception as E:
        print(f'Error -->\n{E}')

        
