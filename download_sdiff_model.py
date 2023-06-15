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


from diffusers import DiffusionPipeline
import json
from pathlib import Path


# Define paths
START_DIR = Path(__file__).parent  # directory of the current file
MODELS_DIR = START_DIR / "HF_models"
parameters_file = START_DIR / "images_parameters.json"


with open(parameters_file) as json_file:
    sdiff_dict = json.load(json_file)
models = sdiff_dict["sdiff_models"]

# Choose HuggingFace model
print("\n*** CHOOSE MODEL TO DOWNLOAD ***\n")
for model_id in models.keys():
    print(f"MODEL ID: {model_id}\n {models[model_id]}\n")

model_input = None
while model_input not in models.keys():
    model_input = input("Please input model_id: ")

hf_model = models[model_input]["name"]
model_name = hf_model.split("/")[-1]
MODEL_PATH = MODELS_DIR / model_name

# Downloading model from HuggingFace to cache
pipeline = DiffusionPipeline.from_pretrained(hf_model)

# Saving model from cache to local storage
pipeline.save_pretrained(MODEL_PATH)