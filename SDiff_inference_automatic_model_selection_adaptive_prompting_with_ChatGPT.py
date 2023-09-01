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
import logging
from pathlib import Path
from random import choice
from waitress import serve


app = Flask(__name__)
CORS(app)

# Set up logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)

# get the current working directory
START_DIR = Path(__file__).parent


### Define the constants for Stable Diffusion
parameters_file = START_DIR / "images_parameters.json"
num_images_per_prompt = 4
num_inference_steps = 50


# Define a route for the index page
@app.route("/", methods=["GET", "POST"])
def index():
    ### Replace FRONTEND with URL on host (IP:port/path/filename.html) #############################
    # return render_template('FRONTEND//path_on_frontend//SDiff_inference_automatic_model_selection_adaptive_prompting_with_ChatGPT.html')
    return render_template(
        "SDiff_inference_automatic_model_selection_adaptive_prompting_with_ChatGPT.html"
    )


# Define a route for the inference endpoint
@app.route("/inference", methods=["POST"])
def inference():
    # Retrieve the data from the POST request from frontend
    ### PROCESSED_INPUT is a product of user input pre-processing made on Frontend
    processed_input = request.form.get("processed_input")
    frontend_object_style = request.form.get("object_style")

    # Retrieve available image parameters from JSON file
    with open(parameters_file) as json_file:
        images_dict = json.load(json_file)

    # Automatic prompt generation
    task_1 = "Photo" if frontend_object_style == "Photo" else "Image"
    chatgpt_response_prompt = ask_chatgpt(
        processed_input, task_1, images_dict["chatgpt_prompts"]
    )

    # Selecting SDiff model and object_style

    if frontend_object_style == "Artistic":
        sdiff_model_type = "high_res"
        object_style = choice(["Oil", "Line", "Anime", "Watercolors"])
    else:
        detected_object = ask_chatgpt(
            chatgpt_response_prompt, "Detect", images_dict["chatgpt_prompts"]
        )
        logging.debug(f"Detected object: {detected_object}")
        if "People" in detected_object:
            sdiff_model_type = "photorealistic"
            object_style = "Photography"
        elif "Person" in detected_object:
            sdiff_model_type = "photorealistic"
            object_style = "Portrait"
        elif "Architecture" in detected_object:
            sdiff_model_type = "regular"
            object_style = "Architecture"
        else:
            sdiff_model_type = "high_res"
            object_style = "Photography"

    logging.debug(f"SDiff model type: {sdiff_model_type}, Object style: {object_style}")

    # Construct final prompt for image generation
    style_prefix = images_dict["object_style"][object_style]["prompt_prefix"]
    style_suffix = images_dict["object_style"][object_style]["prompt_suffix"]
    negative_prompt = images_dict["object_style"][object_style]["negative_prompt"]
    sdiff_model = images_dict["sdiff_models"][sdiff_model_type]["name"].split("/")[-1]

    image_prompt = f"{style_prefix} {chatgpt_response_prompt}, {style_suffix}."

    # Define the paths and parameters
    MODEL_PATH = START_DIR / "HF_models" / sdiff_model

    logging.debug("\n*** COMMERCIAL USE IS FORBIDDEN ***\n")

    # Print image generation data for debugging
    logging.debug(f"SDiff model: {MODEL_PATH}\n Prompt: {image_prompt}")

    # Send the image bytes to the frontend
    image_response = json.dumps(
        {
            "images": generate_images(
                image_prompt=image_prompt,
                MODEL_PATH=MODEL_PATH,
                custom_model_path="",
                USER_DIR="",
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
    ### Change host IP and port according to server configuration #############################
    serve(app, host="127.0.0.1", port=8081)
### For production MODIFY line above #######################################################
