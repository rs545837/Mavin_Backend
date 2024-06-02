import os
from anthropic import Anthropic
import re
from rich.console import Console
from rich.panel import Panel
from datetime import datetime
import json
from tavily import TavilyClient
import pypandoc
from google.cloud import storage, translate_v2 as translate
from gcs import upload_pdf_to_gcs, upload_audio_to_gcs
from deep_translator import GoogleTranslator
from openai import OpenAI
import os
from PyPDF2 import PdfReader
import requests
import io, random, string
from elevenlabs.client import ElevenLabs
from elevenlabs import play, stream, save
from io import BytesIO
from PIL import Image
import soundfile as sf
import uuid
from twilio.rest import Client
import agentops

agentops.init('YOUR_API_KEY')

pypandoc.download_pandoc()

TAVILY_API_KEY = os.environ['TAVILY_API_KEY']
CLAUDE_API_KEY = os.environ['CLAUDE_API_KEY']
OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
GROQ_API_KEY = os.environ['GROQ_API_KEY']

# Set up the GROQ API client
# Set up the Groq API client
from groq import Groq
import os

client = Groq(api_key=GROQ_API_KEY)

# Initialize OpenAI and Anthropic API clients
openai_client = OpenAI(
    api_key='')
anthropic_client = Anthropic(api_key=CLAUDE_API_KEY)

# Available OpenAI models
ORCHESTRATOR_MODEL = "gpt-4o"
SUB_AGENT_MODEL = "llama3-70b-8192"

# Available Claude models for Anthropic API
REFINER_MODEL = "claude-3-opus-20240229"

# Define constants for the script
CHUNK_SIZE = 1024  # Size of chunks to read/write at a time
XI_API_KEY = "fe63b0a68ae7c10e5c97ca6ca03a24b7"  # Your API key for authentication
VOICE_ID = "zyz0WAi2EB3lPpxsZWNY"  # ID of the voice model to use

account_sid = os.getenv('TWILIO_SID')
auth_token = os.getenv('TWILIO_TOKEN')


def transcript_audio(media_url: str) -> dict:
    try:
        ogg_file_path = f'{os.getcwd()}/{uuid.uuid1()}.ogg'
        response = requests.get(media_url, auth=(account_sid, auth_token))

        if response.status_code == 200:
            with open(ogg_file_path, 'wb') as file:
                file.write(response.content)

            audio_data, sample_rate = sf.read(ogg_file_path)
            mp3_file_path = f'{os.getcwd()}/{uuid.uuid1()}.mp3'
            sf.write(mp3_file_path, audio_data, sample_rate)

            with open(mp3_file_path, 'rb') as audio_file:
                transcript_response = openai_client.audio.transcriptions.create(
                    model="whisper-1", file=audio_file)
            print(transcript_response)
            transcript_text = transcript_response.text
            print(transcript_text)
            os.unlink(ogg_file_path)
            os.unlink(mp3_file_path)

            return {'status': 1, 'transcript': transcript_text}
        else:
            return {'status': 0, 'error': 'Failed to download audio file'}
    except Exception as e:
        print('Error at transcript_audio...')
        print(e)
        return {'status': 0, 'transcript': transcript['text']}


def generate_image(objective):

    # Read the image file from disk and resize it
    image = Image.open("image.png")
    width, height = 1024, 576  # Landscape dimensions (example)
    image = image.resize((width, height))

    # Convert the image to a BytesIO object
    byte_stream = BytesIO()
    image.save(byte_stream, format='PNG')
    byte_array = byte_stream.getvalue()

    response = openai_client.images.create_variation(image=byte_array,
                                                     n=1,
                                                     model="dall-e-2",
                                                     size="1024,1024")

    # Return the URL of the generated image
    return response['data'][0]['url']


def download_image(image_url, image_filename):
    response = requests.get(image_url)
    with open(image_filename, 'wb') as file:
        file.write(response.content)


def extract_text_from_pdf(pdf_url):
    print(f"Extracting text from PDF URL: {pdf_url}")
    response = requests.get(pdf_url)
    print(f"PDF downloaded. Status code: {response.status_code}")

    if response.status_code == 200:
        pdf_data = io.BytesIO(response.content)
        reader = PdfReader(pdf_data)
        text = ''
        for page in reader.pages:
            text += page.extract_text()
        print(f"Extracted text from PDF. Length: {len(text)}")
        return text
    else:
        print(f"Failed to download PDF. Status code: {response.status_code}")
        return None


# def generate_audio_from_text(text):
#     response = openai_client.audio.speech.create(model="tts-1-hd",
#                                                  voice="alloy",
#                                                  input=text)
#     print(f"Audio Generated:")
#     audio_file_path = datetime.now().strftime(
#         "%Y%m%d_%H%M%S") + "audiobook.mp3"
#     with open(audio_file_path, 'wb') as audio_file:
#         audio_file.write(response.content)
#     # Upload the audio file to a storage service and return the URL
#     # For example, using Google Cloud Storage or AWS S3
#     audiobook_url = upload_audio_to_gcs(
#         "this-is-goat", audio_file_path,
#         audio_file_path)  # Define this function based on your storage service

#     return audiobook_url


def generate_audio_from_text(text):
    # Construct the URL for the Text-to-Speech API request
    tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}/stream"

    # Set up headers for the API request, including the API key for authentication
    headers = {"Accept": "application/json", "xi-api-key": XI_API_KEY}

    # Set up the data payload for the API request, including the text and voice settings
    data = {
        "text": text,
        "model_id": "eleven_multilingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.8,
            "style": 0.0,
            "use_speaker_boost": True
        }
    }

    # Make the POST request to the TTS API with headers and data, enabling streaming response
    response = requests.post(tts_url, headers=headers, json=data, stream=True)

    # Check if the request was successful
    if response.ok:
        print("Audio Generated:")
        audio_file_path = datetime.now().strftime(
            "%Y%m%d_%H%M%S") + "_audiobook.mp3"

        # Open the output file in write-binary mode
        with open(audio_file_path, "wb") as audio_file:
            # Read the response in chunks and write to the file
            for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                audio_file.write(chunk)

        # Upload the audio file to a storage service and return the URL
        # For example, using Google Cloud Storage or AWS S3
        audiobook_url = upload_audio_to_gcs("this-is-goat", audio_file_path,
                                            audio_file_path)
        return audiobook_url
    else:
        print("Error generating audio:", response.text)
        return None


def translate_md_to_hinglish(md_file_path, translated_md_file_path):
    with open(md_file_path, 'r', encoding='utf-8') as md_file:
        md_content = md_file.read()

    messages = [{
        "role":
        "user",
        "content": [{
            "type":
            "text",
            "text":
            f"Please translate the following Hindi text to Hindi Roman font. Change everything to hinglish except the headings. The output should only be the translation of Refined Final Output and nothing else. :\n\n{md_content}"
        }]
    }]

    haiku_response = anthropic_client.messages.create(model=REFINER_MODEL,
                                                      max_tokens=4096,
                                                      messages=messages)

    translated_md_content = haiku_response.content[0].text.strip()

    with open(translated_md_file_path, 'w',
              encoding='utf-8') as translated_md_file:
        translated_md_file.write(translated_md_content)


def translate_text(text, target_language):
    translate_client = translate.Client()
    result = translate_client.translate(text, target_language=target_language)
    return result['translatedText']


def translate_md(md_file_path, translated_md_file_path, target_language='hi'):
    # Read the content of the Markdown file
    with open(md_file_path, 'r', encoding='utf-8') as md_file:
        md_content = md_file.read()

    # Split content into lines to maintain Markdown formatting
    md_lines = md_content.split('\n')
    translated_lines = []

    # Translate each line
    for line in md_lines:
        translated_line = translate_text(line, target_language)
        translated_lines.append(translated_line)

    # Join translated lines
    translated_md_content = '\n'.join(translated_lines)

    # Write the translated content to a new Markdown file
    with open(translated_md_file_path, 'w',
              encoding='utf-8') as translated_md_file:
        translated_md_file.write(translated_md_content)


def convert_md_to_pdf(md_file_path, pdf_file_path):
    try:
        output = pypandoc.convert_file(md_file_path,
                                       'pdf',
                                       outputfile=pdf_file_path,
                                       extra_args=['--pdf-engine=xelatex'])
        print(f"PDF file has been created: {pdf_file_path}")
    except RuntimeError as e:
        print(f"An error occurred: {e}")
    return True


def calculate_subagent_cost(model, input_tokens, output_tokens):
    # Pricing information per model
    pricing = {
        "claude-3-opus-20240229": {
            "input_cost_per_mtok": 15.00,
            "output_cost_per_mtok": 75.00
        },
        "claude-3-haiku-20240307": {
            "input_cost_per_mtok": 0.25,
            "output_cost_per_mtok": 1.25
        },
        "claude-3-sonnet-20240229": {
            "input_cost_per_mtok": 3.00,
            "output_cost_per_mtok": 15.00
        },
    }

    # Calculate cost
    input_cost = (input_tokens /
                  1_000_000) * pricing[model]["input_cost_per_mtok"]
    output_cost = (output_tokens /
                   1_000_000) * pricing[model]["output_cost_per_mtok"]
    total_cost = input_cost + output_cost

    return total_cost


# Initialize the Rich Console
console = Console()


def gpt_orchestrator(objective,
                     file_content=None,
                     previous_results=None,
                     use_search=False):
    console.print(f"\n[bold]Calling Orchestrator for your objective[/bold]")
    previous_results_text = "\n".join(
        previous_results) if previous_results else "None"
    if file_content:
        console.print(
            Panel(f"File content:\n{file_content}",
                  title="[bold blue]File Content[/bold blue]",
                  title_align="left",
                  border_style="blue"))

    messages = [{
        "role": "system",
        "content": "You are a helpful assistant."
    }, {
        "role":
        "user",
        "content":
        f"Based on the following objective{' and file content' if file_content else ''}, and the previous sub-task results (if any), please break down the objective into the next sub-task, and create a concise and detailed prompt for a subagent so it can execute that task. IMPORTANT!!! when dealing with code tasks make sure you check the code for errors and provide fixes and support as part of the next sub-task. If you find any bugs or have suggestions for better code, please include them in the next sub-task prompt. Please assess if the objective has been fully achieved. If the previous sub-task results comprehensively address all aspects of the objective, include the phrase 'The task is complete:' at the beginning of your response. If the objective is not yet fully achieved, break it down into the next sub-task and create a concise and detailed prompt for a subagent to execute that task. Don't try to deploy more than 3 sub-agents until told so seperately.\n\nObjective: {objective}"
        + ('\nFile content:\n' + file_content if file_content else '') +
        f"\n\nPrevious sub-task results:\n{previous_results_text}"
    }]

    if use_search:
        messages.append({
            "role":
            "user",
            "content":
            "Please also generate a JSON object containing a single 'search_query' key, which represents a question that, when asked online, would yield important information for solving the subtask. The question should be specific and targeted to elicit the most relevant and helpful resources. Format your JSON like this, with no additional text before or after:\n{\"search_query\": \"<question>\"}\n"
        })

    gpt_response = openai_client.chat.completions.create(
        model=ORCHESTRATOR_MODEL, messages=messages, max_tokens=4096)

    response_text = gpt_response.choices[0].message.content
    usage = gpt_response.usage

    console.print(
        Panel(response_text,
              title=f"[bold green]gpt Orchestrator[/bold green]",
              title_align="left",
              border_style="green",
              subtitle="Sending task to gpt 👇"))
    console.print(
        f"Input Tokens: {usage.prompt_tokens}, Output Tokens: {usage.completion_tokens}, Total Tokens: {usage.total_tokens}"
    )

    search_query = None
    if use_search:
        json_match = re.search(r'{.*}', response_text, re.DOTALL)
        if json_match:
            json_string = json_match.group()
            try:
                search_query = json.loads(json_string)["search_query"]
                console.print(
                    Panel(f"Search Query: {search_query}",
                          title="[bold blue]Search Query[/bold blue]",
                          title_align="left",
                          border_style="blue"))
                response_text = response_text.replace(json_string, "").strip()
            except json.JSONDecodeError as e:
                console.print(
                    Panel(f"Error parsing JSON: {e}",
                          title="[bold red]JSON Parsing Error[/bold red]",
                          title_align="left",
                          border_style="red"))
                console.print(
                    Panel(
                        f"Skipping search query extraction.",
                        title=
                        "[bold yellow]Search Query Extraction Skipped[/bold yellow]",
                        title_align="left",
                        border_style="yellow"))
        else:
            search_query = None

    return response_text, file_content, search_query


def gpt_sub_agent(prompt,
                  search_query=None,
                  previous_gpt_tasks=None,
                  use_search=False,
                  continuation=False):
    if previous_gpt_tasks is None:
        previous_gpt_tasks = []

    continuation_prompt = "Continuing from the previous answer, please complete the response."
    system_message = "Previous gpt tasks:\n" + "\n".join(
        f"Task: {task['task']}\nResult: {task['result']}"
        for task in previous_gpt_tasks)
    if continuation:
        prompt = continuation_prompt

    qna_response = None
    if search_query and use_search:
        tavily = TavilyClient(api_key=TAVILY_API_KEY)
        qna_response = tavily.qna_search(query=search_query)
        console.print(f"QnA response: {qna_response}", style="yellow")

    messages = [{
        "role": "system",
        "content": system_message
    }, {
        "role": "user",
        "content": prompt
    }]

    if qna_response:
        messages.append({
            "role": "user",
            "content": f"\nSearch Results:\n{qna_response}"
        })

    gpt_response = client.chat.completions.create(model=SUB_AGENT_MODEL,
                                                  messages=messages,
                                                  max_tokens=8000)

    response_text = gpt_response.choices[0].message.content
    usage = gpt_response.usage

    console.print(
        Panel(response_text,
              title="[bold blue]gpt Sub-agent Result[/bold blue]",
              title_align="left",
              border_style="blue",
              subtitle="Task completed, sending result to gpt 👇"))
    console.print(
        f"Input Tokens: {usage.prompt_tokens}, Output Tokens: {usage.completion_tokens}, Total Tokens: {usage.total_tokens}"
    )

    if usage.completion_tokens >= 4000:  # Threshold set to 4000 as a precaution
        console.print(
            "[bold yellow]Warning:[/bold yellow] Output may be truncated. Attempting to continue the response."
        )
        continuation_response_text = gpt_sub_agent(prompt,
                                                   search_query,
                                                   previous_gpt_tasks,
                                                   use_search,
                                                   continuation=True)
        response_text += continuation_response_text

    return response_text


def anthropic_refine(objective,
                     sub_task_results,
                     filename,
                     projectname,
                     continuation=False):
    console.print(
        "\nCalling Opus to provide the refined final output for your objective:"
    )
    messages = [{
        "role":
        "user",
        "content": [{
            "type":
            "text",
            "text":
            "Objective: " + objective + "\n\nSub-task results:\n" +
            "\n".join(sub_task_results) +
            "\n\nPlease review and refine the sub-task results into a cohesive final output. Add any missing information or details as needed. When working on code projects, ONLY AND ONLY IF THE PROJECT IS CLEARLY A CODING ONE please provide the following:\n1. Project Name: Create a concise and appropriate project name that fits the project based on what it's creating. The project name should be no more than 20 characters long.\n2. Folder Structure: Provide the folder structure as a valid JSON object, where each key represents a folder or file, and nested keys represent subfolders. Use null values for files. Ensure the JSON is properly formatted without any syntax errors. Please make sure all keys are enclosed in double quotes, and ensure objects are correctly encapsulated with braces, separating items with commas as necessary.\nWrap the JSON object in <folder_structure> tags.\n3. Code Files: For each code file, include ONLY the file name NEVER EVER USE THE FILE PATH OR ANY OTHER FORMATTING YOU ONLY USE THE FOLLOWING format 'Filename: <filename>' followed by the code block enclosed in triple backticks, with the language identifier after the opening backticks, like this:\n\n```python\n<code>\n```"
        }]
    }]

    opus_response = anthropic_client.messages.create(model=REFINER_MODEL,
                                                     max_tokens=4096,
                                                     messages=messages)

    response_text = opus_response.content[0].text.strip()
    console.print(
        f"Input Tokens: {opus_response.usage.input_tokens}, Output Tokens: {opus_response.usage.output_tokens}"
    )
    total_cost = calculate_subagent_cost(REFINER_MODEL,
                                         opus_response.usage.input_tokens,
                                         opus_response.usage.output_tokens)
    console.print(f"Refine Cost: ${total_cost:.4f}")

    if opus_response.usage.output_tokens >= 4000 and not continuation:  # Threshold set to 4000 as a precaution
        console.print(
            "[bold yellow]Warning:[/bold yellow] Output may be truncated. Attempting to continue the response."
        )
        continuation_response_text = anthropic_refine(objective,
                                                      sub_task_results +
                                                      [response_text],
                                                      filename,
                                                      projectname,
                                                      continuation=True)
        response_text += "\n" + continuation_response_text

    console.print(
        Panel(response_text,
              title="[bold green]Final Output[/bold green]",
              title_align="left",
              border_style="green"))
    return response_text


def create_folder_structure(project_name, folder_structure, code_blocks):
    # Create the project folder
    try:
        os.makedirs(project_name, exist_ok=True)
        console.print(
            Panel(f"Created project folder: [bold]{project_name}[/bold]",
                  title="[bold green]Project Folder[/bold green]",
                  title_align="left",
                  border_style="green"))
    except OSError as e:
        console.print(
            Panel(
                f"Error creating project folder: [bold]{project_name}[/bold]\nError: {e}",
                title="[bold red]Project Folder Creation Error[/bold red]",
                title_align="left",
                border_style="red"))
        return

    # Recursively create the folder structure and files
    create_folders_and_files(project_name, folder_structure, code_blocks)


def create_folders_and_files(current_path, structure, code_blocks):
    for key, value in structure.items():
        path = os.path.join(current_path, key)
        if isinstance(value, dict):
            try:
                os.makedirs(path, exist_ok=True)
                console.print(
                    Panel(f"Created folder: [bold]{path}[/bold]",
                          title="[bold blue]Folder Creation[/bold blue]",
                          title_align="left",
                          border_style="blue"))
                create_folders_and_files(path, value, code_blocks)
            except OSError as e:
                console.print(
                    Panel(
                        f"Error creating folder: [bold]{path}[/bold]\nError: {e}",
                        title="[bold red]Folder Creation Error[/bold red]",
                        title_align="left",
                        border_style="red"))
        else:
            code_content = next(
                (code for file, code in code_blocks if file == key), None)
            if code_content:
                try:
                    with open(path, 'w') as file:
                        file.write(code_content)
                    console.print(
                        Panel(f"Created file: [bold]{path}[/bold]",
                              title="[bold green]File Creation[/bold green]",
                              title_align="left",
                              border_style="green"))
                except IOError as e:
                    console.print(
                        Panel(
                            f"Error creating file: [bold]{path}[/bold]\nError: {e}",
                            title="[bold red]File Creation Error[/bold red]",
                            title_align="left",
                            border_style="red"))
            else:
                console.print(
                    Panel(
                        f"Code content not found for file: [bold]{key}[/bold]",
                        title="[bold yellow]Missing Code Content[/bold yellow]",
                        title_align="left",
                        border_style="yellow"))


def read_file(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
    return content


def generate_pdf(objective, use_search, language_preference):
    task_exchanges = []
    gpt_tasks = []

    file_content = None

    max_iterations = 3  # Set the maximum number of iterations

    iteration_count = 0

    while iteration_count < max_iterations:
        previous_results = [result for _, result in task_exchanges]
        if not task_exchanges:
            gpt_result, file_content_for_gpt, search_query = gpt_orchestrator(
                objective, file_content, previous_results, use_search)
        else:
            gpt_result, _, search_query = gpt_orchestrator(
                objective,
                previous_results=previous_results,
                use_search=use_search)

        if "The task is complete:" in gpt_result:
            final_output = gpt_result.replace("The task is complete:",
                                              "").strip()
            break
        else:
            sub_task_prompt = gpt_result
            if file_content_for_gpt and not gpt_tasks:
                sub_task_prompt = f"{sub_task_prompt}\n\nFile content:\n{file_content_for_gpt}"
            sub_task_result = gpt_sub_agent(sub_task_prompt, search_query,
                                            gpt_tasks, use_search)
            gpt_tasks.append({
                "task": sub_task_prompt,
                "result": sub_task_result
            })
            task_exchanges.append((sub_task_prompt, sub_task_result))
            file_content_for_gpt = None

        iteration_count += 1

    sanitized_objective = re.sub(r'\W+', '_', objective)
    timestamp = datetime.now().strftime("%H-%M-%S")
    refined_output = anthropic_refine(objective,
                                      [result for _, result in task_exchanges],
                                      timestamp, sanitized_objective)

    project_name_match = re.search(r'Project Name: (.*)', refined_output)
    project_name = project_name_match.group(
        1).strip() if project_name_match else sanitized_objective

    folder_structure_match = re.search(
        r'<folder_structure>(.*?)</folder_structure>', refined_output,
        re.DOTALL)
    folder_structure = {}
    if folder_structure_match:
        json_string = folder_structure_match.group(1).strip()
        try:
            folder_structure = json.loads(json_string)
        except json.JSONDecodeError as e:
            console.print(
                Panel(f"Error parsing JSON: {e}",
                      title="[bold red]JSON Parsing Error[/bold red]",
                      title_align="left",
                      border_style="red"))
            console.print(
                Panel(f"Invalid JSON string: [bold]{json_string}[/bold]",
                      title="[bold red]Invalid JSON String[/bold red]",
                      title_align="left",
                      border_style="red"))

    # Ensure proper extraction of filenames and code contents
    code_blocks = re.findall(r'Filename: (\S+)\s*```[\w]*\n(.*?)\n```',
                             refined_output, re.DOTALL)
    create_folder_structure(project_name, folder_structure, code_blocks)

    max_length = 25
    truncated_objective = sanitized_objective[:max_length] if len(
        sanitized_objective) > max_length else sanitized_objective

    filename = f"{timestamp}_{truncated_objective}.md"

    # Remove JSON code from the refined output
    refined_output_without_json = re.sub(
        r'<folder_structure>.*?</folder_structure>',
        '',
        refined_output,
        flags=re.DOTALL)

    # Extract the refined final output text without the heading
    refined_final_output_text = re.sub(r'^## Refined Final Output\n\n',
                                       '',
                                       refined_output_without_json,
                                       flags=re.MULTILINE)
    # Extract the refined final output text without the heading
    refined_final_output_text = re.sub(r'^## Refined Final Output\n\n',
                                       '',
                                       refined_output_without_json,
                                       flags=re.MULTILINE)

    # Translate refined_final_output_text if language preference is Hinglish
    if language_preference == 'hinglish':
        context = [{
            "role":
            "user",
            "content": [{
                "type":
                "text",
                "text":
                f"Please translate the following Hindi text to Hindi Roman font. Change everything to hinglish except the headings. Remember while us mai instead of main, karu instead of karun while writing hinglish text.:\n\n{refined_final_output_text}"
            }]
        }]

        haiku_response = anthropic_client.messages.create(model=REFINER_MODEL,
                                                          max_tokens=4096,
                                                          messages=context)
        refined_final_output_text = haiku_response.content[0].text.strip()

    # Prepare the full exchange log without JSON code
    # # Generate an image related to the topic using the OpenAI API
    # image_url = generate_image(objective)

    # # Download the image and save it to a file
    # image_filename = f"{timestamp}_{truncated_objective}.jpg"
    # download_image(image_url, image_filename)

    # # Add the image to the beginning of the Markdown content
    # exchange_log = f"![{objective}]({image_filename})\n\n" + exchange_log
    exchange_log = f"# Objective\n\n{objective}\n\n"
    exchange_log += "## Task Breakdown\n\n"
    for i, (prompt, result) in enumerate(task_exchanges, start=1):
        exchange_log += f"### Task {i}\n\n"
        exchange_log += f"**Prompt:**\n{prompt}\n\n"
        exchange_log += f"**Result:**\n{result}\n\n"
        exchange_log += "---\n\n"
    exchange_log += "## Refined Final Output\n\n"
    exchange_log += refined_output_without_json

    console.print(f"\n[bold]Refined Final output:[/bold]\n{refined_output}")

    with open(filename, 'w') as file:
        file.write(exchange_log)
    print(f"\nFull exchange log saved to {filename}")

    # Translate Markdown file if language preference is Hinglish
    if language_preference == 'hinglish':
        translated_md_file_path = filename.replace('.md', '_hinglish.md')
        translate_md_to_hinglish(filename, translated_md_file_path)
        filename = translated_md_file_path

    # Prepare the PDF filename by changing the extension
    pdf_filename = filename.replace('.md', '.pdf')
    # Convert the Markdown file to PDF
    convert_md_to_pdf(filename, pdf_filename)
    # Add the URL prefix to the pdf_filename
    # url_prefix = "/home/runner/Maestro/"
    # pdf_url = url_prefix + pdf_filename
    pdf_url = pdf_filename
    public_url = upload_pdf_to_gcs("this-is-goat", pdf_url, pdf_filename)
    print(f"\nPDF file saved as {pdf_url}")
    return public_url, refined_final_output_text
