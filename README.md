# Production-ready Text-to-Image Stable Diffusion
# This repository contains all the files necessary for PRODUCTION deployment (to be run on GPU-capable instance):
###
###
### (C) Copyright 2023 by *Konstantin Kuteykin-Teplyakov*.
### All rights reserved.
### ANY COMMERCIAL USE IS PROHIBITED.

### DISCLAIMER: This code has been disclosed to general public for  *informational purposes only*, and any commercial use as part of any software or paid service is *not allowed* without written permission from the copyright owner.
###
###
###
## Root folder , files to copy to GPU-enabled backend server *(please keep this folder structure!)*.

`initial_setup.sh` Run this bash script to install the *sdiff_env* Python environment and create all necessary subdirectories. 

`requirements.txt` Environment description - list of Python libraries required for this module.

`download_sdiff_model.py` Run this file to download text-to-image *diffusers* models from Hugging Face (at least 3 models, *regular*, *high_res* and *photoreastic* are essential for the current Python scripts). Models are saved in *./HF_models/*.

`images_parameters.json` All parameters for text-to-image generation: available models and prompts for ChatGPT.

## In order to run Text-to-Image generation:
1. Copy all the content of this repository to the GPU instance, keeping the subfolder structure.
2. Run a shell script "initial_setup.sh" (permissions must be set as executable file) in order to create the environment called *sdiff_env* with python3.9.16 ( the easiest way to do this by installing the "Miniconda3-py39_23.1.0"). 
3. Activate created *sdiff_env* environment (`conda activate sdiff_env`) and install all necessary libraries (`pip3 install -r requirements.txt`). 
4. Download all necessary base text-to-image models from Hugging Face (at least 3 models, regular, high_res and photoreastic are essential for the current Python scripts) by running `download_sdiff_model.py` script several times.
5. Run one of Python scripts (either `SDiff_inference_basic.py`,  `SDiff_inference_automatic_model_selection_adaptive_prompting_with_ChatGPT.py`, `SDiff_inference_multiuser_custom_models.py` or 
`SDiff_finetuning.py`) depending of required task. 
6. If frontend and GPU instance are running on the same virtual machine, open http://127.0.0.1:8081 on your web-browser. If GPU instance is a remote server, replace the localhost IP address 127.0.0.1 to actual IP address of GPU instance and open http://actual-IP-address-of-GPU-instance:8081 instead of localhost.


### Basic version:
Run `SDiff_inference_basic.py` to activate this submodule.

*Features* :
1. Medium image size (currently 512x512 px)
2. Generates ONE image in "watercolour" style



### Advanced version:
Run `SDiff_inference_automatic_model_selection_adaptive_prompting_with_ChatGPT.py` to activate this submodule

*Features* :
1. Larger image size (currently 768x768 px)
2. Generates FOUR images in either or "Photorealistic" or "Artistic" (randomly selected from *"Oil Paint", "Line Art", "Anime Cartoons", "Watercolours"*) style.
3. Adaptive prompt generation and model selection: SD model and final prompt structure automatically detected based on pre-processed user input received from front-end.

### Total flexibility version: user-specific, support custom fine-tuned models
Consists of two parts

`SDiff_inference_multiuser_custom_models.py` for image generation (using either the base SD model or a user-specific custom LoRA model)

`SDiff_finetuning.py`, to be run separately by callback from another frontend web page to enable model fine-tuning module: creates user-specific custom LoRA model (one model for each object in specific style, from 7-15 images of that object)


*Features 
1. **User specific** module - must receive $USER_ID from frontend. All user data is stored in *./Users/$USER_ID/* subfolder.
2. Displays the list of all custom LoRA models available to the current user (located in *./Users/$USER_ID/custom_models*). If this user has not yet created a custom model, the list will be empty.
3. Generates FOUR images.
4. The quality of the final image (number of inference steps) is chosen by the user.
5. Basic text-to-image model is user-selected, there is a choice of final image size.
6. Image style is user-selected (however, if a custom fine-tuned model is selected, this choice is irrelevant and the image will be generated in the style of that custom model object).
7. There is an option to automatically save all generated images to the backend server folder *./Users/$USER_ID/output* by sending the parameter *save_images=True* to the `generate_images` function *(this option must be implemented on the frontend to give the user access to download his files at any later time)*.

### Other system files (do not execute them directly, as they will be called by other scripts)
`images_functions.py` custom python functions essential for the images module

`slugify.py` Convert any text to OS-friendly format - lower case, no punctuation, "-" instead of whitespace, etc.

`train_dreambooth_lora.py` Script by HuggingFace to train the models using the *DreamBooth + LoRA* technology. 

`default_config.yaml` Configuration file for fine-tuning the models 
###
### Subfolder `/static` JavaScript functions for the frontend
###
### Subfolder `/templates` HTML templates for frontend
###
### Subfolder `/Users` User-specific files (custom finetuned models, image datasets used for model customisation, saved output images)
###
### Subfolder `/HF_models` Text-to-Image models downloaded from HuggingFace

