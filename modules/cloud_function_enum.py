import json
import requests
import os
from tabulate import tabulate
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

def load_gcp_perms():
    """Loads valid GCP permissions from a JSON file."""
    with open('valid-gcp-perms.json') as f:
        return json.load(f)

def check_service_public_access(service_name, access_token, project_id, region):
    """Checks if a Cloud Run service is publicly accessible."""
    url = f"https://run.googleapis.com/v2/projects/{project_id}/locations/{region}/services/{service_name}:getIamPolicy"
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    
    response = requests.post(url, headers=headers)
    if response.status_code == 200:
        bindings = response.json().get("bindings", [])
        for binding in bindings:
            if "allUsers" in binding.get("members", []):
                return Fore.RED + "Public" + Style.RESET_ALL
        return Fore.GREEN + "Private" + Style.RESET_ALL
    return Fore.YELLOW + "Unknown" + Style.RESET_ALL

def fetch_cloud_run_services(access_token, project_id, region):
    """Fetches all Cloud Run services in a GCP project and region."""
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    cloud_run_perm = "run.services.list"
    valid_perms = load_gcp_perms()

    if cloud_run_perm in valid_perms:
        url = f"https://run.googleapis.com/v2/projects/{project_id}/locations/{region}/services"
        response = requests.get(url, headers=headers)
        print(response.json())
        if response.status_code == 200:
            services = response.json().get("services", [])
            table_data = []

            for service in services:
                name = service.get("name", "Unknown").split("/")[-1]
                url = service.get("uri", "No URL")
                service_account = service.get("template", {}).get("serviceAccount", "No service account")
                public_status = check_service_public_access(name, access_token, project_id, region)
                env_vars = service.get("template", {}).get("containers", [{}])[0].get("env", [])
                env_vars_str = json.dumps(env_vars, indent=2) if env_vars else Fore.RED + "No env vars" + Style.RESET_ALL

                table_data.append([
                    Fore.CYAN + name + Style.RESET_ALL,
                    Fore.YELLOW + url + Style.RESET_ALL,
                    Fore.GREEN + service_account + Style.RESET_ALL,
                    public_status,
                    env_vars_str
                ])

            headers = [Fore.WHITE + "Service Name" + Style.RESET_ALL,
                       Fore.WHITE + "URL" + Style.RESET_ALL,
                       Fore.WHITE + "Service Account" + Style.RESET_ALL,
                       Fore.WHITE + "Public Access" + Style.RESET_ALL,
                       Fore.WHITE + "Environment Variables" + Style.RESET_ALL]

            print("\n" + tabulate(table_data, headers=headers, tablefmt="fancy_grid"))
        else:
            print(Fore.RED + f"Cloud Run API Error: {response.status_code} - {response.text}" + Style.RESET_ALL)
    else:
        print(Fore.RED + "Missing permission: run.services.list" + Style.RESET_ALL)

def download_source_code(access_token, service_name, region, project_id):
    """Downloads source code of a Cloud Run service (if available)."""
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    url = f"https://run.googleapis.com/v2/projects/{project_id}/locations/{region}/services/{service_name}"

    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        service_data = response.json()
        source_url = service_data.get("sourceArchiveUrl", None)
        
        if source_url:
            os.system(f"wget --header='Authorization: Bearer {access_token}' {source_url} -O {service_name}.zip")
            print(Fore.GREEN + f"Source code downloaded as {service_name}.zip" + Style.RESET_ALL)
        else:
            print(Fore.RED + "No source code archive found for this service." + Style.RESET_ALL)
    else:
        print(Fore.RED + f"Failed to fetch service details: {response.status_code} - {response.text}" + Style.RESET_ALL)
