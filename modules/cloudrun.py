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

def fetch_all_regions(access_token, project_id):
    """Fetches all available regions in the GCP project."""
    headers = {"Authorization": f"Bearer {access_token}"}
    url = f"https://compute.googleapis.com/compute/v1/projects/{project_id}/regions"
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return [region["name"] for region in response.json().get("items", [])]
        print(Fore.RED + f"Failed to fetch regions: {response.status_code}" + Style.RESET_ALL)
        return []
    except Exception as e:
        print(Fore.RED + f"Request failed: {str(e)}" + Style.RESET_ALL)
        return []

def fetch_cloud_run_services(access_token, project_id):
    """Fetches Cloud Run services from all regions and displays them in a table."""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }
    
    # Check permissions
    required_permission = "run.services.list"
    valid_perms = load_gcp_perms()
    if required_permission not in valid_perms:
        print(Fore.RED + f"Missing permission: {required_permission}" + Style.RESET_ALL)
        return None

    # Get regions
    regions = fetch_all_regions(access_token, project_id)
    if not regions:
        print(Fore.YELLOW + "No regions found" + Style.RESET_ALL)
        return None

    all_services = []
    table_data = []

    for region in regions:
        url = f"https://run.googleapis.com/v2/projects/{project_id}/locations/{region}/services"
        try:
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            services = response.json().get("services", [])
            
            for svc in services:
                # Extract service details
                name = svc.get("name", "").split("/")[-1]
                uri = svc.get("uri", "")
                urls = svc.get("urls", [])
                display_url = uri if uri else (urls[0] if urls else "No URL")
                
                # Service account info
                sa = svc.get("template", {}).get("serviceAccount", "No service account")
                is_default_sa = "@developer.gserviceaccount.com" in sa
                
                # Access info
                ingress = svc.get("ingress", "")
                public = ingress == "INGRESS_TRAFFIC_ALL"
               # print(f"Here are the data \n {name} \n {uri} \n {urls} \n {sa}")
                # Environment variables
                containers = svc.get("template", {}).get("containers", [])
                env_vars = []
                if containers:
                    for env in containers[0].get("env", []):
                        env_vars.append({
                            "name": env.get("name", ""),
                            "value": env.get("value", "")
                        })

                # Prepare service data for JSON
                service_info = {
                    "name": name,
                    "region": region,
                    "url": display_url,
                    "all_urls": urls,
                    "service_account": sa,
                    "is_default_sa": is_default_sa,
                    "public_access": public,
                    "ingress_setting": ingress,
                    "env_vars": env_vars,
                    "env_vars_count": len(env_vars),
                    "creation_time": svc.get("createTime", ""),
                    "creator": svc.get("creator", "")
                }
                all_services.append(service_info)
                
                # Prepare table row
                sa_color = Fore.RED if is_default_sa else Fore.YELLOW
                access_color = Fore.GREEN if public else Fore.BLUE
                warning = Fore.RED + "⚠ Default SA" if is_default_sa else ""
                
                table_data.append([
                    Fore.CYAN + name + Style.RESET_ALL,
                    Fore.GREEN + region + Style.RESET_ALL,
                    display_url,
                    access_color + ("Public" if public else "Private") + Style.RESET_ALL,
                    sa_color + sa + Style.RESET_ALL,
                    str(len(env_vars)),
                    warning
                ])

        except Exception as e:
            print(Fore.YELLOW + f"⚠ Skipping {region} (Error: {str(e)})" + Style.RESET_ALL)
            continue

    # Save to JSON file
    if all_services:
        output_file = "cloudrun_services.json"
        try:
            abs_path = os.path.abspath(output_file)
            with open(abs_path, 'w', encoding='utf-8') as f:
                json.dump(all_services, f, indent=4, ensure_ascii=False)
            print(Fore.GREEN + f"✅ Saved {len(all_services)} services to {abs_path}" + Style.RESET_ALL)
        except Exception as e:
            print(Fore.RED + f"❌ Failed to save: {str(e)}" + Style.RESET_ALL)
    else:
        print(Fore.YELLOW + "⚠ No services found" + Style.RESET_ALL)
    
    # Display table
    if table_data:
        headers = [
            Fore.WHITE + "Service" + Style.RESET_ALL,
            Fore.WHITE + "Region" + Style.RESET_ALL,
            Fore.WHITE + "URL" + Style.RESET_ALL,
            Fore.WHITE + "Access" + Style.RESET_ALL,
            Fore.WHITE + "Service Account" + Style.RESET_ALL,
            Fore.WHITE + "Env Vars" + Style.RESET_ALL,
            Fore.WHITE + "Warnings" + Style.RESET_ALL
        ]
        print("\n" + tabulate(table_data, headers=headers, tablefmt="fancy_grid"))
    else:
        print(Fore.RED + "No services found" + Style.RESET_ALL)
    
    return all_services
