import json
import os
import openai
from decouple import config
import click

api_key_default = config("OPENAI_API_KEY")


@click.command()
@click.option('--api_key', default=api_key_default, help='Open API Key')
@click.option('--topic', prompt='course topic',
              help='Topic of the course you wish to generate')
@click.option('--num_of_los', prompt='number of learning objectives',
              help='Number of learning objectives you wish to generate')
@click.option('--output-folder', default="generated_course", prompt='folder where you wish to output the course files')
@click.option('--output_type', prompt='json|html',
              help='What type of output do you want?')
def generate_course(api_key, topic, num_of_los, output_folder, output_type):
    openai.api_key = api_key
    # read file system.txt from the same directory
    with open("system-prompt.txt", "r") as f:
        system_prompt = f.read()

    max_tokens = 2000
    system_message = {
        "role": "system",
        "content": system_prompt
    }
    initial_request = {
        "role": "user",
        "content": f"Generate a set of {num_of_los} Learning Objectives for a course on: {topic}. Use lower levels of blooms taxnomy"
    }
    messages = [system_message, initial_request]
    cache_file = f'./cached-response-{hash(initial_request["content"])}.json'
    try:
        with open(cache_file, 'r') as file:
            response = json.load(file)
            print("Reading cached response...")
            print(response)
    except Exception as e:
        print(e)
        print("No cached response found. Generating new Learning Objective response...")
        response = openai.ChatCompletion.create(
            model="gpt-4",
            max_tokens=max_tokens,
            messages=messages,
        )
        with open(cache_file, "w") as f:
            f.write(json.dumps(response))

    generated_text = response["choices"][0]["message"]
    learning_objectives = generated_text["content"].split("\n")
    learning_objectives = [lo for lo in learning_objectives if lo != ""]
    print(learning_objectives)

    for idx, learning_objective in enumerate(learning_objectives):
        print("Generating lesson for learning objective: ", learning_objective)
        lesson_request = {
            "role": "user",
            "content": f"Generate a lesson in {output_type} format for the following learning objective {idx + 1}. Include 3 multiple choice questions. Wrap the entire response in a renderable {output_type} format as well."
        }
        curr_context = [system_message, initial_request,
                        generated_text, lesson_request]
        lesson_response = openai.ChatCompletion.create(
            model="gpt-4",
            max_tokens=max_tokens,
            messages=curr_context,
        )
        """
        Write the response to the a file.
        The title of the file should be a hash version of learning objective.
        Create the file if it does not already exist
        """
        if not os.path.exists(output_folder):
            os.mkdir(output_folder)
        with open(f"./{output_folder}/lesson-{hash(learning_objective)}.{output_type}", "w") as f:
            f.write(lesson_response.choices[0].message.content)


if __name__ == '__main__':
    generate_course()
