import json
import requests
from tabulate import tabulate
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

def load_gcp_perms():
    """Loads valid GCP permissions from a JSON file."""
    with open('valid-gcp-perms.json') as f:
        return json.load(f)

def fetch_bucket_iam_policies(bucket_name, headers):
    """Fetches IAM policies of a GCS bucket to check public access."""
    url = f"https://storage.googleapis.com/storage/v1/b/{bucket_name}/iam"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        policy = response.json()
        bindings = policy.get("bindings", [])

        public_access_roles = []
        for binding in bindings:
            if "allUsers" in binding.get("members", []) or "allAuthenticatedUsers" in binding.get("members", []):
                public_access_roles.append(binding["role"])

        if public_access_roles:
            return f"Public access detected: {', '.join(public_access_roles)}"
        else:
            return "No public access detected"
    else:
        return "Unable to retrieve IAM policy"

def list_gcs_buckets(access_token, project_id):
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}

    gcs_perm = "storage.buckets.list"
    valid_perms = load_gcp_perms()

    if gcs_perm in valid_perms:
        gcs_url = f"https://storage.googleapis.com/storage/v1/b?project={project_id}"
        response = requests.get(gcs_url, headers=headers)

        if response.status_code == 200:
            buckets = response.json().get("items", [])
            table_data = []
            bucket_list = []

            if buckets:
                print("Buckets found:", len(buckets))
            else:
                print("No buckets found in the response.")

            for bucket in buckets:
                bucket_name = bucket.get("name", "Unknown")
                location = bucket.get("location", "Unknown")
                storage_class = bucket.get("storageClass", "Unknown")
                created_time = bucket.get("timeCreated", "Unknown")
                iam_status = fetch_bucket_iam_policies(bucket_name, headers)

                bucket_info = {
                    "bucket_name": bucket_name,
                    "location": location,
                    "storage_class": storage_class,
                    "created_time": created_time,
                    "iam_status": iam_status
                }

                # Append bucket info to the list
                bucket_list.append(bucket_info)

                # Prepare table data for pretty printing
                table_data.append([
                    Fore.CYAN + bucket_name + Style.RESET_ALL,
                    Fore.BLUE + location + Style.RESET_ALL,
                    Fore.GREEN + storage_class + Style.RESET_ALL,
                    Fore.YELLOW + created_time + Style.RESET_ALL,
                    Fore.RED + iam_status + Style.RESET_ALL if "Public" in iam_status else Fore.GREEN + iam_status + Style.RESET_ALL
                ])

            # Write bucket list to JSON file if it's not empty
            if bucket_list:
                print(bucket_list)
                with open("bucket-output.json", "w") as outfile:
                    json.dump(bucket_list, outfile, indent=4)
                print("✅ Bucket data saved to bucket-output.json")
            else:
                print("⚠ No bucket data to save.")
            
            # Print tabular view of buckets
            headers = [
                Fore.WHITE + "Bucket Name" + Style.RESET_ALL,
                Fore.WHITE + "Location" + Style.RESET_ALL,
                Fore.WHITE + "Storage Class" + Style.RESET_ALL,
                Fore.WHITE + "Created Time" + Style.RESET_ALL,
                Fore.WHITE + "IAM Status" + Style.RESET_ALL
            ]
            print("\n" + tabulate(table_data, headers=headers, tablefmt="fancy_grid"))

        else:
            print(Fore.RED + f"GCS API Error: {response.status_code} - {response.text}" + Style.RESET_ALL)
    else:
        print(Fore.RED + "Missing permission: storage.buckets.list" + Style.RESET_ALL)

# Example usage (replace with your actual values):
# list_gcs_buckets("your-access-token", "your-project-id")
