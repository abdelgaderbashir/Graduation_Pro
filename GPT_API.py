import os
from openai import AzureOpenAI
from  colorama import Fore
import re

def read_file_content(file_path):
  with open(file_path, "r") as file:
      content = file.read()
  return content

def api_call(file_content, collected_data):
    try:
        client = AzureOpenAI(
            azure_endpoint = os.getenv("Azure_API_Endpoint"), 
            api_key = os.getenv("Azure_API_Key"),  
            api_version = "2024-02-01"
        )

        prompt = f'''if you know these info  {collected_data}, use them to modify the code so that it works perfectly without asking the user for any inputs. 
                    Taking into consideration that not every provided piece of info is important for the code to run correctly, use the necessary ones only without changing the code's idea. 
                    Be careful not to remove or alter anything included in quotation marks.'''
        All_prompt = file_content + "\n" + prompt

        message_text = [{"role":"system", "content":"Answer the Question"}, {"role":"user", "content":All_prompt}]

        completion = client.chat.completions.create(
            model = "gpt-4o",
            messages = message_text,
            temperature = 0.7,
            max_tokens = 4096,
            top_p = 0.95,
            frequency_penalty = 0,
            presence_penalty = 0,
            stop = None
        )

        #print(completion) # print all the api res.

        response = completion.choices[0].message.content

        #print("Response from API:", response) # api res. in readable way

        # Combined regex pattern for Python, Ruby, and Perl
        code_match = re.search(r'```(python3?|ruby|perl)\s*(.*?)\s*```', response, re.DOTALL)

        if code_match:
            language = code_match.group(1)
            code = code_match.group(2)

            file_extension = {
                'python': 'py',
                'python3': 'py',
                'ruby': 'rb',
                'perl': 'pl'
            }.get(language, 'txt')

            file_path = f"output_file.{file_extension}"
            
            with open(file_path, "w") as file:
                file.write(code)

            print(f"{Fore.GREEN}[+] The {language.capitalize()} code has been written to {file_path} {Fore.WHITE}")
            return True, file_extension

        else:
            print(f"{Fore.RED}[-] No Python, Ruby, or Perl code was found in the response. {Fore.WHITE}")
            return False, 'np'

    except Exception as e:
        print(f"{Fore.RED}[-] Error occurred while connecting to the API: {e} {Fore.WHITE}")
        return False, 'npx'

if __name__ == "__main__":
  user_input = ""
  file_path = "49757"
  file_content = read_file_content(file_path)
  api_call(file_content)