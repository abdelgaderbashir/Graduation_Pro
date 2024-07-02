import re
from openai import OpenAI
from colorama import Fore

def read_file_content(file_path):
  with open(file_path, "r") as file:
      content = file.read()
  return content

def api_call(user_input):
  try:
    # Point to the local server
    client = OpenAI(base_url="http://localhost:4444/v1", api_key="not-needed")
    temp = "modify the provided code with the required inputs needed, that make the code doesn't need any more inputs from the user. if you know that the variables you have are: {'ip':'192.168.48.135'}. Don't make the code ask the user for inputs, i will take the code from you to run in without giving any inputs for it. you can remove the 'argparse' section and directly assign the IP address to the host variable"
    content = temp + "\n" + user_input
    completion = client.chat.completions.create(
        model="local-model",  # this field is currently unused
        messages=[
            {"role": "user", "content": content}
        ],
        temperature=0.8,
    )

    response = completion.choices[0].message.content  # Extract content from the response object
    print("Response from API:", response)

    python_code_match = re.search(r'```python3?\s*(.*?)\s*```', response, re.DOTALL) # Extracting the Python and python3 code using regex
    # python_code_match = re.search(r'```python3?\n(.+?)\n```', response, re.DOTALL) for LM at pc !
    if python_code_match:
        python_code = python_code_match.group(1)
        print("Extracted Python code:", python_code)

        file_path = "output_file.py"
        # Write the extracted Python code to the file
        with open(file_path, "w") as file:
            file.write(python_code)
        print(f"{Fore.GREEN}[+] The Python code has been written to {file_path} {Fore.WHITE}")
        return True
    else:
        print(f"{Fore.RED}[-] No Python code found in the response. {Fore.WHITE}")
        return False
  except Exception as e:
    print(f"{Fore.RED}[-] Error occurred while connecting to the API: {e} {Fore.WHITE}")
    return False


if __name__ == "__main__":
  user_input = ""
  file_path = "49757"
  file_content = read_file_content(file_path)
  api_call(file_content)
