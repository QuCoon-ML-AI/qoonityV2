def generate_attribute_table(entities):
    table_data = []

    
    for entity in entities:
        entityName = entity["entityName"]
        for attribute in entity["attributes"]:
            table_row = {}
            table_row["attributeId"] = None
            table_row["attributeEntityId"] = None
            table_row["attributeName"] = attribute["attributeName"]

            # Datatype
            if attribute["attributeDataType"] == 'string':
                table_row["attributeDataType"] = 'String'
            elif attribute["attributeDataType"] == 'integer':
                table_row["attributeDataType"] = 'Int'
            elif attribute["attributeDataType"] == 'datetime':
                table_row["attributeDataType"] = 'Datetime'
            else:
                table_row["attributeDataType"] = 'String'

            # Foreign Key
            if attribute["foreignKey"]["isForeignKey"]:
                table_row["attributeForeignKey"] = 'YES'
            else:
                table_row["attributeForeignKey"] = 'NO'

            # Primary Key
            if attribute["isPrimaryKey"]:
                table_row["attributePrimaryKey"] = 'YES'
            else:
                table_row["attributePrimaryKey"] = 'NO'

            # Other attributes
            table_row["attributeNull"] = 'NO' if attribute["isPrimaryKey"] else 'YES'
            table_row["attributeAutoIncrement"] = 'YES' if attribute["isPrimaryKey"] else 'NO'
            table_row["attributeUnique"] = 'NO'

            if attribute["isPrimaryKey"]:
                table_row["attributeStartValue"] = 100
                table_row["attributeStep"] = 1
                table_row["attributeDefaultValue"] = 100
            else:
                table_row["attributeStartValue"] = None
                table_row["attributeStep"] = None
                table_row["attributeDefaultValue"] = None

            # Default values for specific attributes
            if attribute["attributeName"].endswith("Status"):
                table_row["attributeDefaultValue"] = '\'ACTIVE\''
            if attribute["attributeName"].endswith("CreatedAt"):
                table_row["attributeDefaultValue"] = "getdate()"
            if attribute["attributeName"].endswith("UpdatedAt"):
                table_row["attributeDefaultValue"] = "getdate()"

            table_row["attributeValueList"] = None
            
            # Length Data
            if attribute["attributeDataType"] == 'string':
                table_row["attributeLength"] = 100
            elif attribute["attributeDataType"] == 'integer':
                table_row["attributeLength"] = None
            elif attribute["attributeDataType"] == 'datetime':
                table_row["attributeLength"] = None
            
            
            table_row["attributeDecimalLimit"] = None

            # Test Data
            if attribute["attributeDataType"] == 'string':
                table_row["attributeTestData"] = 'Test'
            elif attribute["attributeDataType"] == 'integer':
                table_row["attributeTestData"] = 1001
            elif attribute["attributeDataType"] == 'datetime':
                table_row["attributeTestData"] = '2022-01-01 00:00:00'

            # Status and timestamps
            table_row["attributeStatus"] = 'ACTIVE'
            table_row["attributeCreatedAt"] = None
            table_row["attributeUpdatedAt"] = None

            # Foreign key references
            if attribute["foreignKey"]["isForeignKey"]:
                table_row["attributeReferenceEntity"] = attribute["foreignKey"].get("foreignKeyRefrenceEntity", None)
                table_row["attributeReferenceAttribute"] = attribute["foreignKey"].get("foreignKeyRefrenceAttribute", None)
            else:
                table_row["attributeReferenceEntity"] = None
                table_row["attributeReferenceAttribute"] = None

            # Required fields for create, update, and delete
            table_row["attributeIsRequiredCreate"] = 'NO' if attribute["attributeName"].endswith("Status") or attribute["attributeName"].endswith("CreatedAt") or attribute["attributeName"].endswith("UpdatedAt") else 'YES'
            if attribute["isPrimaryKey"]:
                table_row["attributeIsRequiredCreate"] = 'NO'
            table_row["attributeIsRequiredUpdate"] = 'NO' if attribute["attributeName"].endswith("CreatedAt") or attribute["attributeName"].endswith("UpdatedAt") else 'OPTIONAL'
            if attribute["isPrimaryKey"]:
                table_row["attributeIsRequiredUpdate"] = 'YES'
            table_row["attributeIsRequiredDelete"] = 'YES' if attribute["isPrimaryKey"] else 'NO'

            table_row["entity"] = entityName
            # Add the row to the table data list
            table_data.append(table_row)

       

    return table_data


def generate_entity_table(entities):
    table_data = []
    for entity in entities:
        
        table_row = {}

        table_row["entityId"] = None
        table_row["entityApplicationId"] = None

        table_row["entityName"] = entity["entityName"]
        table_row["entityDescription"] = entity["entityName"]

        table_row["entityStatus"] = "ACTIVE"
        table_row["entityCreatedAt"] = None
        table_row["entityUpdatedAt"] = None
        table_data.append(table_row)
    
    return table_data

def generate_auth_config_table(auth_entity):
    table_row =  {}

    table_row["authenticationConfigId"] = None
    table_row["authenticationConfigApplicationId"] = None

    table_row["authenticationConfigUserEntity"] = auth_entity["authenticationConfigUserEntity"]
    table_row["authenticationConfigUsernameAttribute"] = auth_entity["authenticationConfigUsernameAttribute"]
    table_row["authenticationConfigPasswordAttribute"] = auth_entity["authenticationConfigPasswordAttribute"]
    table_row["authenticationConfigRoleIdAttribute"] = None

    table_row["authenticationConfigSendSms"] = "YES"
    table_row["authenticationConfigSendEmail"] = "YES"
    table_row["authenticationConfigGenerateOtp"] = "YES"
    table_row["authenticationConfigGenerateLink"] = "YES"
    table_row["authenticationConfigNonReusableRecentPassword"] = "NO"
    table_row["authenticationConfigIsPasswordEncrypted"] = "NO"

    table_row["authenticationConfigStatus"] = "ACTIVE"
    table_row["authenticationConfigCreatedAt"] = None
    table_row["authenticationConfigUpdatedAt"] = None
    
    return table_row

