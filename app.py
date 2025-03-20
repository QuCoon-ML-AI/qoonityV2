import streamlit as st
from main import get_response
import time
import pandas as pd
import service
import api
import io
import concurrent.futures
from github import GitHubManager
import os
import requests

st.title('Qoonity.ai🤖')
st.write('Welcome to Qoonity.ai!')

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []

if "application_details" not in st.session_state:
    st.session_state.application_details = {}

if "entities" not in st.session_state:
    st.session_state.entities = []

if "tables_created" not in st.session_state:
    st.session_state.tables_created = False

if "application_created" not in st.session_state:
    st.session_state.application_created = False

if "entities_created" not in st.session_state:
    st.session_state.entities_created = False

if "attributes_created" not in st.session_state:
    st.session_state.attributes_created = False

# Initialize response_type
if "response_type" not in st.session_state:
    st.session_state.response_type = ""

if "application_table_data" not in st.session_state:
    st.session_state.application_table_data = {}

if "application_id" not in st.session_state:
    st.session_state.application_id = 0

# Initialize session state for button tracking
if "downloading" not in st.session_state:
    st.session_state.downloading = False

if "deploying" not in st.session_state:
    st.session_state.deploying = False

if "auth_config_data" not in st.session_state:
    st.session_state.auth_config_data = {}

if "entities_with_auth" not in st.session_state:
    st.session_state.entities_with_auth = []

if "auth_user" not in st.session_state:
    st.session_state.auth_user = None

if "auth_username" not in st.session_state:
    st.session_state.auth_username = None

if "auth_config_created" not in st.session_state:
    st.session_state.auth_config_created = False

if "auth_user_entity" not in st.session_state:
    st.session_state.auth_user_entity = []

if "new_application" not in st.session_state:   
    st.session_state.new_application = ""

if "application_create" not in st.session_state:
    st.session_state.application_create = ""

if "auth_config_table_create" not in st.session_state:
    st.session_state.auth_config_table_create = ""

if "applicatiion_entities" not in st.session_state:
    st.session_state.applicatiion_entities = []

if "file_exist" not in st.session_state:
    st.session_state.file_exist = False

if 'github_manager' not in st.session_state:
    # Get token from secrets (recommended) or other secure storage
    #github_token = st.secrets.github.token  # Configure in Streamlit secrets
    github_token = os.getenv("GITHUB_TOKEN")
    st.session_state.github_manager = GitHubManager(github_token)

# Cache the API response to avoid redundant calls
@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_code_data(applicationId):
    # Simulate a long-running API call
    time.sleep(10)  # Replace this with your actual API call
    file_data = api.code_download(applicationId)
    return file_data

def fetch_deploy_url(applicationId):
    time.sleep(10)  # Simulate API call
    deploy_config = api.code_deploy(applicationId)
    apiUrl = deploy_config["apiUrl"]
    return apiUrl

# Function to check if the file exists
def file_exists(file_path):
    """Check if the file exists at the given path."""
    return os.path.exists(file_path)

# Sidebar Chat
with st.sidebar:
    messages = st.container(height=650)
    
    # Display chat messages from history
    for message in st.session_state.messages:
        messages.chat_message(message["role"]).write(message["content"])
            
    if prompt := st.chat_input("What would you like to build today?"):
        messages.chat_message("user").write(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        with messages:
            with st.spinner('Wait for it...'):
                # Pass the message history to the get_response function
                response = get_response(prompt, st.session_state.messages)
                time.sleep(1)
        
        st.session_state.response_type = response.get("request_type", "generic_request")
        chat_response = response.get("response", "I'm sorry, I didn't understand that.")
        response.pop("response", None)
        messages.chat_message("assistant").write(chat_response)
        st.session_state.messages.append({"role": "assistant", "content": chat_response})

        if st.session_state.response_type == "application_design":
            st.session_state.application_details = response.get("application_details", {})
            st.session_state.entities = response.get("entities", [])

# Using the response_type safely
if st.session_state.response_type == "application_design":
    application_details = st.session_state.application_details
    new_entities = st.session_state.entities

    if new_entities:
        for entity in new_entities:
            st.subheader(f"{entity['entityName']}", divider=True)
            entity_df = pd.DataFrame(entity["attributes"])

            entity_df = entity_df[["attributeName", "attributeDataType"]]
            entity_df.columns = ["Attribute", "Datatype"]

            def add_emoji(datatype):
                emoji_map = {
                    "string": "🟨",
                    "integer": "🟦",
                    "datetime": "🟥",
                }
                return f"{datatype.upper()} {emoji_map.get(datatype, '')}"

            entity_df["Datatype"] = entity_df["Datatype"].apply(add_emoji)
            st.data_editor(entity_df)


# Application Details Form
if st.session_state.entities:
    with st.form("Application Configuration"):
        application_details = st.session_state.application_details
        application_name = st.text_input("Application Name", application_details.get("applicationName", ""))
        application_description = st.text_input("Application Description", application_details.get("applicationDescription", ""))
        application_prefix = st.text_input("Application Prefix", application_details.get("applicationTablePrefix", ""))

        application_architecture = st.selectbox("Application Architecture", ["Web App", "Mobile App"])
        application_language = st.selectbox("Application Language", ["Kotlin", "Java", "Javascript", "Python"])
        application_framework = st.selectbox("Application Framework", ["SpringBoot", "Koin", "Django", "FastAPI", "Node.js"])
        application_cloud = st.selectbox("Application Cloud Provider", ["AWS", "Azure", "GCP", "Huawei"])
        application_compute = st.selectbox("Application Compute Mode", ["Serverless", "VM", "Container"])
        application_database = st.selectbox("Application Database", ["Microsoft SQL", "MySQL", "SQL Server"])

        submitted = st.form_submit_button("Submit App Configuration")
        if submitted:
            application_table_data = {
                "applicationId": None,
                "applicationProjectId": 100,
                "applicationUserId": 103,
                "applicationName": application_name,
                "applicationDescription": application_description,
                "applicationArchitecture": application_architecture,
                "applicationFramework": application_framework,
                "applicationLanguage": application_language,
                "applicationCloudProvider": application_cloud,
                "applicationCloudCompute": application_compute,
                "applicationDatabase": application_database,
                "applicationTablePrefix": application_prefix,
                "applicationStatus": "ACTIVE",
                "applicationCreatedAt": None,
                "applicationUpdatedAt": None,
                "applicationWorkplaceId": 100,
                "applicationEnableMakerChecker": "NO"
            }
            st.session_state.application_table_data = application_table_data

if st.session_state.application_table_data:
    if st.session_state.entities:
        user_like_entities = [entity for entity in st.session_state.entities if entity.get("entityIsAUser")]
    
        with st.form("Auth Entity Configuration"):
            # Store previous selection to detect changes
            previous_auth_user = st.session_state.get("auth_user")
            
            # User entity selection
            new_auth_user = st.radio(
                "Please select the user for Authentication",
                [entity['entityName'] for entity in user_like_entities],
                key="auth_user_radio",
                index=0
            )
            
            submitted = st.form_submit_button("Submit Auth Configuration")
            if submitted:
                # Clear username if entity changes
                if new_auth_user != previous_auth_user:
                    st.session_state.auth_username = None
                    
                # Update auth user in session state
                st.session_state.auth_user = new_auth_user
            
                # Get the selected user entity
                auth_user_entity = next(
                    (e for e in user_like_entities if e["entityName"] == new_auth_user),
                    None
                )
                st.session_state.auth_user_entity = auth_user_entity
        
    # Modified Auth Attribute Configuration form
    if st.session_state.auth_user_entity:
        with st.form("Auth Attribute Configuration"):
            # Get fresh attributes list based on current entity
            username_attrs = [
                attr for attr in st.session_state.auth_user_entity["attributes"] 
                if attr.get("attributeCanBeUserName")
            ]
            
            if username_attrs:
                # Always get current entity's attributes
                current_username = st.radio(
                    "Please select the Attribute for Username",
                    [attr['attributeName'] for attr in username_attrs],
                    key="auth_username_radio",
                    index=0  # Always reset to first option
                )
                st.session_state.auth_username = current_username
            else:
                st.error("No username attributes found in selected user entity!")

            submitted = st.form_submit_button("Submit Auth Configuration")
            if submitted:
                auth_config_data = {
                    "authenticationConfigUserEntity" : st.session_state.auth_user,
                    "authenticationConfigUsernameAttribute" :  st.session_state.auth_username,
                    "authenticationConfigPasswordAttribute" : f"{str(st.session_state.auth_user).lower()}Password"
                }
                st.session_state.auth_config_data = auth_config_data

if st.session_state.auth_config_data:
    if st.session_state.auth_user_entity:
        # Add password attribute
        password_attribute = {
            "attributeName": f"{st.session_state.auth_user_entity['entityName'].lower()}Password",
            "attributeCanBeUserName": False,
            "attributeDataType": "string",
            "isPrimaryKey": False,
            "foreignKey": {
                "isForeignKey": False,
                "foreignKeyRefrenceEntity": "NA",
                "foreignKeyRefrenceAttribute": "NA"
            }
        }
        
        # Update entities with password
        updated_entities = []
        for entity in st.session_state.entities:
            if entity["entityName"] == st.session_state.auth_user:
                if not any(attr["attributeName"] == password_attribute["attributeName"] 
                        for attr in entity["attributes"]):
                    entity["attributes"].append(password_attribute)
            updated_entities.append(entity)
        
        st.session_state.entities = updated_entities
        st.info(f"Added {str(st.session_state.auth_user_entity['entityName']).lower()}Password to {str(st.session_state.auth_user_entity['entityName'])} for Authentication")     
                


if st.session_state.auth_config_data:
    st.info("Let's go ahead to Deploy!")
    if st.button("Generate Qoonity Excel"):
            entities = st.session_state.entities

            application_table_df = pd.DataFrame([st.session_state.application_table_data])
            st.session_state.generated_application_table = application_table_df
            st.write("Application Table")
            st.dataframe(application_table_df)

            entity_table_data = service.generate_entity_table(entities)
            entity_table_df = pd.DataFrame(entity_table_data)
            st.session_state.generated_entity_table = entity_table_df
            st.write("Entity Table")
            st.dataframe(entity_table_df)

            attribute_table_data = service.generate_attribute_table(entities)
            attribute_table_df = pd.DataFrame(attribute_table_data).drop("entity",axis=1)
            st.session_state.generated_attribute_table = attribute_table_df
            st.write("Attribute Table")
            st.dataframe(attribute_table_df)

            auth_config_data = st.session_state.auth_config_data 
            auth_config_data = service.generate_auth_config_table(auth_config_data)
            auth_config_data_df = pd.DataFrame([auth_config_data])
            st.session_state.generated_auth_config_table = auth_config_data_df
            st.write("Auth Config Table")
            st.dataframe(auth_config_data_df)
        
            st.session_state.tables_created = True


# Deploy Application
if st.session_state.auth_config_data:
    if st.button("QooDeploy"):
        with st.spinner('Logging in...'):
            st.session_state.login_auth_data = api.login()
            auth_token = st.session_state.login_auth_data.get("token", None)

            if not auth_token:
                st.error("Authentication Failed!")
                st.stop()

        # Process 1: Configure Application
        with st.spinner('Configuring Application'):
            st.session_state.application_create = api.create_application(auth_token, st.session_state.application_table_data)
            if st.session_state.application_create["responseCode"] == "00":
                st.session_state.new_application = api.get_application_by_name(auth_token, st.session_state.application_table_data["applicationName"])
                if st.session_state.new_application["responseCode"] == "00":
                    st.session_state.application_created = True
                    new_application_id = st.session_state.new_application["data"][0]["applicationId"]
                    st.session_state.application_id = new_application_id
                    st.success("Application Configuration Done ✅")
                else:
                    st.error(f"Application Configuration Failed: {st.session_state.new_application['responseMessage']}")
            else:
                st.error(f"Application Configuration Failed: {st.session_state.application_create['responseMessage']}")
            time.sleep(1)

        # Process 2: Configure Entities
        if st.session_state.application_created:
            with st.spinner('Configuring Entities'):
                entity_table_data = service.generate_entity_table(st.session_state.entities)
                for entity in entity_table_data:
                    print(new_application_id)
                    entity["entityApplicationId"] = st.session_state.application_id  # Assign new app ID
                
                entity_create = api.bulk_create_entity(auth_token, entity_table_data)
                
                if entity_create["responseCode"] == "00":
                    st.session_state.entities_created = True
                    st.success("Entity Configuration Done ✅")
                else:
                    st.error("Entity Configuration Failed")
                time.sleep(1)

        # Process 3: Configure Attributes
        if st.session_state.entities_created:
            with st.spinner('Configuring Attributes'):
                attribute_table_data = service.generate_attribute_table(st.session_state.entities)
                application_entities = api.get_entity_by_application_id(auth_token, st.session_state.application_id).get("data",None)
                
                
                for attribute in attribute_table_data:
                    attribute_entity_name = attribute["entity"]
                    entity_id = [item["entityId"] for item in application_entities if item["entityName"] == attribute_entity_name][0]

                    attribute["attributeEntityId"] = entity_id
                st.session_state.attribute_create = api.bulk_create_attribute(auth_token, attribute_table_data)
                if st.session_state.attribute_create["responseCode"] == "00":
                    st.session_state.attributes_created = True
                    st.success("Attribute Configuration Done ✅")
                else:
                    st.error("Attribute Configuration Failed")
        
        # Process 4: Configure Authentication
        if st.session_state.attributes_created:
            with st.spinner('Configuring Authentication'):
                auth_config_table_data = service.generate_auth_config_table(st.session_state.auth_config_data)
                #print(auth_config_table_data)
                auth_config_table_data["authenticationConfigApplicationId"] = st.session_state.application_id
                auth_config_table_data["authenticationConfigRoleIdAttribute"] = st.session_state.auth_username
                st.session_state.auth_config_table_create = api.create_auth_config(auth_token, auth_config_table_data)
                #print(auth_config_table_create)
                if st.session_state.auth_config_table_create["responseCode"] == "00":
                    st.session_state.auth_config_created = True
                    st.success("Auth Config Configuration Done ✅")
                else:
                    st.error("Auth Config Configuration Failed")
        
    
if st.session_state.auth_config_created and st.session_state.application_id:
    if st.session_state.application_id:
        applicationId = st.session_state.get("application_id")
        file_url= api.code_download(applicationId)
        print(file_url)
        # Display a download button that redirects to the file URL
        st.markdown(f"[🔗 Click here to download]( {file_url} )", unsafe_allow_html=True)

# Ensure you check the session state keys first
if st.session_state.auth_config_created and st.session_state.application_id:
    application_id = st.session_state.get("application_id")
    
    if application_id:
        application_name = st.session_state.application_table_data.get(
            "applicationName", 
            f"APP_{st.session_state.application_table_data.get('applicationId')}"
        )

        # Simplified UI - direct push button
        if st.button("Push to GitHub"):
            try:
                # Get S3 download URL from your API
                api_response = api.code_s3_url(application_id)
                if not api_response or 's3Url' not in api_response:
                    st.error("Failed to get download URL")
                    st.stop()

                # Download zip content directly
                with st.spinner('Downloading and deploying code...'):
                    response = requests.get(api_response['s3Url'])
                    response.raise_for_status()
                    zip_content = response.content

                    # Push using GitHub manager
                    success = st.session_state.github_manager.push_zip_to_repo(
                        repo_owner="QuCoon-ML-AI",
                        repo_name=application_name,
                        zip_content=zip_content,
                        commit_message=f"Initial commit for {application_name}"
                    )

                    if success:
                        github_link = f"https://github.com/QuCoon-ML-AI/{application_name}"
                        st.markdown(f"[🔗 GitHub Repo]({github_link})", unsafe_allow_html=True)
                        st.success("Code successfully pushed to GitHub!")
                    else:
                        st.error("Failed to push code to GitHub")

            except requests.exceptions.RequestException as e:
                st.error(f"S3 download failed: {str(e)}")
            except Exception as e:
                st.error(f"Deployment failed: {str(e)}")

    

# SEPARATE DEPLOY TO CLOUD BUTTON (outside QooDeploy callback)
if st.session_state.auth_config_created and st.session_state.application_id:
    if st.button("Deploy to Cloud"):
        with st.spinner("Configuring Cloud Environment, Deploying..."):
            try:
                applicationId = st.session_state.application_id
                
                # Use a single background thread with timeout
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(fetch_deploy_url, applicationId)
                    try:
                        swagger_link = future.result(timeout=300)
                        
                        # Streamlit UI updates must happen in the main thread
                        if swagger_link:
                            st.success("Deployment Successful!")
                            st.markdown(f"[Click here to access Swagger]({swagger_link})", unsafe_allow_html=True)
                            st.text_input("Swagger URL", swagger_link)
                        else:
                            st.error("Failed to get deployment URL")
                            
                    except concurrent.futures.TimeoutError:
                        st.error("Deployment timed out after 5 minutes. Please try again.")
                        future.cancel()
                        
            except Exception as e:
                st.error(f"Deployment failed: {str(e)}")