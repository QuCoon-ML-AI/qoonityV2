import boto3, json
import os
from qooneous import qoonity_head
from botocore.exceptions import ClientError

session = boto3.Session()


aws_access_key_id = os.getenv("aws_access_key_id")
aws_secret_access_key = os.getenv("aws_secret_access_key")
region_name = os.getenv("region_name")

bedrock = session.client(service_name='bedrock-runtime', region_name="us-east-1", aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
modelId = "anthropic.claude-3-5-sonnet-20240620-v1:0"
memory_list = []

tool_list = [
    {
        "toolSpec": {
            "name": "application_design",
            "description": "Design an application based on the user's requirements.",
            "inputSchema": {
                "json": {
                    "type": "object",  # Change type to object
                    "properties": {
                        "request_type": {
                            "type": "string",
                            "description": "The type of request. Always set to 'application_design'.",
                            "enum": ["application_design"]
                        },
                        "application_details": {
                            "type": "object",
                            "properties": {
                                "applicationName": {
                                    "type": "string",
                                    "description": "A name that suits the app in Capitalized case, restrict to at most 3 words, Example: UserManagementPortal"
                                },
                                "applicationDescription":{
                                    "type": "string",
                                    "description": "a one or two lines short description of the app",
                                    "maxLength": 50
                                },
                                "applicationTablePrefix": {
                                    "type": "string",
                                    "description": "a unique 3 or 4 letter prefix for the application, example QNT for Qoonity, UMPL for UserManagementPortal",
                                    "maxLength": 4
                                }

                            }
                        },
                        "entities": {  # Wrap the array in an object property
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "entityName": {
                                        "type": "string",
                                        "description": "The name of the entity."
                                    },
                                    "entityIsAUser":{
                                        "type": "boolean",
                                        "description": "Decribes if the entity is a kind of user on the app, this will be helpful to set up authentication."
                                    },
                                    "attributes": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "attributeName": {
                                                    "type": "string",
                                                    "description": "The name of the attribute."
                                                },
                                                "attributeDataType": {
                                                    "type": "string",
                                                    "description": "The data type of the attribute."
                                                },
                                                "attributeCanBeUserName":{
                                                    "type": "boolean",
                                                    "description": "This defines if the user can use the attribute as a username for authentication"
                                                },
                                                "isPrimaryKey": {
                                                    "type": "boolean",
                                                    "description": "If the attribute is the primary key for that entity."
                                                },
                                                "foreignKey": {
                                                    "type": "object",
                                                    "properties": {
                                                        "isForeignKey": {
                                                            "type": "boolean",
                                                            "description": "If the attribute is a foreign key."
                                                        },
                                                        "foreignKeyRefrenceEntity": {
                                                            "type": "string",
                                                            "description": "The entity the attribute is a foreign key to. Return NA if not applicable. Always return value even if not applicable."
                                                        },
                                                        "foreignKeyRefrenceAttribute": {
                                                            "type": "string",
                                                            "description": "The attribute the foreign key references. Return NA if not applicable. Always return value even if not applicable"
                                                        }
                                                    },
                                                    "required": ["isForeignKey", "foreignKeyRefrenceEntity", "foreignKeyRefrenceAttribute"]
                                                    
                                                }
                                            },
                                            "required": ["attributeName", "attributeCanBeUserName","attributeDataType", "isPrimaryKey", "foreignKey"]
                                        }
                                    }
                                },
                                "required": ["entityName", "entityIsAUser","attributes"]
                            }
                        },
                        "response": {
                            "type": "string",
                            "description": """
                            The response to the user summarizing the application design and thought process, highlighting only very important details.
                            Always ask for feedback and make suggestions to improve the design.
                            The response should follow a causal conversational style.
                            """,
                           "maxLength": 500,
                        }
                    },
                    "required": ["request_type", "entities", "response"]  # Require Entities and response
                }
            }
        }
    },
    {
        "toolSpec": {
            "name": "generic_request",
            "description": "Helps to interact with the user.",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "request_type": {
                            "type": "string",
                            "description": "The type of request. Always set to 'generic_request'.",
                            "enum": ["generic_request"]
                        },
                        "response": {
                            "type": "string",
                            "description": "The response to the user.",
                            "maxLength": 500
                        }
                    },
                    "required": ["request_type", "response"]
                }
            }
        }
    }
    
]

# Function to fetch a response from the model
def get_completion(prompt, system_prompt=None):
    inference_config = {
        "temperature": 0.0
    }
    tools = {
                "tools": tool_list
            }
    
    converse_api_params = {
        "modelId": modelId,
        "messages": [{"role": "user", "content": [{"text": prompt}]}],
        "inferenceConfig": inference_config,
        "toolConfig": tools
    }
    if system_prompt:
        converse_api_params["system"] = [{"text": system_prompt}]
    
    
    try:
        response = bedrock.converse(**converse_api_params)

        response_message = response['output']['message']

        response_content_blocks = response_message['content']

        content_block = next((block for block in response_content_blocks if 'toolUse' in block), None)

        tool_use_block = content_block['toolUse']

        tool_result_dict = tool_use_block['input']
        
        if "response" in tool_result_dict:
            return tool_result_dict
        return {
                "request_type": "generic_request",
                "response": response_message
            }
        

            

    except ClientError as err:
        message = err.response['Error']['Message']
        print(f"A client error occurred: {message}")
        return None

# Load memory from file if it exists and is valid
file_path = 'memory.txt'
if os.path.exists(file_path):
    try:
        with open(file_path, 'r') as file:
            memory_list = json.load(file)
            print(f"Memory loaded from {file_path}")
    except json.JSONDecodeError:
        print("Error: memory.txt is empty or contains invalid JSON. Starting fresh.")
        memory_list = [] 
else:
    print("No memory file found, starting fresh.")

def get_response(prompt, system_prompt=None):
    try:
        system_prompt = qoonity_head
        
        # Use the loaded memory when generating the completion
        response = get_completion(prompt + " " + str(memory_list), system_prompt)
        
        if response:  # Only process if the response is valid
            memory_list.append(f"prompt: {prompt}, response: {response}")
            #print("Response:", json.dumps(response, indent=4))
            #print("Memory:", memory_list)

            # Save memory to a file
            with open(file_path, 'w') as file:
                json.dump(memory_list, file, indent=4)

            
            print(f"Memory successfully written to {file_path}")
            return response
        else:
            print("No response from the model. Please try again.")
            return None     
    except Exception as e:
        print(f"An error occurred: {e}")

