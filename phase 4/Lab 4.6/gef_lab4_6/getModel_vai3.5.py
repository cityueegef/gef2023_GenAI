#!/usr/bin/env python3

import argparse
import subprocess as sp
import os

import yaml
from yaml.loader import SafeLoader

parser = argparse.ArgumentParser(description="""DPU-PYNQ helper script for downloading and compiling models from the Vitis AI modelzoo. 
        For list of models see: https://github.com/Xilinx/Vitis-AI/tree/v3.5/model_zoo/model-list""")
parser.add_argument('-n', '--name', type=str, help="Name of the model as seen in the model zoo list.")
parser.add_argument('-o', '--output_dir', type=str, default='.', help="Path to output folder")
args = parser.parse_args()

def download_model(model_name):
    """Downloads and extracts the contents of a quantized Vitis AI modelzoo model. The model.yaml file for the model
    must contain the "float & quantized" version.

    model_name -- the model name string as seen on in the modelzoo list (e.g. tf_inceptionv1_imagenet_224_224_3G_2.5)
    """

    # In order to retrieve the model download link, we parse the model.yaml file for that model
    yaml_url = f"https://github.com/Xilinx/Vitis-AI/raw/v3.5/model_zoo/model-list/{model_name}/model.yaml"
    download_url = None

    output = sp.run([f'wget', f'{yaml_url}', '-O', f'{model_name}.yaml'],
           stdout=sp.PIPE, universal_newlines=True)

    assert output.returncode == 0, "Failed to download the model.yaml file."
    assert os.path.isfile(f'{model_name}.yaml'), "Downloaded yaml has an unexpected name."

    # Open yaml and look for the 'float & quantized' type, the board that will
    # have this type will typically be GPU
    with open(f'{model_name}.yaml') as f:
        data = yaml.load(f, Loader=SafeLoader)

    for file in data['files']:
        if file['type'] == 'float & quantized':
            download_url = file['download link']
    
    assert download_url != None, "Can't find the 'float & quantized' field in model.yaml. Make sure this model has a quantized version available."

    # Download the model
    tarball_name = download_url.split('filename=')[-1]
   
    # If model already exists don't redownload
    if not os.path.isdir(model_name):
        output = sp.run([f'wget', f'{download_url}', '-O', tarball_name],
                stdout=sp.PIPE, universal_newlines=True)

        assert output.returncode == 0, "Failed to download the model."

        # Resolve if it's a zipfile or a tarball and extract appropriately
        if os.path.splitext(tarball_name)[1] == '.zip':
            output = sp.run(['unzip', tarball_name],
                    stdout=sp.PIPE, universal_newlines=True)
        elif os.path.splitext(tarball_name)[1] == '.gz':
            output = sp.run(['tar', 'xvf', tarball_name],
                    stdout=sp.PIPE, universal_newlines=True)
        else:
            raise Exception("Not a zip or tar")

    print(f'Extracted to: {model_name}')
    
download_model(args.name)
