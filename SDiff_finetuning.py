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


import json
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import logging
from pathlib import Path
import slugify
import subprocess
import shutil
from waitress import serve


app = Flask(__name__)
CORS(app)

# get the current working directory
START_DIR = Path(__file__).parent  # directory of the current file
parameters_file = START_DIR / "images_parameters.json"

# Set up logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)


@app.route("/", methods=["GET", "POST"])
def index():
    ### Replace FRONTEND with URL on host (IP:port/path/filename.html) ##############################
    # return render_template('FRONTEND//path_on_frontend//images_finetuning.html')
    return render_template("SDiff_finetuning.html")
    ### For production MODIFY the line above ########################################################


@app.route("/upload", methods=["POST"])
def upload():
    # retrieve user_id and training_prompt from the form data
    training_prompt = request.form.get("training_prompt")
    ### For production $USER_ID is generated from Login page on Frontend ###
    ### Here the *user_id* variable is received from the frontend form for testing purposes only - REPLACE it for production  ###
    user_id = request.form.get("user_id")
    ### For production MODIFY the line above ###########################################################

    # convert training prompt to a valid directory name
    prompt_as_path = slugify(training_prompt)

    logging.debug(f"User: {user_id}\n Training Prompt: {training_prompt}")

    logging.debug("\n*** COMMERCIAL USE IS FORBIDDEN ***\n")

    # construct file paths
    USER_DIR = START_DIR / "Users" / user_id
    TRAINING_DATA_PATH = USER_DIR / "training_data" / prompt_as_path
    if TRAINING_DATA_PATH.is_dir():
        shutil.rmtree(TRAINING_DATA_PATH)
    TRAINING_DATA_PATH.mkdir(parents=True, exist_ok=True)

    if "files" not in request.files:
        return jsonify({"error": "No file found in request"}), 400

    files = request.files.getlist("files")

    # save uploaded files to TRAINING_DATA_PATH folder
    for file in files:
        filename = file.filename
        file.save(TRAINING_DATA_PATH / filename)
    logging.debug("\n*** Files uploaded successfully *** \n")
    return jsonify({"message": "Files uploaded successfully"}), 200


# Route for finetuning
@app.route("/finetuning", methods=["POST"])
def finetuning():
    # Retrieve user_id, training_prompt and resolution from the form data
    training_prompt = request.form.get("training_prompt")
    sdiff_model_type = request.form.get("sdiff_model_type")
    ### For production $USER_ID is generated from Login page on Frontend ###
    ### Here the *user_id* variable is received from the frontend form for testing purposes only - REPLACE it for production  ###
    user_id = request.form.get("user_id")
    ### For production MODIFY the line above ###############################################################

    # Retrieve available image parameters from JSON file
    with open(parameters_file) as json_file:
        sdiff_dict = json.load(json_file)
    sdiff_model = sdiff_dict["sdiff_models"][sdiff_model_type]["name"].split("/")[-1]
    resolution = sdiff_dict["sdiff_models"][sdiff_model_type]["resolution"]

    # convert training prompt to a valid directory name
    prompt_as_path = slugify(training_prompt)

    # construct file paths
    MODEL_PATH = START_DIR / "HF_models" / sdiff_model
    USER_DIR = START_DIR / "Users" / user_id
    LORA_DIR = USER_DIR / "custom_models"
    TRAINING_DATA_PATH = USER_DIR / "training_data" / prompt_as_path
    LR_SCHEDULER = "constant"

    # print some debug info
    print("*** FINETUNING ***")

    logging.debug("\n*** COMMERCIAL USE IS FORBIDDEN ***\n")

    logging.debug("User: ", user_id)
    logging.debug("Training Prompt: ", training_prompt)
    logging.debug("Stable Diffusion Model: ", sdiff_model)
    logging.debug("Loading training images from: ", TRAINING_DATA_PATH)

    ### set CUDA_VISIBLE_DEVICES environment variable to 1 (assuming you have one GPU) ##############
    # os.environ['CUDA_VISIBLE_DEVICES'] = '1'
    ### For production MODIFY the line above ########################################################

    # Launch train_dreambooth_lora.py with command line parameters
    print(
        "Training is running, ETA = 4 min. for *512 px*, ETA = 9 min. for *768 px* for NVIDIA V100 GPU"
    )
    subprocess.run(
        [
            "accelerate",
            "launch",
            "train_dreambooth_lora.py",
            f"--pretrained_model_name_or_path={MODEL_PATH}",
            f"--instance_data_dir={TRAINING_DATA_PATH}",
            f"--output_dir={LORA_DIR}",
            f"--instance_prompt={training_prompt}",
            f"--resolution={resolution}",
            f"--train_batch_size=1",
            f"--gradient_accumulation_steps=1",
            f"--checkpointing_steps=250",
            f"--learning_rate=1e-4",
            f"--lr_scheduler={LR_SCHEDULER}",
            f"--lr_warmup_steps=0",
            f"--max_train_steps=500",
            f"--validation_prompt={training_prompt}",
            f"--validation_epochs=50",
            f"--seed=0",
            f"--gradient_checkpointing",
            f"--use_8bit_adam",
            f"--enable_xformers_memory_efficient_attention",
        ],
        capture_output=True,
        text=True,
    )

    # Rename LoRA model
    created_model = LORA_DIR / "pytorch_lora_weights.bin"
    LORA_PATH = created_model.rename(LORA_DIR / f"{prompt_as_path}__{sdiff_model}.bin")
    logging.debug("Model saved as ", LORA_PATH)

    # Cleaning up - Remove intermediate checkpoints
    shutil.rmtree(LORA_DIR / "checkpoint-250")
    shutil.rmtree(LORA_DIR / "checkpoint-500")

    logging.debug("*** Finetuning finished successfully! ***\n")

    # return success message
    return jsonify({"message": "Fine-tuning completed!"}), 200


# Run the app if the script is run directly
if __name__ == "__main__":
    ### Change host IP and port according to server configuration ###############################
    serve(app, host="127.0.0.1", port=8082)
### For production MODIFY the line above ########################################################
