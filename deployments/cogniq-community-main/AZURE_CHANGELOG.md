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

4. At this point, you may wish to save your credentials to a .envrc file for later use.

```bash
# cogniq-community-main
export AZURE_SUBSCRIPTION_ID=REDACTED
export AZURE_RESOURCE_GROUP_NAME=cogniq-community-main
export AZURE_CLIENT_ID=REDACTED
export AZURE_APPLICATION_OBJECT_ID=REDACTED
export AZURE_TENANT_ID=REDACTED
export AZURE_ASSIGNEE_OBJECT_ID=REDACTED
export AZURE_ROLE_ASSIGNMENT_OBJECT_ID="/subscriptions/REDACTED/resourceGroups/cogniq-community-main/providers/Microsoft.Authorization/roleAssignments/REDACTED"

```

5. Run the following command to create a new [federated identity credential](https://learn.microsoft.com/en-us/graph/api/application-post-federatedidentitycredentials?) for deploying the active directory application for the cogniq-community-main environment.

```bash
cat > credential.json
{
    "name": "cogniq-gha-environment-cogniq-community-main",
    "issuer": "https://token.actions.githubusercontent.com",
    "subject": "repo:CogniQ/CogniQ:environment:cogniq-community-main",
    "description": "cogniq-gha-environment-cogniq-community-main",
    "audiences": [
        "api://AzureADTokenExchange"
    ]
}

az ad app federated-credential create --id ${AZURE_APPLICATION_OBJECT_ID} --parameters credential.json
```

6. Grant Azure Container Instances access

Grant [Contributor role](https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles) to the App.

This is frankly, very broad credentials.

```bash
az role assignment create \
--assignee ${AZURE_CLIENT_ID} \
--role Contributor \
 --scope /subscriptions/${AZURE_SUBSCRIPTION_ID}/resourceGroups/${AZURE_RESOURCE_GROUP_NAME}
 ```

7. Create Secrets in GitHub with the following names and values

  | Secret Name | Value |
  | ----------- | ----- |
  | AZURE_CLIENT_ID | ${AZURE_CLIENT_ID} |
  | AZURE_TENANT_ID | ${AZURE_TENANT_ID} |
  | AZURE_SUBSCRIPTION_ID | ${AZURE_SUBSCRIPTION_ID} |


8. Register for the provider

```bash
az provider register --namespace Microsoft.ContainerInstance
```

## 20230617 - Add PostgreSQL instance.

1. Create the vnet for the database

```bash
az network vnet create --resource-group ${AZURE_RESOURCE_GROUP_NAME} --name cogniq --location eastus --address-prefixes 10.0.0.0/16

az network vnet subnet create --resource-group ${AZURE_RESOURCE_GROUP_NAME} --vnet-name cogniq --address-prefixes 10.0.0.0/24 --name cogniq-db

az network vnet subnet create --resource-group ${AZURE_RESOURCE_GROUP_NAME} --vnet-name cogniq --address-prefixes 10.0.1.0/24 --name cogniq-web

```


2. Create the PostgreSQL instance

```bash
az postgres flexible-server create \
  --name cogniq-db \
  --resource-group ${AZURE_RESOURCE_GROUP_NAME} \
  --vnet cogniq \
  --subnet cogniq-db \
  --database-name cogniq \
  --location "eastus" \
  --storage-size 32 \
  --tier Burstable \
  --sku-name Standard_B1ms

```


3. Create the web app

```bash

az appservice plan create \
  --resource-group ${AZURE_RESOURCE_GROUP_NAME} \
  --name cogniq-web \
  --location eastus \
  --is-linux \
  --number-of-workers 1 \
  --sku B1


az webapp create \
  --resource-group ${AZURE_RESOURCE_GROUP_NAME} \
  --plan cogniq-web \
  --name cogniq-web \
  --deployment-container-image-name ghcr.io/cogniq/cogniq:main \
  --https-only \
  --public-network-access Enabled \
  --vnet cogniq \
  --subnet cogniq-web \
  --role Reader

az webapp config appsettings set --resource-group ${AZURE_RESOURCE_GROUP_NAME} --name cogniq-web --settings '@deployments/cogniq-community-main/app-settings.json'

az webapp vnet-integration add --resource-group ${AZURE_RESOURCE_GROUP_NAME} -n  cogniq-web --vnet cogniq --subnet cogniq-web

az webapp log config \
  --name cogniq-web \
  --resource-group ${AZURE_RESOURCE_GROUP_NAME} \
  --docker-container-logging filesystem

az webapp log tail --name cogniq-web --resource-group ${AZURE_RESOURCE_GROUP_NAME}

```