import requests
import json
import argparse
from tabulate import tabulate
from colorama import Fore, Style, init

init(autoreset=True)

def fetch_project_iam_policy(project_id, access_token):
    """Fetches IAM policy for a GCP project using the provided access token."""
    try:
        url = f"https://cloudresourcemanager.googleapis.com/v1/projects/{project_id}:getIamPolicy"
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.post(url, headers=headers)
        response.raise_for_status()
        policy = response.json()
        print(Fore.GREEN + f"[+] Retrieved IAM policy for Project IAM" + Style.RESET_ALL)
        return policy
    except requests.exceptions.RequestException as e:
        print(Fore.RED + f"[-] Failed to get IAM policy for Project IAM: {str(e)}" + Style.RESET_ALL)
        return None

def fetch_compute_iam_policy(project_id, access_token):
    """Fetches IAM policy for Compute Engine using the provided access token."""
    try:
        url = f"https://compute.googleapis.com/compute/v1/projects/{project_id}/getIamPolicy"
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.post(url, headers=headers)
        response.raise_for_status()
        policy = response.json()
        print(Fore.GREEN + f"[+] Retrieved IAM policy for Compute Engine" + Style.RESET_ALL)
        return policy
    except requests.exceptions.RequestException as e:
        print(Fore.RED + f"[-] Failed to get IAM policy for Compute Engine: {str(e)}" + Style.RESET_ALL)
        return None

def fetch_storage_buckets_iam_policies(project_id, access_token):
    """Fetches IAM policies for all Cloud Storage buckets in a project using the provided access token."""
    try:
        list_buckets_url = f"https://storage.googleapis.com/storage/v1/b?project={project_id}"
        headers = {"Authorization": f"Bearer {access_token}"}
        list_buckets_response = requests.get(list_buckets_url, headers=headers)
        list_buckets_response.raise_for_status()
        buckets_data = list_buckets_response.json()
        buckets = buckets_data.get('items', [])

        bucket_policies = {}
        for bucket in buckets:
            bucket_name = bucket['name']
            try:
                get_iam_url = f"https://storage.googleapis.com/storage/v1/b/{bucket_name}/iam"
                get_iam_response = requests.get(get_iam_url, headers=headers)
                get_iam_response.raise_for_status()
                policy = get_iam_response.json()
                print(Fore.GREEN + f"[+] Retrieved IAM policy for bucket: {bucket_name}" + Style.RESET_ALL)
                bucket_policies[bucket_name] = policy
            except requests.exceptions.RequestException as e:
                print(Fore.RED + f"[-] Failed to get IAM policy for bucket {bucket_name}: {str(e)}" + Style.RESET_ALL)
        return bucket_policies
    except requests.exceptions.RequestException as e:
        print(Fore.RED + f"[-] Failed to access Cloud Storage buckets: {str(e)}" + Style.RESET_ALL)
        return None

def get_all_iam_policies(project_id, access_token):
    """Fetches IAM policies for GCP services and displays them in a table."""
    table_data = []

    project_policy = fetch_project_iam_policy(project_id, access_token)
    if project_policy:
        bindings = project_policy.get("bindings", [])
        roles = ", ".join([binding["role"] for binding in bindings]) if bindings else "No roles assigned"
        table_data.append([
            Fore.CYAN + "Project IAM" + Style.RESET_ALL,
            Fore.YELLOW + roles + Style.RESET_ALL
        ])

    compute_policy = fetch_compute_iam_policy(project_id, access_token)
    if compute_policy:
        bindings = compute_policy.get("bindings", [])
        roles = ", ".join([binding["role"] for binding in bindings]) if bindings else "No roles assigned"
        table_data.append([
            Fore.CYAN + "Compute Engine" + Style.RESET_ALL,
            Fore.YELLOW + roles + Style.RESET_ALL
        ])

    bucket_policies = fetch_storage_buckets_iam_policies(project_id, access_token)
    if bucket_policies:
        for bucket_name, policy in bucket_policies.items():
            bindings = policy.get("bindings", [])
            roles = ", ".join([binding["role"] for binding in bindings]) if bindings else "No roles assigned"
            table_data.append([
                Fore.CYAN + f"Storage Bucket: {bucket_name}" + Style.RESET_ALL,
                Fore.YELLOW + roles + Style.RESET_ALL
            ])

    headers = [
        Fore.WHITE + "Service Name" + Style.RESET_ALL,
        Fore.WHITE + "Roles Assigned" + Style.RESET_ALL
    ]

    print("\n" + tabulate(table_data, headers=headers, tablefmt="fancy_grid"))

def main():
    parser = argparse.ArgumentParser(description='GCP IAM Policy Checker (Access Token)')
    parser.add_argument('--project-id', required=True, help='GCP Project ID')
    parser.add_argument('--access-token', required=True, help='User access token')

    args = parser.parse_args()

    print("Using provided access token.....")
    get_all_iam_policies(args.project_id, args.access_token)

if __name__ == "__main__":
    print(Fore.RED + "WARNING: Passing access tokens as command-line arguments is highly insecure!" + Style.RESET_ALL)
    main()