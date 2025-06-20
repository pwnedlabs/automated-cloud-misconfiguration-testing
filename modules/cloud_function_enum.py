import json
import requests
import os
from tabulate import tabulate
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

def load_gcp_perms():
    """Loads valid GCP permissions from a JSON file."""
    try:
        with open('valid-gcp-perms.json') as f:
            return json.load(f)
    except Exception as e:
        print(Fore.RED + f"Error loading permissions: {str(e)}" + Style.RESET_ALL)
        return {}

def check_service_public_access(service_name, access_token, project_id, region):
    """Checks if a Cloud Run service is publicly accessible."""
    url = f"https://run.googleapis.com/v2/projects/{project_id}/locations/{region}/services/{service_name}:getIamPolicy"
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    
    try:
        response = requests.post(url, headers=headers, timeout=10)
        if response.status_code == 200:
            bindings = response.json().get("bindings", [])
            for binding in bindings:
                if "allUsers" in binding.get("members", []):
                    return Fore.RED + "Public" + Style.RESET_ALL
            return Fore.GREEN + "Private" + Style.RESET_ALL
        return Fore.YELLOW + "Unknown" + Style.RESET_ALL
    except Exception as e:
        print(Fore.RED + f"Error checking access: {str(e)}" + Style.RESET_ALL)
        return Fore.YELLOW + "Error" + Style.RESET_ALL

def save_response_to_json(response_data, filename):
    """Saves API response to JSON file with proper error handling."""
    try:
        abs_path = os.path.abspath(filename)
        with open(abs_path, 'w', encoding='utf-8') as f:
            json.dump(response_data, f, indent=4, ensure_ascii=False)
        print(Fore.GREEN + f"✅ Response saved to {abs_path}" + Style.RESET_ALL)
        return True
    except Exception as e:
        print(Fore.RED + f"❌ Failed to save JSON: {str(e)}" + Style.RESET_ALL)
        return False

def fetch_cloud_run_services(access_token, project_id, region):
    """Fetches all Cloud Run services in a GCP project and region."""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    cloud_run_perm = "run.services.list"
    valid_perms = load_gcp_perms()

    if cloud_run_perm not in valid_perms:
        print(Fore.RED + "Missing permission: run.services.list" + Style.RESET_ALL)
        return None

    url = f"https://run.googleapis.com/v2/projects/{project_id}/locations/{region}/services"
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # Save the raw API response
        raw_response = response.json()
        save_response_to_json(raw_response, f"cloudrun_raw_{region}.json")
        
        services = raw_response.get("services", [])
        if not services:
            print(Fore.YELLOW + "No Cloud Run services found in this region" + Style.RESET_ALL)
            return None

        table_data = []
        processed_services = []

        for service in services:
            name = service.get("name", "Unknown").split("/")[-1]
            uri = service.get("uri", "")
            urls = service.get("urls", [])
            display_url = uri if uri else (urls[0] if urls else "No URL")
            
            service_account = service.get("template", {}).get("serviceAccount", "No service account")
            is_default_sa = "@developer.gserviceaccount.com" in service_account
            
            public_status = check_service_public_access(name, access_token, project_id, region)
            
            containers = service.get("template", {}).get("containers", [])
            env_vars = []
            if containers:
                env_vars = containers[0].get("env", [])
            
            # Prepare processed data for JSON output
            service_info = {
                "name": name,
                "region": region,
                "url": display_url,
                "service_account": service_account,
                "is_default_sa": is_default_sa,
                "public_access": "Public" if "Public" in public_status else "Private",
                "environment_variables": env_vars,
                "creation_time": service.get("createTime", ""),
                "last_modified": service.get("updateTime", ""),
                "ingress_settings": service.get("ingress", "")
            }
            processed_services.append(service_info)
            
            # Prepare table data
            sa_color = Fore.RED if is_default_sa else Fore.YELLOW
            env_display = json.dumps(env_vars, indent=2) if env_vars else Fore.RED + "No env vars" + Style.RESET_ALL
            
            table_data.append([
                Fore.CYAN + name + Style.RESET_ALL,
                Fore.YELLOW + display_url + Style.RESET_ALL,
                sa_color + service_account + Style.RESET_ALL,
                public_status,
                env_display
            ])

        # Save processed data to another JSON file
        save_response_to_json(processed_services, f"cloudrun_processed_{region}.json")

        # Display table
        headers = [
            Fore.WHITE + "Service Name" + Style.RESET_ALL,
            Fore.WHITE + "URL" + Style.RESET_ALL,
            Fore.WHITE + "Service Account" + Style.RESET_ALL,
            Fore.WHITE + "Public Access" + Style.RESET_ALL,
            Fore.WHITE + "Environment Variables" + Style.RESET_ALL
        ]
        print("\n" + tabulate(table_data, headers=headers, tablefmt="fancy_grid"))
        
        return processed_services

    except Exception as e:
        print(Fore.RED + f"API Error: {str(e)}" + Style.RESET_ALL)
        return None

def download_source_code(access_token, service_name, region, project_id):
    """Downloads source code of a Cloud Run service (if available)."""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }
    url = f"https://run.googleapis.com/v2/projects/{project_id}/locations/{region}/services/{service_name}"

    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        service_data = response.json()
        save_response_to_json(service_data, f"cloudrun_source_{service_name}.json")
        
        source_url = service_data.get("sourceArchiveUrl", None)
        if source_url:
            print(Fore.CYAN + f"Attempting to download source from {source_url}" + Style.RESET_ALL)
            os.system(f"wget --header='Authorization: Bearer {access_token}' {source_url} -O {service_name}.zip")
            print(Fore.GREEN + f"Source code downloaded as {service_name}.zip" + Style.RESET_ALL)
        else:
            print(Fore.RED + "No source code archive found for this service." + Style.RESET_ALL)
            
    except Exception as e:
        print(Fore.RED + f"Download failed: {str(e)}" + Style.RESET_ALL)

# Example usage:
# fetch_cloud_run_services("your_access_token", "your-project-id", "us-central1")
# download_source_code("your_access_token", "your-service-name", "us-central1", "your-project-id")