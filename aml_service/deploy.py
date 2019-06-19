import argparse
import azureml.core
from azureml.core import Workspace, Experiment, Run
from azureml.core.webservice import AciWebservice, Webservice
from azureml.core import Image
from azureml.core.authentication import AzureCliAuthentication
import json
import os

print("In deploy.py")
print("Azure Python SDK version: ", azureml.core.VERSION)

print('Opening eval_info.json...')
eval_filepath = os.path.join('./outputs', 'eval_info.json')

try:
    with open(eval_filepath) as f:
        eval_info = json.load(f)
        print('eval_info.json loaded')
        print(eval_info)
except:
    print("Cannot open: ", eval_filepath)
    print("Exiting...")
    sys.exit(0)

model_name = eval_info["model_name"]
model_version = eval_info["model_version"]
model_path = eval_info["model_path"]
model_acc = eval_info["model_acc"]
deployed_model_acc = eval_info["deployed_model_acc"]
deploy_model = eval_info["deploy_model"]
image_name = eval_info["image_name"]
image_id = eval_info["image_id"]

if deploy_model == False:
    print('Model metric did not meet the metric threshold criteria and will not be deployed!')
    print('Existing')
    sys.exit(0)

print('Moving forward with deployment...')

parser = argparse.ArgumentParser("deploy")
parser.add_argument("--service_name", type=str, help="service name", dest="service_name", required=True)
parser.add_argument("--aci_name", type=str, help="aci name", dest="aci_name", required=True)
parser.add_argument("--description", type=str, help="description", dest="description", required=True)
args = parser.parse_args()

print("Argument 1: %s" % args.service_name)
print("Argument 2: %s" % args.aci_name)
print("Argument 3: %s" % args.description)

print('creating AzureCliAuthentication...')
cli_auth = AzureCliAuthentication()
print('done creating AzureCliAuthentication!')

print('get workspace...')
ws = Workspace.from_config(auth=cli_auth)
print('done getting workspace!')

image = Image(ws, id = image_id)
print(image)

try:
    existing_websrv = Webservice(ws, args.service_name)
    existing_websrv.delete()
    print("Existing webservice deleted: ", args.service_name)
except:
    print("No existing webservice found: ", args.service_name)

aci_config = AciWebservice.deploy_configuration(
    cpu_cores = 1, 
    memory_gb = 1, 
    tags = {'name': args.aci_name, 'image_id': image_id}, 
    description = args.description)

aci_service = Webservice.deploy_from_image(deployment_config=aci_config, 
                                           image=image, 
                                           name=args.service_name, 
                                           workspace=ws)

aci_service.wait_for_deployment(show_output=True)

aci_webservice = {}
aci_webservice["aci_name"] = aci_service.name
aci_webservice["aci_url"] = aci_service.scoring_uri
print("ACI Webservice Scoring URI")
print(aci_webservice)

print("Saving aci_webservice.json...")
aci_webservice_filepath = os.path.join('./outputs', 'aci_webservice.json')
with open(aci_webservice_filepath, "w") as f:
    json.dump(aci_webservice, f)
print("Done saving aci_webservice.json!")

# Single test data
test_data = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 2, 5, 6, 4, 3, 1, 34]]
# Call the webservice to make predictions on the test data
prediction = aci_service.run(json.dumps(test_data))
print('Test data prediction: ', prediction)

