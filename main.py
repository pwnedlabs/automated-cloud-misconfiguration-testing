import argparse
import os
import json
import requests
import threading
import signal
from modules.rule_based_detection import load_permissions, process_rules_directory
from modules.compute_engine_enum import *
from modules.cloud_run import *
from modules.app_engine_enum import *
from modules.gcp_bucket_enum import *
from modules.cloud_function_enum import *
from modules.pull_users_and_iam import *
from modules.pull_iam_policy_all_resource import *



# Initialize the parser
parser = argparse.ArgumentParser(description="This script tests IAM permissions on GCP using brute force techniques.")

# Add optional arguments
parser.add_argument('--csp', type=str, help='Are You Using GCP? AWS OR AZURE?', default='gcp')
parser.add_argument('--bruteforce_gcp_iam', type=str, help="BruteForce GCP IAM Permissions.", default='no')
parser.add_argument('--enumerate-gcp', type=str, help="Automatically enumerate all IAM permissions in GCP.", default='yes')
parser.add_argument('--access-token', type=str, help="Enter your access token for Google Cloud", required=False)
parser.add_argument('--service-account-email', type=str, help="Enter Service Account Email for Google Cloud.", required=False)
parser.add_argument('--project-id', type=str, help="Enter your Google Cloud project id", required=False)
parser.add_argument('--roles-directory', type=str, help="Directory containing role JSON files", default='roles/gcp/roles')
parser.add_argument('--gcp_permission_analyze', action='store_true', help="Analyze GCP permissions using Predefined rules.")
parser.add_argument('--check-gcp-services', action='store_true', help="Check different GCP services for accessible resources.")
parser.add_argument('--auto-enum', action='store_true', help="Performs iam bruteforcing and automatically identifies exploitables permissions and services.")
parser.add_argument("--test",action="store_true",help="test")
parser.add_argument("--region")
parser.add_argument("--security-reviewer",action='store_true',help="Tries to identify misconfifuration in different gcp services/accounts. ")
# Parse the arguments
args = parser.parse_args()

# Global set to hold unique permissions
unique_permissions = set()
stop_threads = False

# Function to save permissions in real-time
def save_permissions_to_file():
    with open("valid-gcp-perms.json", "w") as outfile:
        json.dump(list(unique_permissions), outfile, indent=4)

# Function to handle Ctrl+C and save before exiting
def signal_handler(sig, frame):
    global stop_threads
    print("\nKeyboardInterrupt detected. Saving permissions and stopping...")
    stop_threads = True
    save_permissions_to_file()  # Save gathered permissions before exiting
    exit(0)

# Register signal handler for Ctrl+C
signal.signal(signal.SIGINT, signal_handler)

# Function to process the GCP IAM brute force testing
def gcpiambruteforce_testIAM_Endpoint(access_token, project_id, service_account_email, roles_directory):
    def process_file(filename):
        global stop_threads
        if stop_threads:  # Check if we should stop
            return

        file_path = os.path.join(roles_directory, filename)

        # Check if the file is not empty
        if os.path.getsize(file_path) == 0:
            return

        # Load permissions from the JSON file
        try:
            with open(file_path, "r") as file:
                permissions_data = json.load(file)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON in {filename}: {e}")
            return

        # Extract included permissions from the JSON file
        PERMISSIONS = permissions_data.get("includedPermissions", [])

        # If permissions are empty, ignore the role
        if not PERMISSIONS:
            print(f"Ignoring: {filename} - Empty permissions")
            return

        # Prepare the request payload
        payload = {
            "permissions": PERMISSIONS,
        }

        # Set the API endpoint URL
        url = f"https://cloudresourcemanager.googleapis.com/v1/projects/{project_id}:testIamPermissions"

        # Set the headers
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        # Make the API request to test the permissions
        response = requests.post(url, headers=headers, json=payload)

        # Check for errors in the response
        if response.status_code != 200:
            print(f"Error in API call for {filename}: {response.status_code} - {response.text}")
            return

        # Get the valid permissions from the response
        valid_permissions = response.json().get("permissions", [])

        # Add valid permissions to the set (to ensure uniqueness)
        if valid_permissions:
            print(f"Valid Permissions for {filename}: {valid_permissions}")
            unique_permissions.update(valid_permissions)  # Add to the set
            save_permissions_to_file()  

    # List all role files in the roles directory
    role_files = [f for f in os.listdir(roles_directory) if os.path.isfile(os.path.join(roles_directory, f))]

    # Use threading to process each file concurrently
    threads = []
    for role_file in role_files:
        if stop_threads:
            break

        if len(threads) >= 10:  # Limit the maximum number of threads to 10
            for thread in threads:
                thread.join()  # Wait for threads to complete before starting new ones
            threads = []  # Reset the thread list

        thread = threading.Thread(target=process_file, args=(role_file,))
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

# Check if brute force is enabled and validate required arguments
if args.bruteforce_gcp_iam == "yes":
    if not args.access_token or not args.service_account_email or not args.project_id:
        print("Error: --access-token, --service-account-email, and --project-id are required when using brute force.")
        exit(1)

    gcpiambruteforce_testIAM_Endpoint(
        access_token=args.access_token,
        project_id=args.project_id,
        service_account_email=args.service_account_email,
        roles_directory=args.roles_directory
    )

# GCP Permission Analysis
if args.gcp_permission_analyze:
    print("Analyzing GCP permissions using predefined rules.")
    permissions = load_permissions("valid-gcp-perms.json")
    process_rules_directory(permissions, "rules/")


# Other CSP options
elif args.csp == "gcp":
    print("Using GCP.....")
elif args.csp == "aws":
    print("AWS support COMING SOON.")
elif args.csp == "azure":
    print("Azure support COMING SOON.")
else:
    print("Cloud not supported.")

def gcp_perms_anal():
    print("Analyzing GCP permissions using predefined rules.")
    permissions = load_permissions("valid-gcp-perms.json")
    process_rules_directory(permissions, "rules/")

def load_gcp_valid_perms():
    with open('valid-gcp-perms.json') as f:
        return json.load(f)

def parse_compute_engine_instances(response_json):
    """Extracts instance name, zone, and service account from API response."""
    instances = []

    for zone, details in response_json.get("items", {}).items():
        if "instances" in details:
            for instance in details["instances"]:
                instance_name = instance.get("name")
                instance_zone = instance.get("zone", "").split("/")[-1]  # Extract only zone name
                service_accounts = [sa["email"] for sa in instance.get("serviceAccounts", [])] if "serviceAccounts" in instance else ["No service account"]

                instances.append({
                    "name": instance_name,
                    "zone": instance_zone,
                    "service_accounts": service_accounts
                })
    
    return instances

def parse_storage_buckets(response_json):
    """Extracts bucket name and location from Cloud Storage API response."""
    buckets = []

    if "items" in response_json:
        for bucket in response_json["items"]:
            bucket_name = bucket.get("name")
            bucket_location = bucket.get("location", "Unknown location")

            buckets.append({
                "name": bucket_name,
                "location": bucket_location
            })
    
    return buckets

def check_gcp_services(access_token, project_id):
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    
    # Compute Engine - List VMs
    compute_engine_perm="compute.instances.list"
    valid_perms = load_gcp_valid_perms()  # Load permissions
    if compute_engine_perm in valid_perms:
        compute_url = f"https://compute.googleapis.com/compute/v1/projects/{project_id}/aggregated/instances"
        compute_response = requests.get(compute_url, headers=headers)
        
        if compute_response.status_code == 200:
            parsed_instances = parse_compute_engine_instances(compute_response.json())

            if parsed_instances:
                print("\nCompute Engine Instances:")
                for instance in parsed_instances:
                    print(f"Instance Name: {instance['name']}")
                    print(f"Zone: {instance['zone']}")
                    print(f"Service Account: {', '.join(instance['service_accounts'])}")
                    print("-" * 40)
            else:
                print("No Compute Engine instances found.")
        else:
            print(f"Compute Engine API Error: {compute_response.status_code} - {compute_response.text}")
    else:
        print("Missing permission: compute.instances.list")

    # ✅ Cloud Storage - List Buckets
    storage_perm = "storage.buckets.list"
    if storage_perm in valid_perms:
        storage_url = f"https://storage.googleapis.com/storage/v1/b?project={project_id}"
        storage_response = requests.get(storage_url, headers=headers)
        
        if storage_response.status_code == 200:
            parsed_buckets = parse_storage_buckets(storage_response.json())

            if parsed_buckets:
                print("\n🔹 Cloud Storage Buckets:")
                for bucket in parsed_buckets:
                    print(f"   - Name: {bucket['name']}")
                    print(f"   - Location: {bucket['location']}")
                    print("-" * 40)
            else:
                print("No Cloud Storage buckets found.")
        else:
            print(f"❌ Cloud Storage API Error: {storage_response.status_code} - {storage_response.text}")
    else:
        print("🚨 Missing permission: storage.buckets.list")



    # Cloud Functions - List Functions
    functions_url = f"https://cloudfunctions.googleapis.com/v1/projects/{project_id}/locations/-/functions"
    functions_response = requests.get(functions_url, headers=headers)
    if functions_response.status_code == 200:
        print("Cloud Functions:", functions_response.json())
    else:
        print(f"Cloud Functions API Error: {functions_response.status_code} - {functions_response.text}")

if args.check_gcp_services:
    if not args.access_token or not args.project_id:
        print("Error: --access-token and --project-id are required when checking GCP services.")
        exit(1)
    check_gcp_services(args.access_token, args.project_id)

if args.auto_enum:
    if not args.access_token or not args.project_id:
        print("Error: --access-token and --project-id are required when checking GCP services.")
        exit(1)
    #gcpiambruteforce_testIAM_Endpoint(args.access_token, args.project_id,args.service_account_email, args.roles_directory)
    gcp_perms_anal()
    check_compute_instance(args.access_token, args.project_id)
    #check_cloud_run_services(args.access_token, args.project_id)
    check_app_engine_services(args.access_token,args.project_id)
    list_gcs_buckets(args.access_token,args.project_id)



if args.test:
    list_gcs_buckets(args.access_token,args.project_id)
    check_compute_instance(args.access_token, args.project_id)
    get_all_iam_policies(args.access_token,args.project_id)
    gcp_perms_anal()

print(args)