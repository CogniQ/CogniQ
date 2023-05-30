# Azure Changelog

A record of configurations on Azure.


# 20230528 - Deploy CogniQ to CogniQ Community Slack


The application will run in the CogniQ Community Dev subscription, sponsored by [startops](https://startops.us)

> Instructions from [https://learn.microsoft.com/en-us/azure/container-instances/container-instances-github-action?tabs=openid](https://learn.microsoft.com/en-us/azure/container-instances/container-instances-github-action?tabs=openid)


1. Create an Azure Active Directory (Azure AD) application and service principal that can be used with the role-based access control
`az ad app create --display-name cogniq-gha`

> Capture the appId from the output and set as AZURE_CLIENT_ID in .envrc and as a GitHub Secret

`export AZURE_CLIENT_ID=REDACTED`

> Note the objectId value when creating federated credentials with Graph API so set it as the APPLICATION_OBJECT_ID.

`export AZURE_APPLICATION_OBJECT_ID=REDACTED`

2. Create a Service Principal

`az ad sp create --id ${AZURE_CLIENT_ID}`

> Capture the appOwnerTenantId/appOwnerOrganizationId from the output and set as AZURE_TENANT_ID in .envrc and as a GitHub Secret

`export AZURE_TENANT_ID=REDACTED`

> Note the objectId from this step. This is the ASSIGNEE_OBJECT_ID

`export AZURE_ASSIGNEE_OBJECT_ID=REDACTED`

3. Create a new role assignment by subscription and object.

```bash
az role assignment create \
  --role contributor \
  --subscription ${AZURE_SUBSCRIPTION_ID} \
  --assignee-object-id ${AZURE_ASSIGNEE_OBJECT_ID} \
  --scope /subscriptions/${AZURE_SUBSCRIPTION_ID}/resourceGroups/${AZURE_RESOURCE_GROUP_NAME} \
  --assignee-principal-type ServicePrincipal
```

4. Run the following command to create a new [federated identity credential](https://learn.microsoft.com/en-us/graph/api/application-post-federatedidentitycredentials?) for your active directory application.

```bash
cat > credential.json
{
    "name": "cogniq-gha-main",
    "issuer": "https://token.actions.githubusercontent.com/",
    "subject": "repo:CogniQ/CogniQ:ref:refs/heads/main",
    "description": "cogniq-gha-main",
    "audiences": [
        "api://AzureADTokenExchange"
    ]
}

az ad app federated-credential create --id ${AZURE_APPLICATION_OBJECT_ID} --parameters credential.json

```

Again for pull requests.

```bash
cat > credential.json
{
    "name": "cogniq-gha-pull-requests",
    "issuer": "https://token.actions.githubusercontent.com/",
    "subject": "repo:CogniQ/CogniQ:pull_request",
    "description": "cogniq-gha-pull-request",
    "audiences": [
        "api://AzureADTokenExchange"
    ]
}

az ad app federated-credential create --id ${AZURE_APPLICATION_OBJECT_ID} --parameters credential.json
```

Again for the cogniq-community-main environment.

```bash
cat > credential.json
{
    "name": "cogniq-gha-environment-cogniq-community-main",
    "issuer": "https://token.actions.githubusercontent.com/",
    "subject": "repo:CogniQ/CogniQ:environment:cogniq-community-main",
    "description": "cogniq-gha-environment-cogniq-community-main",
    "audiences": [
        "api://AzureADTokenExchange"
    ]
}

az ad app federated-credential create --id ${AZURE_APPLICATION_OBJECT_ID} --parameters credential.json
```





5. Grant Azure Container Instances access

Grant [Contributor role](https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles) to the App.

This is frankly, very broad credentials.

```bash
az role assignment create \
--assignee ${AZURE_CLIENT_ID} \
--role Contributor \
 --scope /subscriptions/${AZURE_SUBSCRIPTION_ID}/resourceGroups/${AZURE_RESOURCE_GROUP_NAME}
 ```

6. Create Secrets in GitHub with the following names and values

  | Secret Name | Value |
  | ----------- | ----- |
  | AZURE_CLIENT_ID | ${AZURE_CLIENT_ID} |
  | AZURE_TENANT_ID | ${AZURE_TENANT_ID} |
  | AZURE_SUBSCRIPTION_ID | ${AZURE_SUBSCRIPTION_ID} |


7. Create Environment variables with the following names and values

  | Variable Name | Value |
  |---------------|-------|
  | AZURE_RESOURCE_GROUP_NAME | cogniq-community-main |
