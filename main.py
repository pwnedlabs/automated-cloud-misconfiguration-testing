import os
import json
import requests
import threading
import signal
import argparse
from modules.rule_based_detection import load_permissions, process_rules_directory
from modules.compute_engine_enum import *
from modules.cloudrun import *
from modules.app_engine_enum import *
from modules.gcp_bucket_enum import *
from modules.cloud_function_enum import *
from modules.pull_users_and_iam import *
from modules.pull_iam_policy_all_resource import *

from tqdm import tqdm
from jinja2 import Environment, FileSystemLoader
import datetime
# ------------------------- Argument Parser Setup -------------------------

parser = argparse.ArgumentParser(description="This script tests IAM permissions on GCP using brute force techniques.")
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
parser.add_argument("--test", action="store_true", help="test")
parser.add_argument("--region")
parser.add_argument("--security-reviewer", action='store_true', help="Tries to identify misconfiguration in different gcp services/accounts.")
parser.add_argument('--generate-report', type=str, help="Generate HTML Report for GCP.", default='yes')

args = parser.parse_args()

# ------------------------- Globals -------------------------

unique_permissions = set()
stop_threads = False
thread_lock = threading.Lock()

# ------------------------- Signal Handler -------------------------

def save_permissions_to_file():
    with open("valid-gcp-perms.json", "w") as outfile:
        json.dump(sorted(unique_permissions), outfile, indent=4)

def signal_handler(sig, frame):
    global stop_threads
    print("\n[!] KeyboardInterrupt detected. Saving permissions and stopping...")
    stop_threads = True
    save_permissions_to_file()
    exit(0)

signal.signal(signal.SIGINT, signal_handler)

# ------------------------- Core Functionality -------------------------

def process_role_file(access_token, project_id, file_path):
    global stop_threads
    if stop_threads or not os.path.getsize(file_path):
        return

    try:
        with open(file_path, "r") as file:
            permissions_data = json.load(file)
    except json.JSONDecodeError as e:
        print(f"[!] Error decoding JSON in {file_path}: {e}")
        return

    permissions = permissions_data.get("includedPermissions", [])
    if not permissions:
        print(f"[-] Ignoring {file_path}: Empty permissions")
        return

    payload = { "permissions": permissions }
    url = f"https://cloudresourcemanager.googleapis.com/v1/projects/{project_id}:testIamPermissions"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code != 200:
            #print(f"[!] API call failed for {file_path}: {response.status_code} - {response.text}")
            return

        valid = response.json().get("permissions", [])
        if valid:
            #print(f"[+] Valid Permissions from {os.path.basename(file_path)}: {valid}")
            with thread_lock:
                unique_permissions.update(valid)
                save_permissions_to_file()
    except Exception as e:
        print(f"[!] Request error for {file_path}: {e}")

def gcpiambruteforce_testIAM_Endpoint(access_token, project_id, service_account_email, roles_directory):
    files = [
        os.path.join(roles_directory, f)
        for f in os.listdir(roles_directory)
        if os.path.isfile(os.path.join(roles_directory, f))
    ]

    threads = []
    max_threads = 15

    with tqdm(total=len(files), desc="Brute Forcing Permissions", unit="file") as pbar:
        for file_path in files:
            if stop_threads:
                break

            while len(threads) >= max_threads:
                threads = [t for t in threads if t.is_alive()]

            def run_and_update(*args):
                process_role_file(*args)
                pbar.update(1)

            t = threading.Thread(target=run_and_update, args=(access_token, project_id, file_path))
            t.start()
            threads.append(t)

        for t in threads:
            t.join()






# ------------------------- Utility Functions -------------------------

def gcp_perms_anal():
    print("[*] Analyzing GCP permissions using predefined rules.")
    permissions = load_permissions("valid-gcp-perms.json")
    process_rules_directory(permissions, "rules/")

def load_gcp_valid_perms():
    with open('valid-gcp-perms.json') as f:
        return json.load(f)

# ------------------------- Execution -------------------------

if args.bruteforce_gcp_iam == "yes":
    if not all([args.access_token, args.service_account_email, args.project_id]):
        print("[!] Missing required arguments for bruteforce.")
        exit(1)
    gcpiambruteforce_testIAM_Endpoint(args.access_token, args.project_id, args.service_account_email, args.roles_directory)

if args.gcp_permission_analyze:
    gcp_perms_anal()

if args.auto_enum:
    if not args.access_token or not args.project_id:
        print("[!] Missing access token or project ID for auto enum.")
        exit(1)
    gcpiambruteforce_testIAM_Endpoint(args.access_token, args.project_id, args.service_account_email, args.roles_directory)
    gcp_perms_anal()
    check_compute_instance(args.access_token, args.project_id)
    check_app_engine_services(args.access_token, args.project_id)
    list_gcs_buckets(args.access_token, args.project_id)
    fetch_cloud_run_services(args.access_token, args.project_id,args.region)
    #generate_cloud_run_report()

if args.generate_report:
    from report.cloudstorage import *
    from report.cloudrunreport import *
    from report.computeengine import *
    from report.iam import *
    generate_cloud_run_report()
    generate_compute_report(datetime)
    generate_cloud_storage_report()
    generate_iam_report()

if args.test:
    #list_gcs_buckets(args.access_token, args.project_id)
    #check_compute_instance(args.access_token, args.project_id)
    #get_all_iam_policies(args.access_token, args.project_id)
    #gcp_perms_anal()
    fetch_cloud_run_services(args.access_token, args.project_id,args.region)
if args.csp == "gcp":
    print("[*] GCP selected.")
elif args.csp == "aws":
    print("[*] AWS support coming soon.")
elif args.csp == "azure":
    print("[*] Azure support coming soon.")
else:
    print("[!] Cloud not supported.")

#report_data="report_data.json"
#generate_html_report(report_data)
#print(args)
