![copilot](./img/copilot.png)
# Microsoft Copilot Studio
## Lab 03 - Consuming an Custom MCP Server

In this lab, you are going to understand how to extend an agent made with Microsoft Copilot Studio using an MCP (Model Context Protocol) server. Specifically, you are going to consume an existing HR MCP server that provides tools for managing a hypothetical list of candidates for a job role. The MCP server will offer functionalities to:

- List all candidates
- Search for candidates by criteria
- Add new candidates
- Update existing candidate information
- Remove candidates

### In this lab you will learn:

- How to configure and connect to an existing MCP server
- How to consume MCP tools and resources from an external server
- How to integrate MCP servers with Copilot Studio agents

### Step 1 : Setting up the MCP Server
The HR MCP server that you will be consuming in this lab provides the following tools:

- list_candidates: Provides the whole list of candidates
- search_candidates: Searches for candidates by name, email, skills, or current role
- add_candidate: Adds a new candidate to the list
- update_candidate: Updates an existing candidate by email
- remove_candidate: Removes a candidate by email

The server manages candidates information including:

Personal details (firstname, lastname, full name, email)
Professional information (spoken languages, skills, current role)

*** 
If you don't want to set up your own MCP server, you can use the provided mock server for testing purposes. and go to Step 2. <br/>
https://hr-mcp-ci.ambitiousbush-7fa2fef0.eastasia.azurecontainerapps.io/mcp

*** 
#### Deploy the MCP Server to Azure Container App
1. Clone the git 
# 部署到 Azure Container Apps（使用 azd）

以下说明将引导你使用 Azure Developer CLI (`azd`) 将本项目部署到 Azure Container Apps（ACA）。我们在仓库中添加了 `azure.yaml`（项目清单）和 `infra/main.bicep`（Bicep 模板）以支持 `azd up`。

前提条件：

- 已安装并登录 Azure CLI（`az login`）。
- 已安装 Azure Developer CLI（`azd`）。参考文档安装：https://aka.ms/azure-dev/azd
- 已安装 Docker（用于在本地构建镜像并将其推送到 Azure Container Registry）。

部署步骤（最小流程）：

1. 在本地登录 Azure：

```bash
az login
```

2. 在项目根目录运行 azd：

```bash
azd up
```

运行 `azd up` 时，命令行工具会提示你选择订阅、指定环境名（例如 `dev`）和区域。`azd` 会完成以下操作：

- 创建或复用 Azure 资源组与所需资源（包括 Log Analytics、用户分配的托管标识、Azure Container Registry、Container Apps 环境等），这些资源由 `infra/main.bicep` 定义；
- 使用仓库中的 `Dockerfile` 构建镜像并将其推送到 ACR；
- 在 Container Apps 环境中创建并部署 Container App（服务名为 `hr-mcp-api`）。

3. 部署完成后，你可以获取容器应用的 FQDN（外网访问地址）：

```bash
# 假设你知道资源组名和容器应用名，示例：
az containerapp show --name az-hrm-ca-<token> --resource-group rg-<env> --query properties.configuration.ingress.fqdn -o tsv
```

注：`azd up` 在运行过程中会输出创建的资源名和访问地址，按终端提示操作即可。

清理资源：

- 你可以使用 `azd down` 来删除由 `azd up` 创建的资源：

```bash
azd down
```

- 或者直接使用 `az group delete -n <resource-group-name>`（注意：这将删除资源组及其中所有资源，请谨慎使用）。

常见问题与提示：

- 若本地 Docker 无法访问或构建失败，可先手动构建镜像并推送到一个可访问的镜像仓库（例如 Docker Hub 或 ACR），再在 Bicep/部署流程中引用该镜像；
- 若希望在 CI/CD 中运行 `azd up`，建议在 CI runner 中安装 `azd` 并配置好服务主体凭据（通过 `az login --service-principal`）或使用 GitHub Actions 的 Azure 登录步骤；
- 本仓库已经提供 `Dockerfile`，`azd up` 会默认使用它来构建镜像。确保 `Dockerfile` 能在无交互模式下完成镜像构建。


需要我为你：

- 自动创建一个简单的 GitHub Actions Workflow（在 push 时运行 `azd up` 或自动部署到 Azure Container Apps），或
- 生成一个更严格的 `infra` Bicep 模块化结构（将资源拆分成多个文件），

请告诉我要生成哪一种，我可以继续为你实现。