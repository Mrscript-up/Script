import subprocess
import paramiko
import time
import sys
from pathlib import Path
import os
from subprocess import Popen,PIPE
import hashlib

BLUE, RED, WHITE, YELLOW, MAGENTA, GREEN, END = '\33[94m', '\033[91m', '\33[97m', '\33[93m', '\033[1;35m', '\033[1;32m', '\033[0m'

class start:
    def __init__(self,host,username1,password1):
        self.username2 = username1
        self.password2 = password1
        self.host2 = host
        self.ssh_clint = None

        print(f"""{GREEN}
$$$$$$$$$   $$$$$$$$$   $$$$$$$$$   $$$$$$$$$
$$  $       $$  $       $       $   $       $      $
$$  $       $$  $       $       $$$$$       $    $    $
$$$$$$$$$   $$$$$$$$$   $    #          #   $  $   $    $
    $  $$       $  $$   $       $$$$$       $    $    $
    $  $$       $  $$   $       $   $       $      $
$$$$$$$$$   $$$$$$$$$   $$$$$$$$$   $$$$$$$$$
         {END}{RED}<GHASEMI--GROUP>{END}
""")
        self.concting()
    def concting(self): 
        try:
            print(f"{BLUE}[-]{END} <connecting to SSH pleas waiting.....>")
            start = round(time.time()) 
            self.ssh_clint = paramiko.SSHClient()
            self.ssh_clint.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh_clint.connect(hostname=self.host2,username=self.username2,password=self.password2,timeout=5)
            end = round(time.time(),1)
            
            print(f'{BLUE}[-]{END} connecting on {start - end}')
            print(f"{GREEN}[*]{END} <connecting successfoly.....>")
            return True
        except paramiko.AuthenticationException:
            print(f'{RED}[~]{END} Authentication fild: pleas check your your <username> or <password>')
            return False
        except paramiko.SSHException as ex:
            print(f'{RED}[~]{END} there is somthing wrong in the:\n{RED}[~]{END} {ex}')
            return False
        except Exception as exip:
            print(f'{RED}[~]{END} connection FALSE <error!>\n{RED}[~]{END} {exip}')
            return False
        except KeyboardInterrupt:
            print(f'{BLUE}:){END}')
        
    

    def runing_command(self):
        if not self.ssh_clint:
            print(f'{RED}[~]{END} there is somthings wrong in the SSH connecting....\n<pleas check that>')
            return
            
        while True:
            try:
                print(f"{BLUE}[-]{END} what is your command:")
                print(f'{GREEN}[-]{END} for exit >>> <<exit>>')
                command_user = input(">>>")
                if command_user.lower() == 'exit':
                    break  
                if not command_user:
                    print(f'{RED}[*]{END} pleas inter somthing command [*]')
                    continue
                                
                stdin , stdout , stderr = self.ssh_clint.exec_command(command_user)
                output = stdout.read().decode('utf-8')
                error = stderr.read().decode('utf-8')
                if output:
                    print(f'{GREEN}[-]{END} responce:\n{GREEN}[~]{END} {output}')
                if error:
                    print(f'{RED}[~]{END} error:\n{RED}[~]{END} {error}')

                file_saving = input(f'{BLUE}[-]{END} would you like to saving response? ({GREEN}y{END};{RED}n{END})>>>')
                if not file_saving:
                    continue
                if file_saving.lower() == 'y':
                    Path.touch('resp0nce_c0mmand.txt')
                    path = Path('resp0nce_c0mmand.txt')
                    with path.open(mode='a',encoding='utf-8') as f:
                        f.write('----------------------'+'\n'+f'command : {command_user}'+'\n'+ output)
                    print(f'{GREEN}[-]{END} file has been success fuly in (resp0nse_c0mmand.txt)')
                else:
                    continue

            except Exception as e:
                print(f'{RED}[~]{END} there is some <problem>:\n{RED}[~]{END} {e}')
                sys.exit()
            except KeyboardInterrupt:
                print(f'{RED}[~]{END} exit = (exit)')
                continue
            

                

    def file_sending(self):
        if not self.ssh_clint:
            print(f'{RED}[-]{END} there is somthing wrong in the ssh conection......')
            return
        ###-----------------------------------------------------------------------------###color since here.
        while True:
            try:
                print(f"{BLUE}[-]{END} welcom to ssh file upload....")
                print(f'{RED}[-]{END} Exit = (n,N)')
                local_path = input(f'{BLUE}[-]{END} your file local path>>>')
                if local_path.lower == 'n':
                    break
                remote_path = input(f'{BLUE}[-]{END} your remote path>>>')
                if remote_path.lower() == 'n':
                    break
                file_name = input(f'{BLUE}[-]{END} file name(seaving)>>>')
                if file_name.lower() == 'n':
                    break
                Access_infor = input(f'{RED}[-]{END} thise your information is right? ({GREEN}y{END},{RED}n{END})\n{YELLOW}[-]{END} localpath = {local_path}\n{YELLOW}[-]{END} remotepath = {remote_path}\n{YELLOW}[-]{END} filename = {file_name}\n>>>')
                if not Access_infor:
                    print(f'{RED}[*]{END} please accept information [*]')
                    continue
                if Access_infor.lower() == 'y':
                    sftp = self.ssh_clint.open_sftp()
                    sftp.put(local_path,os.path.join(remote_path,file_name))
                    print(f'{GREEN}[-]{END} file has been upload....')
                    sftp.close()
                    stdout , stderr = self.ssh_clint.exec_command(f'ls {remote_path} | grep {file_name}')
                    out_put = stdout.read().decode('utf-8')
                    error = stderr.read().decode('utf-8')
                    if out_put:
                        print(f'{RED}[-]{END} responce:\n{RED}[-]{END} {out_put}')
                    if error:
                        print(f'{RED}[~]{END} error:\n{RED}[-]{END} {error}')
                if Access_infor.lower() == 'n':
                    break
            except Exception as e:
                print(f'\n{RED}[~]{END} there are a error:\n{e}')
                sys.exit()
            
            except FileNotFoundError:
                print(f'\n{RED}[~]{END} file not found...')
                break
            except KeyboardInterrupt:
                print(f'\n{RED}[~]{END} exit = (n)')
                continue


    def file_downloding(self):
        if not self.ssh_clint:
            print(f'{RED}[-]{END} there is somthing wrong in the ssh conection......')
            return
        while True:
            try:
                print(f'{BLUE}[-]{END} welcom to ssh file downloding...\n{BLUE}[-]{END} exit = (exit)')
                file_remote_path = input(f"{BLUE}[-]{END} path the file in server:>>>")
                if file_remote_path.lower() == 'exit':
                    break
                file_local_path = input(f"{BLUE}[-]{END} path the file in local:>>>")
                if file_local_path.lower() == 'exit':
                    break
                file_name = input(f'{BLUE}[-]{END} name file (for saving):>>>')
                if file_name.lower() == 'exit':
                    break
                print(f'{BLUE}[-]{END} your file (/home/username/) = {file_remote_path}')
                print(f'{BLUE}[-]{END} your server path (/home/username/) = {file_local_path}')
                print(f'{BLUE}[-]{END} your file name = {file_name}')
                sure = input(f'{RED}[-]{END} are you sure? ({GREEN}y,Y{END}||{RED}n,N{END})>>>')
                if not sure:
                    print(f'{RED}[~]{END}pleas accept informations....')
                    continue
                if sure.lower() == 'y':
                    sftp = self.ssh_clint.open_sftp()
                    sftp.get(file_remote_path,os.path.join(file_local_path,file_name))
                    print(f'{GREEN}[-]{END} the uoload has been successfuly.....')
                    print(f'{BLUE}[-]{END} this file {file_remote_path} from this path {file_local_path}.')
                    sftp.close()
                else:
                    print(f'{RED}[*]{END}try again...')
                    continue
            except Exception as er:
                print(f'{RED}[~]error:{END}\n{er}')
            except FileNotFoundError:
                print(f'{RED}[~]{END} file not fond...')
            except KeyboardInterrupt:
                print(f'{RED}[~]{END} exit = (exit)')
                continue
            
    
    def port_forwarding_local(self):
        if not self.ssh_clint:
            print(f'{RED}[~]{END} there is somthings wrong in the SSH connecting....\n<pleas check that>')
            return
        while True:
            try:
                ssh_host = self.host2
                ssh_user = self.username2
                
                print(f'{BLUE}[-]{END} welcom to the ssh port forwarding local.....')
                print(f'{BLUE}[-]{END} pleas waiting....')
                time.sleep(1)
                print(f'{RED}[-]{END} exit == <n or N>')
                local_port = input(f'{BLUE}[-]{END} local port>>>')
                if local_port.lower() == 'n':
                    break
                remote_host = input(f'{BLUE}[-]{END} remote host>>>')
                if remote_host.lower() == 'n':
                    break
                remote_port = input(f'{BLUE}[-]{END} remote port>>>')
                if remote_port.lower() == 'n':
                    break
                path_key = input(f'{BLUE}[-]{END} path <SSH> key>>>')
                if path_key.lower() == 'n':
                    break
                
                print(f'{BLUE}[*]{END} your information:')
                print(f'{BLUE}[-]{END} >>>\n{YELLOW}[1]{END} local_port = {local_port}\n{YELLOW}[2]{END} remote_host = {remote_host}\n{YELLOW}[3]{END} remote_port = {remote_port}')
                print(f'{YELLOW}[4]{END} by this path_key = {path_key}')
                authentication = input(f'{RED}[*]{END} is thise informations is right?? (y,n) >>>')
                if authentication.lower() == 'y':
                    command = [
                    'ssh',
                    '-i', path_key,
                    '-o', 'StrictHostKeyChecking=no',
                    '-N',
                    '-L', f'{local_port}:{remote_host}:{remote_port}',
                    f'{ssh_user}@{ssh_host}'
                    ]
                    start_command = subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
                    stdout , stderr = start_command.communicate()
                    output = stdout
                    error = stderr
                    if start_command.returncode == 0:
                        print(f'{GREEN}[-]{END} the port_forwarding has been successfuly.....')
                        print(output)
                    if error:
                        print(f'{RED}[~]{END} error....')
                        print(f'{RED}[~]{END} error:\n{RED}[-]{END} {error}') 
                  
                if authentication == 'n' or authentication == 'N':
                    break
                if not authentication:
                    print(f'{RED}[*]{END} pleas write the right information [*]')
                    print(f'{RED}[*]{END} exit : <n or N> [*]')
                    continue

            except Exception as e:
                print(f'\n{RED}[~]{END} error.....')
                print(f'{RED}[~]{END} {e}')
            except KeyboardInterrupt:
                print(f'\n{RED}[~]{END} <<Ctr +c>> :)')
            except FileNotFoundError as file:
                print(f'\n{RED}[~]{END} file ssh-key not found:\n[~] {file}')


    def port_forwarding_remote(self):
        if not self.ssh_clint:
            print(f'{RED}[~]{END} there is somthings wrong in the SSH connecting....\n<pleas check that>')
            return
        while True:
            try:
                ssh_host = self.host2
                ssh_user = self.username2

                print(f'{BLUE}[-]{END} welcom to ssh <port_forwarding_remote>.....')
                print(f'{BLUE}[-]{END} pleas wait....')
                time.sleep(1)
                print(f'{BLUE}[-]{END} filling thise information:')
                remote_port = input(f'{BLUE}[-]{END} remote port>>>')
                if remote_port.lower() == 'n':
                    break
                local_host = input(f'{BLUE}[-]{END} localhost << defald:127.0.0.1 >> >>>')
                if local_host.lower() == 'n':
                    break
                if not local_host:
                    local_host = '127.0.0.1'
                local_port = input(f'{BLUE}[-]{END} local-port>>>')
                if local_port.lower() == 'n':
                    break
                path_key = input(f'{BLUE}[-]{END} your ssh-key path>>>')
                if path_key.lower == 'n':
                    break
                accept_informations = input(f'{RED}[*]{END} are you sure that your unformation is right <y,n>:\n[1] remote-port = {remote_port}\n[2] localhost = {local_host}\n[3] local-port = {local_port}\n[4] path-key = {path_key}\n>>>')

                if accept_informations.lower() == 'y':
                    print(f'{RED}[-]{END} start....')
                    command = [
                    'ssh',
                    '-i', path_key,
                    '-o','StrictHostKeyChecking=no',
                    '-N',
                    '-L',f'{remote_port}:{local_host}:{local_port}',
                    f'{ssh_user}@{ssh_host}'
                    ]

                    response = subprocess.Popen(command,stdout=PIPE,stderr=PIPE,text=True)
                    stdout , stderr = response.communicate()
                    output = stdout
                    error = stderr
                    if response.returncode == 0:
                        print(f'{GREEN}[-]{END} the port-forwarding has been success....')
                        print(f'{GREEN}[-]{END} response:\n{output}')
                    if error:
                        print(f'{RED}[~]{END} error:')
                        print(f'{RED}[~]{END} {error}')


                if accept_informations.lower() == 'n':
                    break
                if not accept_informations:
                    print(f'{RED}[*]{END} pleas accept your informations or for exit type <exit> [*]')
                    continue
            except Exception as ex:
                print(f'\n{RED}[~]{END} Error:\n[~] {ex}')
            except KeyboardInterrupt:
                break
            except FileNotFoundError as file:
                print(f'\n{RED}[~]{END} file not found error:\n[~] {file}')

    
    def close_ssh_con(self):
        if self.ssh_clint:
            self.ssh_clint.close()
            print(f'\n{RED}[~]{END} SSH connecting close.....')

    def help_meno(self):
        help = (f'''
                help meno
/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/
{GREEN}What is ssh_con tool??{END} /-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/
    this is a tool for helping you for working with ssh_protokol /-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/
    esyer than later. /-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/
/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/
{GREEN}for more informations:{END} /-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/
    serching: /-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/
            {YELLOW}what is ssh_protocol?{END} /-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/
            {YELLOW}what is port forwarding?{END}  /-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/
            {YELLOW}how can i run a ssh server?{END} /-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/
            and etc..... /-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/
/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/              
{GREEN}but if you know all thise:{END} /-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/
i explain you something that how this tool work. /-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/
    just write your ip address and username in this form --> /-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/
            {RED}run = start('192.168.121.134','toor',password){END} /-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/
    then run the tool and write your ssh_password. /-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/
    then accesp your choise. /-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/
/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/
{BLUE}<i,ll hope to help you>{END} /-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/
/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/
''')
        print(help)
        return

if __name__ == "__main__":
    import getpass
    try:
        password = getpass.getpass(f'{BLUE}[-]{END} writing your ssh password pleas:>>>')
        if not password:
            while not password:
                print(f'{RED}[~]{END} pleas password.')
                password = getpass.getpass(f'{BLUE}[*]{END} writing your ssh password pleas:>>>')
    except KeyboardInterrupt:
        sys.exit()

    run = start('111.111.111.111','your username',password)
    if run.ssh_clint:
        while True:
            try:
                print("Meno:")
                print(f"""
{YELLOW}[1]{END} Runnign Command
{YELLOW}[2]{END} Dowloding File
{YELLOW}[3]{END} Uploding File
{YELLOW}[4]{END} Port Forwarding <local>
{YELLOW}[5]{END} Port Forwarding <Remote>
{YELLOW}[6]{END} Help
{RED}[7]{END} Exit
            """)
                user__input = input(">>>")
                if user__input == '1':
                    run.runing_command()
                elif user__input == '2':
                    run.file_downloding()
                elif user__input == '3':
                    run.file_sending()
                elif user__input == '4':
                    run.port_forwarding_local()
                elif user__input == '5':
                    run.port_forwarding_remote()
                elif user__input == "6":
                    run.help_meno()
                elif user__input == '7':
                    run.close_ssh_con()
                    sys.exit(f'{RED}[~]{END} the <ssh_con> brake.....')
                else:
                    print(f'{RED}[*]{END} invalid option!! [*]')
                    print(f'{RED}[~]{END} checking your input pleas....')
                    continue
            except Exception as e:
                print(f'\n{RED}[~]{END} error\n[-] {e}')
            except KeyboardInterrupt:
                run.close_ssh_con()
                sys.exit(f'{RED}[~]{END} the <ssh_con> brake.....')


    if not run.ssh_clint:
        sys.exit(f'{RED}[~]{END} ssh connection FALSE....\npleas check your <<SSH_CONNECTION>>....')            
