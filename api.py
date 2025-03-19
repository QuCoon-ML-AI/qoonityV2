import requests
import json

base_url = "https://33ga2ruf6d.execute-api.us-east-1.amazonaws.com"
stage = "dev"

def call_api(url, method="GET", headers=None, payload=None):
    try:
        method = method.upper()
        headers = headers or {}  # Ensure headers is a dictionary

        if method == "POST":
            response = requests.post(url, json=payload, headers=headers)
        elif method == "PUT":
            response = requests.put(url, json=payload, headers=headers)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        else:
            response = requests.get(url, headers=headers)

        # Check for successful response
        if response.status_code in {200, 201, 204}:  
            try:
                return response.json()  # Return JSON response if possible
            except ValueError:
                return response.text  # Return text response if JSON parsing fails
        else:
            return {"error": f"HTTP {response.status_code}", "message": response.text}

    except requests.exceptions.RequestException as e:
        return {"error": "Request failed", "message": str(e)}


def login():
    url = base_url+f"/api/{stage}/authentication/login"
    method = "POST"
    headers = None
    payload = {
    "deviceId": "string",
    "latitude": "string",
    "longitude": "string",
    "userEmail": "dagbuelawrence@yopmail.com",
    "userPassword": "123456"
    }

    response = call_api(url, method, headers=headers, payload=payload)
    return response

def create_application(bearer_token,payload):
    url = base_url + f"/api/{stage}/application/create"  
    method = "POST"
    
    headers = {
        "Authorization": bearer_token,  
        "Content-Type": "application/json"
    }
    
    # Merge default values with user input
    payload = {
        "applicationArchitecture": payload.get("applicationArchitecture",None),
        "applicationCloudCompute": payload.get("applicationCloudCompute", None),
        "applicationCloudProvider": payload.get("applicationCloudProvider", None),
        "applicationDatabase": payload.get("applicationDatabase", None),
        "applicationDescription": payload.get("applicationDescription", None),
        "applicationFramework": payload.get("applicationFramework", None),
        "applicationLanguage": payload.get("applicationLanguage", None),
        "applicationName": payload.get("applicationName", None),
        "applicationProjectId": payload.get("applicationProjectId", 143),
        "applicationUserId": payload.get("applicationUserId", 143),
        "applicationWorkspaceId": payload.get("applicationWorkspaceId", 143),
    }
    response = call_api(url, method, headers=headers, payload=payload)
    return response

def get_application_by_name(bearer_token,applicationName):
    url = base_url + f"/api/{stage}/application/read-by-application-name/{applicationName}"  
    method = "GET"
    
    headers = {
        "Authorization": bearer_token,  
        "Content-Type": "application/json"
    }
    
    response = call_api(url, method, headers=headers, payload=None)
    return response

def get_entity_by_name(bearer_token,entityName):
    url = base_url + f"/api/{stage}/entity/read-by-entity-name/{entityName}"  
    method = "GET"
    
    headers = {
        "Authorization": bearer_token,  
        "Content-Type": "application/json"
    }
    
    response = call_api(url, method, headers=headers, payload=None)
    return response



def bulk_create_entity(bearer_token,payload):
    url = base_url + f"/api/{stage}/bulk-entity/bulk-create"  
    method = "POST"
    
    headers = {
        "Authorization": bearer_token,  
        "Content-Type": "application/json"
    }
   
    response = call_api(url, method, headers=headers, payload=payload)
    return response

def bulk_create_attribute(bearer_token,payload):
    url = base_url + f"/api/{stage}/bulk-attribute/bulk-create"  
    method = "POST"
    
    headers = {
        "Authorization": bearer_token,  
        "Content-Type": "application/json"
    }

    response = call_api(url, method, headers=headers, payload=payload)
    return response

def create_auth_config(bearer_token,payload):
    url = base_url + f"/api/{stage}/authentication-config/create"  
    method = "POST"
    
    headers = {
        "Authorization": bearer_token,  
        "Content-Type": "application/json"
    }
    
    # Merge default values with user input
    payload = {
        "authenticationConfigApplicationId": payload.get("authenticationConfigApplicationId",None),
        "authenticationConfigGenerateLink":  payload.get("authenticationConfigGenerateLink",None),
        "authenticationConfigGenerateOtp":  payload.get("authenticationConfigGenerateOtp",None),
        "authenticationConfigIsPasswordEncrypted":  payload.get("authenticationConfigIsPasswordEncrypted",None),
        "authenticationConfigNonReusableRecentPassword":  payload.get("authenticationConfigNonReusableRecentPassword",None),
        "authenticationConfigPasswordAttribute":  payload.get("authenticationConfigPasswordAttribute",None),
        "authenticationConfigRoleIdAttribute":  payload.get("authenticationConfigRoleIdAttribute",None),
        "authenticationConfigSendEmail":  payload.get("authenticationConfigSendEmail",None),
        "authenticationConfigSendSms":  payload.get("authenticationConfigSendSms",None),
        "authenticationConfigUserEntity":  payload.get("authenticationConfigUserEntity",None),
        "authenticationConfigUsernameAttribute":  payload.get("authenticationConfigUsernameAttribute",None)
        }
    
    response = call_api(url, method, headers=headers, payload=payload)
    return response

def get_entity_by_application_id(bearer_token,entityApplicationId):
    url = base_url + f"/api/{stage}/entity/read-by-entity-application-id/{entityApplicationId}"  
    method = "GET"
    
    headers = {
        "Authorization": bearer_token,  
        "Content-Type": "application/json"
    }
    
    response = call_api(url, method, headers=headers, payload=None)
    return response


base_url_deploy = "https://api.qoonity.com"

def code_deploy(applicationId):
    url = base_url_deploy + f"/{stage}/application/deploy/{applicationId}" 
    method = "GET"

    response = call_api(url, method)
    return response

def code_download(applicationId):
    url = base_url_deploy + f"/{stage}/application/download/{applicationId}" 
    method = "GET"

    #response = call_api(url, method)
    return url

def code_s3_url(applicationId):
    url = base_url_deploy + f"/{stage}/application/s3download/{applicationId}" 
    method = "GET"

    response = call_api(url, method)
    return response