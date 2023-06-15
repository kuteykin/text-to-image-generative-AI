###########################################################
#   (C) Copyright 2023 by Konstantin Kuteykin-Teplyakov   #
#                  All Rights Reserved                    #
#           ANY COMMERCIAL USE IS NOT ALLOWED             #
#        Violation of IP rights will be prosecuted        #
#                                                         #
# DISCLAIMER: This code was disclosed to general public   #
# solely for informational purposes, and any commercial   #
# use as part of software or paid service is              #
# NOT PERMITTED without written consent of IP rights      #
# owner.                                                  #
###########################################################


from images_functions import ask_chatgpt, generate_images
from flask import Flask, render_template, request, Response
from flask_cors import CORS
import json
from pathlib import Path
from re import match
from waitress import serve


app = Flask(__name__)
CORS(app)

# Get the current working directory
START_DIR = Path(__file__).parent

# Settign the working folder for given user

### For production $USER_ID is generated from Login page on Frontend #####################################
### Here the *user_id* variable is set manually for testing purposes only - REPLACE it for production  ###
user_id = "12345"
### For production MODIFY the line above #################################################################

USER_DIR = START_DIR / "Users" / user_id

# Get the list of all custom LoRA models available for given User
LORA_DIR = USER_DIR / "custom_models"
custom_model_files = [""] + sorted(
    [
        file.name
        for file in LORA_DIR.glob("*.bin")
        if match(r"^[\w-]+__[\w-]+$", file.stem) and file.is_file()
    ]
)
custom_model_prompts = [
    file.split("__")[0].replace("-", " ") for file in custom_model_files
]


# Define the constants for Stable Diffusion
parameters_file = START_DIR / "images_parameters.json"
num_images_per_prompt = 4


# Define a route for the index page
@app.route("/", methods=["GET", "POST"])
def index():
    ### Replace FRONTEND with URL on host (IP:port/path/filename.html) ##############################
    # return render_template('FRONTEND//path_on_frontend//SDiff_inference_multiuser_custom_models.html')
    return render_template(
        "SDiff_inference_multiuser_custom_models.html", custom_model_prompts=custom_model_prompts
    )


# Define a route for the inference endpoint
@app.route("/inference", methods=["POST"])
def inference():
    # Retrieve the data from the POST request from frontend

    object_style = request.form.get("object_style")
    sdiff_model_type = request.form.get("sdiff_model")
    lora_model_index = int(request.form.get("lora_index"))
    lora_prompt = custom_model_prompts[lora_model_index]
    lora_model = custom_model_files[lora_model_index]
    num_inference_steps = int(request.form.get("num_inference_steps"))
    ### PROCESSED_INPUT is a product of  user input (generated on Frontend), so modify next line accordingly ############
    processed_input = request.form.get("processed_input")

    LORA_PATH = LORA_DIR / lora_model

    print("\n*** COMMERCIAL USE IS FORBIDDEN ***\n")


    # Retrieve available image parameters from JSON file
    with open(parameters_file) as json_file:
        images_dict = json.load(json_file)
    style_prefix = images_dict["object_style"][object_style]["prompt_prefix"]
    style_suffix = images_dict["object_style"][object_style]["prompt_suffix"]
    negative_prompt = images_dict["object_style"][object_style]["negative_prompt"]
    sdiff_model = images_dict["sdiff_models"][sdiff_model_type]["name"].split("/")[-1]

    # Print the retrieved data for debugging
    print("Stable Diffusion Model selected by User: ", sdiff_model)
    print("User folder: ", USER_DIR)
    print("lora prompt=", lora_prompt)
    print("Finetuned LoRA Model (selected on Frontend): ", LORA_PATH)

    # Automatic prompt generation
    task_1 = "Photo" if object_style == "Photography" else "Image"
    chatgpt_response_prompt = ask_chatgpt(
        processed_input, task_1, images_dict["chatgpt_prompts"]
    )

    # If the LoRA finetuned model is specified and exists,
    # corresponding SDiff model will be automatically selected despite the user's selection of the base model,
    # and image promts will be generated in a different way
    if LORA_PATH.is_file():
        model_name = LORA_PATH.stem
        image_prompt = f"{lora_prompt} and {chatgpt_response_prompt}"
        sdiff_model = model_name.split("__")[-1]
    else:
        image_prompt = f"{style_prefix} {chatgpt_response_prompt}, {style_suffix}."
        model_name = sdiff_model
        LORA_PATH = ""

    MODEL_PATH = START_DIR / "HF_models" / sdiff_model

    # Print the retrieved data for debugging

    print("Basic model path: ", MODEL_PATH)
    print(
        f"Model used for image generation: {model_name} \nConstructed Prompt: {image_prompt}\n"
    )

    # Send the image bytes to the frontend
    image_response = json.dumps(
        {
            "images": generate_images(
                image_prompt=image_prompt,
                MODEL_PATH=MODEL_PATH,
                custom_model_path=LORA_PATH,
                USER_DIR=USER_DIR,
                negative_prompt=negative_prompt,
                num_inference_steps=num_inference_steps,
                num_images_per_prompt=num_images_per_prompt,
                save_images=False,
            )
        }
    )
    return Response(response=image_response, content_type="application/json")


# Run the app if the script is run directly
if __name__ == "__main__":
    ### Change host IP and port according to server configuration ###################################
    serve(app, host="127.0.0.1", port=8081)
### For production MODIFY the line above ########################################################
