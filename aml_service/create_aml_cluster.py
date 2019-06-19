import argparse
import azureml.core
from azureml.core import Workspace, Experiment, Run
from azureml.core.compute import AmlCompute, ComputeTarget
from azureml.core.compute_target import ComputeTargetException
from azureml.core.authentication import AzureCliAuthentication

print("In create_aml_cluster.py")

parser = argparse.ArgumentParser("create_aml_cluster")
parser.add_argument("--aml_compute_target", type=str, help="compute target name", dest="aml_compute_target", required=True)
args = parser.parse_args()

print("Argument 1: %s" % args.aml_compute_target)

print('creating AzureCliAuthentication...')
cli_auth = AzureCliAuthentication()
print('done creating AzureCliAuthentication!')

print('get workspace...')
ws = Workspace.from_config(auth=cli_auth)
print('done getting workspace!')

try:
    aml_compute = AmlCompute(ws, args.aml_compute_target)
    print("found existing compute target.")
except ComputeTargetException:
    print("creating new compute target")
    
    provisioning_config = AmlCompute.provisioning_configuration(vm_size = "STANDARD_D2_V2",
                                                                min_nodes = 1, 
                                                                max_nodes = 1)    
    aml_compute = ComputeTarget.create(ws, args.aml_compute_target, provisioning_config)
    aml_compute.wait_for_completion(show_output=True, min_node_count=None, timeout_in_minutes=20)
    
print("Aml Compute attached")
