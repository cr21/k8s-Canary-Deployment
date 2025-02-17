import os
import subprocess
import logging

logging.basicConfig(level=logging.INFO, 
format='%(asctime)s - %(levelname)s - %(message)s',
datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

CONFIG_TEMPLATE ="""
inference_address=http://0.0.0.0:8085
management_address=http://0.0.0.0:8085
metrics_address=http://0.0.0.0:8082
grpc_inference_port=7070
grpc_management_port=7071
enable_envvars_config=true
install_py_dep_per_model=true
load_models={0}
max_response_size=655350000
model_store=/mnt/models/model-store
default_response_timeout=600
enable_metrics_api=true
metrics_format=prometheus
number_of_netty_threads=4
job_queue_size=10
model_snapshot={{"name":"startup.cfg","modelCount":1,"models":{{"{0}":{{"1.0":{{"defaultVersion":true,"marName":"{0}.mar","minWorkers":1,"maxWorkers":1,"batchSize":1,"maxBatchDelay":10,"responseTimeout":600}}}}}}}}
"""


MODELS=['cat-classifier', 'food-classifier', 'imagenet-vit','indian-food-classifier','dog-classifier']

def create_folder_structure(root, model):
    model_dir = os.path.join(root, model)
    config_path = os.path.join(model_dir, 'config')
    model_store_dir_path = os.path.join(model_dir, 'model-store')

    os.makedirs(model_dir, exist_ok=True)
    os.makedirs(config_path, exist_ok=True)
    os.makedirs(model_store_dir_path, exist_ok=True)
    logger.info(f"Created folder structure for {model}")
    return model_dir

def create_config_file(modle_dir, model):
    config_file = os.path.join(model_dir,'config', 'config.properties')
    with open(config_file, 'w') as f:
        f.write(CONFIG_TEMPLATE.format(model))
    logger.info(f"Created config file for {model}")

def create_mar_file(model, model_store_dir):
    CMD = [
        "torch-model-archiver",
        "--model-name", model,
        "--handler", "ts_handlers/hf-image-classification/hf_image_classification_handler.py",
        "--version", "1.0",
        "--extra-files",f"models/{model}",
        "--export-path", model_store_dir,
    ]
    try:
        logger.info(f"Creating MAR file for {model}.mar in {model_store_dir}")
        subprocess.check_call(CMD)
        logger.info(f"MAR file for {model}.mar created successfully")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error creating MAR file for {model}.mar: {e}")
        
    

if __name__ == "__main__":
    root_dir = "./model-store"
    for model in MODELS:
        model_dir = create_folder_structure(root_dir, model)
        create_config_file(model_dir, model)
        create_mar_file(model, os.path.join(model_dir, 'model-store'))
        logger.info(f"Completed MAR file creation for {model}")
