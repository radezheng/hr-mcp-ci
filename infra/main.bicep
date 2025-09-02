targetScope = 'resourceGroup'

param environmentName string = 'dev'

param location string = resourceGroup().location

var resourcePrefix = 'hrm'
var resourceToken = uniqueString(subscription().id, resourceGroup().id, location, environmentName)

// Container Registry name must be lowercase and alphanumeric
var acrNameRaw = 'az-${resourcePrefix}-${resourceToken}-acr'
var acrName = toLower(replace(acrNameRaw, '-', ''))

// Log Analytics Workspace
resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2021-06-01' = {
  name: 'az-${resourcePrefix}-law-${resourceToken}'
  location: location
  properties: {}
  tags: {
    azd: 'true'
  }
}

// Key Vault (minimal configuration)
resource keyVault 'Microsoft.KeyVault/vaults@2021-06-01-preview' = {
  name: 'az-${resourcePrefix}-kv-${resourceToken}'
  location: location
  properties: {
    tenantId: subscription().tenantId
    sku: {
      family: 'A'
      name: 'standard'
    }
    accessPolicies: []
    enableSoftDelete: true
  }
  tags: {
    azd: 'true'
  }
}

// Azure Container Registry (启用管理员用户以简化初始部署的凭据配置)
resource acr 'Microsoft.ContainerRegistry/registries@2021-09-01' = {
  name: acrName
  location: location
  sku: {
    name: 'Standard'
  }
  properties: {
    adminUserEnabled: true
  }
  tags: {
    azd: 'true'
  }
}

// Container Apps Environment (managed environment) with Log Analytics attached
resource containerEnv 'Microsoft.App/managedEnvironments@2022-03-01' = {
  name: 'az-${resourcePrefix}-cae-${resourceToken}'
  location: location
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logAnalytics.properties.customerId
        sharedKey: listKeys(logAnalytics.id, '2020-08-01').primarySharedKey
      }
    }
  }
  tags: {
    azd: 'true'
  }
}

// Container App deployed into the managed environment
resource containerApp 'Microsoft.App/containerApps@2022-03-01' = {
  name: 'az-${resourcePrefix}-ca-${resourceToken}'
  location: location
  properties: {
    managedEnvironmentId: containerEnv.id
    configuration: {
      ingress: {
        external: true
        targetPort: 8000
        transport: 'Auto'
      }
      registries: [
        {
          server: '${acr.name}.azurecr.io'
          username: listCredentials(acr.id, '2019-05-01').username
          passwordSecretRef: 'acr-password'
        }
      ]
      secrets: [
        {
          name: 'acr-password'
          value: listCredentials(acr.id, '2019-05-01').passwords[0].value
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'hr-mcp-api'
          image: 'mcr.microsoft.com/azuredocs/containerapps-helloworld:latest'
          resources: {
            cpu: 1
            memory: '2.0Gi'
          }
        }
      ]
      scale: {
        minReplicas: 0
        maxReplicas: 1
      }
    }
  }
  tags: {
    'azd-service-name': 'hr-mcp-api'
  }
}

output RESOURCE_GROUP_ID string = resourceGroup().id
output AZURE_CONTAINER_REGISTRY_ENDPOINT string = '${acr.name}.azurecr.io'
