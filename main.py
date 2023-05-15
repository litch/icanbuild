from dotenv import load_dotenv
import sys
import os
import ast
import openai
import tiktoken

# load secrets from .env
load_dotenv()

# get the open api key from the secrets
open_api_key = os.getenv("OPENAI_API_KEY")


generated_dir = "generated"

openai_model = "gpt-3.5-turbo"

openai_model_max_tokens = 2000

def report_tokens(prompt):
    encoding = tiktoken.encoding_for_model(openai_model)
    print("\033[37m" + str(len(encoding.encode(prompt))) + " tokens\033[0m" + " in prompt: " + "\033[92m" + prompt[:50] + "\033[0m")

def generate_response(system_prompt, user_prompt, *args):

    openai.api_key = open_api_key
    messages = []
    messages.append({"role": "system", "content": system_prompt})
    report_tokens(system_prompt)
    messages.append({"role": "user", "content": user_prompt})   
    report_tokens(user_prompt)

    role = "assistant"

    for value in args:
        messages.append({"role": role, "content": value})
        report_tokens(value)
        role = "user" if role == "assistant" else "assistant"
    
    params = {
        "model": openai_model,
        "max_tokens": openai_model_max_tokens,
        "temperature": 0,
        "messages": messages,
    }

    response = openai.ChatCompletion.create(**params)

    reply = response.choices[0]["message"]["content"]
    return reply

def generate_file(filename, filepaths_string=None, shared_dependencies=None, prompt=None):
    filecode = generate_response(
        f"""You are an AI developer who is trying to write a program that will generate code for the user based on their intent.
        
    the app is: {prompt}

    the files we have decided to generate are: {filepaths_string}

    the shared dependencies (like filenames, variable names, and package versions) we have decided on are: {shared_dependencies}

    only write valid code for the given filepath and file type, and return only the code.
    do not add any other explanation, only return valid code for that file type.
    """,
        f"""
    We have broken up the program into per-file generation. 
    Now your job is to generate only the code for the file {filename}. 
    Make sure to have consistent filenames if you reference other files we are also generating.
    
    Remember that you must obey 3 things: 
       - you are generating code for the file {filename}
       - do not stray from the names of the files and the shared dependencies we have decided on
       - MOST IMPORTANT OF ALL - the purpose of our app is {prompt} - every line of code you generate must be valid code. Do not include code fences in your response, for example
    
    Bad response:
    ```javascript 
    console.log("hello world")
    ```
    
    Good response:
    console.log("hello world")
    
    Begin generating the code now.

    """,
    )

    return filename, filecode

def main(prompt, directory=generated_dir, file=None):
    if prompt.endswith(".md"):
        with(open(prompt, "r")) as f:
            prompt = f.read()

    # print a few musical notes to make it look like we're doing something
    print("\033[92m" + "♫♪♫♪♫♪♫♪♫♪♫♪♫♪♫♪♫♪♫♪♫♪" + "\033[0m")    
    print("It's me, hi")
    print("I'm going to generate code for you based on your intent.")
    print("\033[92m" + prompt + "\033[0m")

    filepaths_string = generate_response(
        """You are an AI developer who is trying to write a program that will generate code for the user based on their intent.
        
    When given their intent, create a complete, exhaustive list of filepaths that the user would write to make the program.

    only list the filepaths you would write, and return them as a python list of strings. 
    do not add any other explanation, only return a python list of strings.
    """,
        prompt,
    )

    print("Filepaths: " + filepaths_string)

    dependencies_string = generate_response(
        """You are an AI developer who is trying to write a program that will generate code for the user based on their intent. 

        The prompt is: {prompt} and the list of files we will generate is {filepaths_string}

        Now we will consider which packages these will depend on.

        Please write a list of packages and versions that these files will depend on

        Then list the packages as a python list of strings.
        do not add any other explanation, only return a python list of strings.
        """,

        prompt,)
    
    package_list_actual = []
    try:
        package_list_actual = ast.literal_eval(dependencies_string)
    except ValueError:
        print("Failed to parse result: " + dependencies_string)
        print("Yolo let's continue")

    # parse the result into a python list
    list_actual = []
    try:
        list_actual = ast.literal_eval(filepaths_string)

        # if shared_dependencies.md is there, read it in, else set it to None
        shared_dependencies = None
        if os.path.exists("shared_dependencies.md"):
            with open("shared_dependencies.md", "r") as shared_dependencies_file:
                shared_dependencies = shared_dependencies_file.read()

        if file is not None:
            # check file
            print("file", file)
            filename, filecode = generate_file(file, filepaths_string=filepaths_string, shared_dependencies=shared_dependencies, prompt=prompt)
            write_file(filename, filecode, directory)
        else:
            clean_dir(directory)

            # understand shared dependencies
            shared_dependencies = generate_response(
                """You are an AI developer who is trying to write a program that will generate code for the user based on their intent.
                
            In response to the user's prompt:

            ---
            the app is: {prompt}
            ---
            
            the files we have decided to generate are: {filepaths_string}

            Now that we have a list of files, we need to understand what dependencies they share.
            Please name and briefly describe what is shared between the files we are generating, including exported variables, data schemas, id names of every DOM elements that javascript functions will use, message names, and function names.
            Exclusively focus on the names of the shared dependencies, and do not add any other explanation.



            """,
                prompt,
            )
            print(shared_dependencies)
            # write shared dependencies as a md file inside the generated directory
            write_file("shared_dependencies.md", shared_dependencies, directory)
            
            # Existing for loop
            # for filename, filecode in generate_file.map(
            #     list_actual, order_outputs=False, kwargs=dict(filepaths_string=filepaths_string, shared_dependencies=shared_dependencies, prompt=prompt)
            # ):
            #     write_file(filename, filecode, directory)

            for l in list_actual:
                print(l)
                filename, filecode = generate_file(l, filepaths_string=filepaths_string, shared_dependencies=shared_dependencies, prompt=prompt)
                write_file(filename, filecode, directory)
            


    except ValueError:
        print("Failed to parse result: " + result)


def write_file(filename, filecode, directory):
    # Output the filename in blue color
    print("\033[94m" + filename + "\033[0m")
    print(filecode)

    # if the filename includes a path, make sure the directory exists
    if "/" in filename:
        os.makedirs(os.path.dirname(directory + "/" + filename), exist_ok=True)

    # Open the file in write mode
    with open(directory + "/" + filename, "w") as file:
        # Write content to the file
        file.write(filecode)


def clean_dir(directory):
    import shutil

    extensions_to_skip = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg', '.ico', '.tif', '.tiff']  # Add more extensions if needed

    # Check if the directory exists
    if os.path.exists(directory):
        # If it does, iterate over all files and directories
        for root, dirs, files in os.walk(directory):
            for file in files:
                _, extension = os.path.splitext(file)
                if extension not in extensions_to_skip:
                    os.remove(os.path.join(root, file))
    else:
        os.makedirs(directory, exist_ok=True)

if __name__ == "__main__":
    if len(sys.argv) > 1:

        main(sys.argv[1])
    else:
        print("Please provide a prompt.")