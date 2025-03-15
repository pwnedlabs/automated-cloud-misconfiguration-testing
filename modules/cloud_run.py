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

def get_all_regions(access_token, project_id):
    """Fetches all available Cloud Run regions for a GCP project."""
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    url = f"https://run.googleapis.com/v2/projects/{project_id}/locations"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return [loc["locationId"] for loc in response.json().get("locations", [])]
    else:
        print(Fore.RED + f"Failed to fetch regions: {response.status_code} - {response.text}" + Style.RESET_ALL)
        return []

def determine_service_type(service):
    """Determines if a service is Cloud Run or Cloud Function based on its metadata."""
    labels = service.get("labels", {})
    if labels.get("goog-managed-by") == "cloudfunctions" or "goog-drz-cloudfunctions-id" in labels:
        return "Cloud Function"
    
    build_config = service.get("buildConfig", {})
    if build_config.get("functionTarget"):
        return "Cloud Function"
        
    return "Cloud Run"

def fetch_cloud_run_services(access_token, project_id):
    """Fetches all Cloud Run services across all regions in a GCP project."""
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    cloud_run_perm = "run.services.list"
    valid_perms = load_gcp_perms()
    
    if cloud_run_perm in valid_perms:
        regions = get_all_regions(access_token, project_id)
        table_data = []
        
        for region in regions:
            url = f"https://run.googleapis.com/v2/projects/{project_id}/locations/{region}/services"
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                services = response.json().get("services", [])
                for service in services:
                    name = service.get("name", "Unknown").split("/")[-1]
                    service_url = service.get("uri", "No URL")
                    service_account = service.get("template", {}).get("serviceAccount", "No service account")
                    managed_by = service.get("labels", {}).get("goog-managed-by", "Unknown")  # Extract managed by
                    service_type = determine_service_type(service)

                    table_data.append([
                        Fore.CYAN + name + Style.RESET_ALL,
                        Fore.YELLOW + region + Style.RESET_ALL,
                        Fore.YELLOW + service_url + Style.RESET_ALL,
                        Fore.GREEN + service_account + Style.RESET_ALL,
                        Fore.MAGENTA + managed_by + Style.RESET_ALL,  # Display managed by
                        Fore.BLUE + service_type + Style.RESET_ALL
                    ])
            else:
                print(Fore.RED + f"Cloud Run API Error in {region}: {response.status_code} - {response.text}" + Style.RESET_ALL)
        
        headers = [
            Fore.WHITE + "Service Name" + Style.RESET_ALL,
            Fore.WHITE + "Region" + Style.RESET_ALL,
            Fore.WHITE + "URL" + Style.RESET_ALL,
            Fore.WHITE + "Service Account" + Style.RESET_ALL,
            Fore.WHITE + "Managed By" + Style.RESET_ALL,  # New column
            Fore.WHITE + "Service Type" + Style.RESET_ALL
        ]
        
        print("\n" + tabulate(table_data, headers=headers, tablefmt="fancy_grid"))
    else:
        print(Fore.RED + "Missing permission: run.services.list" + Style.RESET_ALL)
