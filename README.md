(chatgpt generated this readme and I didn't actually read it.  yolo & ymmv)

# Code Generation Application

This application is a powerful code generation tool, which uses OpenAI's language model, GPT-3.5-turbo, to generate code based on a user's intent. The application is based on the original work which you can find at [smol-ai/developer](https://github.com/smol-ai/developer).

## How it works

The application takes a user's intent as input, and then proceeds to generate a list of filepaths that would be required to create the program based on the intent. It also generates a list of packages and their versions that the files will depend on. 

After generating the list of filepaths and dependencies, the application generates the actual code for each file in the list. The code is written to be valid for the specific file type, and care is taken to ensure that filenames are consistent across all generated files.

The application also generates shared dependencies, which includes exported variables, data schemas, id names of DOM elements that JavaScript functions will use, message names, and function names. These shared dependencies are written to a markdown file in the generated directory.

## Running the Application

To run the application, you would use the following command:

```bash
python main.py 'Your prompt here'
```

Replace `'Your prompt here'` with your intended prompt. If your prompt is a markdown file, you can pass the file's name instead.

Please note that you need to have OpenAI API key set in your environment variables for the application to work.

## Contributing

This project is open for contributions. If you find any issues or if you want to suggest any improvements, feel free to open an issue or a pull request.

## License

This project is licensed under the terms of the MIT license. You are free to use, modify, and distribute the code as you see fit. 

Please note that while the application is designed to generate accurate and useful code, it is always a good idea to review and test any generated code before using it in a production environment.

## Acknowledgements

This project would not be possible without the hard work and dedication of the original authors at smol-ai. We are grateful for their contributions and for making their work available for others to use and learn from.