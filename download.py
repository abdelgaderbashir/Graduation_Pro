import os
import requests
from colorama import Fore

def exploit_download(file_path, download_dir="downloads/"):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    downloaded_files = []
    
    with open(file_path, "r") as file:
        urls = file.readlines()
    
    # Loop through each URL and download the file
    for url in urls:
        url = url.strip()  # Remove any leading/trailing whitespace
        if url:  # Check if the URL is not empty
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                filename = os.path.join(download_dir, url.split("/")[-1])
                # Create the directory if it doesn't exist
                os.makedirs(os.path.dirname(filename), exist_ok=True)
                with open(filename, "wb") as f:
                    f.write(response.content)
                downloaded_files.append(filename)
                print(f"{Fore.GREEN}[+] File downloaded: {filename} {Fore.WHITE}")
            else:
                print(f"{Fore.RED}[-] Failed to download the file. {Fore.WHITE}", response.status_code)
    
    return downloaded_files

if __name__ == "__main__":
    download_directory = "downloads/"
    file_with_urls = "Rawlinks_Exploit_DB.txt"
    downloaded_files = exploit_download(file_with_urls, download_directory)
    print(f"{Fore.BLUE}Downloaded files: {downloaded_files}{Fore.WHITE}") 

