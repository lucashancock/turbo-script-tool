import requests
import logging
import csv
from requests.exceptions import HTTPError, Timeout, RequestException

# Set up logging
# Logging turned off because level set to critical!
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
logging.captureWarnings(True)
logger = logging.getLogger()

# Disable SSL warnings for insecure requests
TARGETS_ENDPOINT = "/api/v3/targets"
LOGIN_ENDPOINT = "/api/v3/login?hateoas=true"
SEARCH_ENDPOINT = "/api/v3/search"
GROUPS_ENDPOINT = "/api/v3/groups"

# Configurations for requests
TIMEOUT = 10  # seconds
RETRIES = 1  

# Helper function to log in the user
def login(api_url, username, password):
    logger.info(f"Initiating login to {api_url} with provided username: {username}")
    try:
        response = requests.post(
            url=f"{api_url}{LOGIN_ENDPOINT}",
            data={"username": username, "password": password},
            timeout=TIMEOUT,
            verify=False
        )

        response.raise_for_status()  # Will raise an error for bad status codes (4xx, 5xx)

        # Extract the authentication token
        auth_token = response.headers.get('Set-Cookie').split(";")[0]
        if auth_token:
            logger.info("Login successful. Authentication token received.")
            return auth_token
        else:
            logger.error("Login failed: Authentication token not found in response headers.")
            return None

    except (HTTPError, Timeout, RequestException) as e:
        logger.error(f"Login failed: {e}")
        return None

# Helper function to handle requests with retries
def request_with_retries(method, url, params=None, data=None, headers=None, retries=RETRIES, timeout=TIMEOUT):
    attempt = 0
    while attempt < retries:
        try:
            logger.info(f"Attempting {method.upper()} request to {url} with params: {params} and data.")
            response = requests.request(
                method=method,
                url=url,
                params=params,
                json=data, 
                headers=headers,
                timeout=timeout,
                verify=False
            )
            response.raise_for_status()  # Raise an error for bad status codes
            return response
        except (HTTPError, Timeout, RequestException) as e:
            attempt += 1
            logger.error(f"Attempt {attempt}/{retries} failed: {e}")
            if attempt >= retries:
                logger.error(f"All {retries} attempts failed. Raising exception.")
                raise
            else:
                logger.info("Retrying...")

# Function to perform GET request on /targets
def get_targets(api_url, token="", params={}):
    if not token:
        logger.error("Token is required for fetching targets.")
        return None
    
    try:
        logger.info(f"Fetching targets from {api_url}{TARGETS_ENDPOINT} with token.")
        response = request_with_retries("GET", f"{api_url}{TARGETS_ENDPOINT}", params=params, headers={"cookie": token})
        return response.json()  # Assuming response is in JSON format
    except Exception as e:
        logger.error(f"Failed to get targets: {e}")
        return None

def delete_target(api_url, token, target_uuid):
    if not token:
        logger.error("Token is required for deleting targets.")
        return None
    if not target_uuid:
        logger.error("Target UUID is required.")
        return None
    try:
        logger.info(f"Attempting to delete target with UUID: {target_uuid}...")
        url = f"{api_url}{TARGETS_ENDPOINT}/{target_uuid}"
        
        # Sending the PUT request to update the target
        response = request_with_retries("DELETE", url, headers={"cookie": token})

        # Check if the response was successful
        if response.status_code == 200:
            logger.info(f"Target {target_uuid} successfully deleted.")
            return response.json()
        else:
            logger.error(f"Failed to update target {target_uuid}. Status code: {response.status_code}.")
            return None
    except Exception as e:
        logger.error(f"Error occurred while updating target {target_uuid}: {e}")
        return None

# def delete_scope(api_url, token, scope_uuid):
#     if not token:
#         logger.error("Token is required for deleting targets.")
#         return None
#     if not scope_uuid:
#         logger.error("Scope UUID is required.")
#         return None
#     try:
#         logger.info(f"Attempting to delete scope with UUID: {scope_uuid}...")
#         url = f"{api_url}{GROUPS_ENDPOINT}/{scope_uuid}"
        
#         response = request_with_retries("DELETE", url, headers={"cookie": token})

#         # Check if the response was successful
#         if response.status_code == 200:
#             logger.info(f"Scope {scope_uuid} successfully deleted.")
#             return response.json()
#         else:
#             logger.error(f"Failed to delete scope {scope_uuid}. Status code: {response.status_code}.")
#             return None
#     except Exception as e:
#         logger.error(f"Error occurred while deleting scope {scope_uuid}: {e}")
#         return None

def delete_oracle_targets(api_url, token="", params={}):
    if not token:
        logger.error("Token is required for deleting Oracle targets.")
        return

    try:
        logger.info(f"Deleting malfunctioning Oracle targets from {api_url}{TARGETS_ENDPOINT}")
        targets = request_with_retries("GET", f"{api_url}{TARGETS_ENDPOINT}", params={"target_type": "ORACLE", "health_state": "CRITICAL"}, headers={"cookie": token})
        results = targets.json()
        for result in results:
            uuid = result.get("uuid")
            # scope_uuid = next((field["value"] for field in result["inputFields"] if field["name"] == "targetEntities"), None)
            try:
                response = request_with_retries("DELETE", f"{api_url}{TARGETS_ENDPOINT}/{uuid}", headers={"cookie": token})
                # delete groups associated with the targets too.
                # response2 = request_with_retries("DELETE", f"{api_url}{GROUPS_ENDPOINT}/{scope_uuid}", headers={"cookie": token})
                if response.status_code == 500: 
                    logger.error(f"Server error (500) while deleting target {uuid}. Skipping this target.")
                    continue  
                if not response.ok:
                    logger.error(f"Failed to delete target {uuid}, status code: {response.status_code}")
                    continue
                logger.info(f"Successfully deleted target {uuid}")
            except Exception as e:
                logger.error(f"Error deleting target {uuid}: {e}")
                continue  # Continue to the next target if an exception occurs

    except Exception as e:
        logger.error(f"Failed to retrieve or delete Oracle targets: {e}")
    return None

# Function to perform POST request on /targets to create new Oracle targets
def create_oracle_targets(api_url, token="", params=[]):
    if not token:
        logger.error("Token is required for creating Oracle targets.")
        return None
    if not params:
        logger.error("No payload provided to create Oracle targets.")
        return None
    
    for cf in params:
        logger.info(f"Attempting to create an Oracle target...")
        try:
            # Sending the request - "fire and forget"
            request_with_retries(method="POST", url=f"{api_url}{TARGETS_ENDPOINT}", data=cf, headers={"cookie": token}, timeout=1)
            logger.info(f"Oracle target creation request sent")
        except Exception as e:
            logger.info(f"Broke out of wait for request completion. Expected output")

# Example function to test all request types
def run_targets_script(api_url, username, password, filepath):
    # Login
    token = login(api_url, username, password)
    if not token:
        logger.error("Failed to log in. Exiting the script.")
        return
    
    # Get the current configured Oracle targets
    logger.info("Fetching existing Oracle targets...")
    targets = get_targets(api_url, token, params={"target_type": "Oracle"})
    if targets:
        logger.info(f"Found {len(targets)} Oracle targets.")
    else:
        logger.info("No Oracle targets found.")
    
    # Delete the old oracle targets
    logger.info("Deleting old Oracle targets... (This functionality needs to be implemented)")

    # Parse the CSV to get JSON payload
    payload = oracle_csv_to_json(api_url, token, filepath, header=True) 
    logger.info(f"Parsed CSV and created payload: {len(payload)} entries.")

    # Create the new oracle targets
    if payload:
        logger.info(f"Creating {len(payload)} new Oracle targets...")
        create_oracle_targets(api_url, token, params=payload)

def oracle_csv_to_json(api_url, token, csv_file, header=True):
    payload = []

    # Read the CSV file
    logger.info(f"Reading CSV file: {csv_file}")
    with open(csv_file, mode='r', encoding='utf-8-sig') as file:
        csv_reader = csv.reader(file) 
        skipped_header = False 
        for row in csv_reader:
            if (header and not skipped_header):
                skipped_header = True
                continue  # Skip the header row
            
            scope_uuid = create_group(api_url, token, row[0]) 
            if not scope_uuid:
                logger.warning(f"Couldn't create group for: {row[0]}. Check VMname matches an actual VM. Skipping this row.")
                continue
            # Construct the data for creating the target
            logger.info(scope_uuid["uuid"]) 

            # Group:  On-Prem - Oracle – ServerName
            # Target:  On-Prem - Oracle - ServerName-InstanceName
            
            data = {
                "category": "Applications and Databases",
                "type": "Oracle",  
                "inputFields": [
                    {"name": "targetId", "value": f"On-Prem - Oracle - {row[0]}-{row[1]}"},
                    {"name": "username", "value": row[3]},
                    {"name": "password", "value": row[4]},
                    {"name": "targetEntities", "value": scope_uuid["uuid"]},  
                    {"name": "port", "value": row[2]},
                    {"name": "databaseID", "value": row[1]},
                    {"name": "fullValidation", "value": row[5].strip().lower()} 
                ]
            }

            payload.append(data)
    return payload

def create_group(api_url, token, server_name):
    # Check inputs
    if not token:
        logger.error("Token is required for creating group.")
        return None
    if not server_name:
        logger.error("Group_name and VM_name should be supplied in the CSV file.")
        return None

    # TO-DO: search if a group with this name exists
    logger.info(f"Attempting to find an existing group")
    response = request_with_retries(method="GET", url=f"{api_url}{SEARCH_ENDPOINT}", params={"q": f"On-Prem - Oracle - {server_name}", "types": ["Group"]}, headers={"cookie": token})
    existing_groups = response.json()
    if len(existing_groups) > 0:
        return existing_groups[0]

    try:
        logger.info(f"Attempting to create group with for and VM: {server_name}...")
        url = f"{api_url}{GROUPS_ENDPOINT}"

        # Get the UUID for the VM specified in the row of the CSV
        vm_uuid = get_vm_uuid(api_url, token, server_name)
        if not vm_uuid:
            logger.error(f"Could not create group because couldn't fetch VM uuid.")
            return None

        # Create the payload to send to the Turbo backend to create the group
        data = {"criteriaList":[],
                "displayName": f"On-Prem - Oracle - {server_name}",
                "groupType":"VirtualMachine",
                "isStatic":True,
                "memberUuidList":[vm_uuid]
                }

        # POST to create the group
        create = request_with_retries("POST", url, data=data, headers={"cookie": token})
        # Check if the response was successful
        if create.status_code == 200:
            logger.info(f"Group successfully created")
            return create.json()
        else:
            logger.error(f"Failed to create group in API req. {server_name}. Status code: {create.status_code}.")
            return None
    except Exception as e:
        logger.error(f"Error occurred while updating target {server_name}: {e}")
        return None

def get_vm_uuid(api_url, token, vm_name):
    try:
        logger.info(f"Looking up UUID for VM: {vm_name}")
        response = request_with_retries(method="GET", url=f"{api_url}{SEARCH_ENDPOINT}", params={"q": vm_name, "types": ["VirtualMachine"]}, headers={"cookie": token})
        res_data = response.json()
        
        if len(res_data) != 1:
            logger.warning(f"Expected 1 result for VM {vm_name}, found {len(res_data)}. Skipping.")
            return None
        return res_data[0]['uuid']
    except Exception as e:
        logger.error(f"Failed to retrieve scope UUID for {vm_name}: {e}")
        return None

# Function to perform PUT request on /targets/{target_UUID}
def update_target(api_url, token, target_uuid, data=None):
    if not token:
        logger.error("Token is required for updating targets.")
        return None
    if not target_uuid:
        logger.error("Target UUID is required.")
        return None

    # If no data is provided, send an empty body
    if data is None:
        data = {}

    try:
        logger.info(f"Attempting to update target with UUID: {target_uuid}...")
        url = f"{api_url}{TARGETS_ENDPOINT}/{target_uuid}"
        
        # Sending the PUT request to update the target
        response = request_with_retries("PUT", url, data=data, headers={"cookie": token})
        # Rediscover the target after editing it
        rediscover = request_with_retries("POST", url + "?rediscover=true", headers={"cookie": token})

        # Check if the response was successful
        if response.status_code == 200 and rediscover.status_code == 200:
            logger.info(f"Target {target_uuid} successfully updated.")
            return response.json()
        else:
            logger.error(f"Failed to update target {target_uuid}. Status code: {response.status_code}.")
            return None
    except Exception as e:
        logger.error(f"Error occurred while updating target {target_uuid}: {e}")
        return None

if __name__ == "__main__":
    # Information to be passed from command line or configuration
    API_URL = "https://url"
    username = "administrator"
    password = "administrator"
    filepath =  "filepath here"
    # Run the script
    run_targets_script(api_url=API_URL, username=username, password=password, filepath=filepath)
