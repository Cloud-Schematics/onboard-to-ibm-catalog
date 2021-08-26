# Onboard Terraform templates into IBM Cloud private catalog

IBM Cloud team is adminstering your contribution of Terraform template in the [IBM Cloud public repositories](https://github.com/Cloud-Schematics) for IBM Cloud Schematics. For an high reusability and ease of IBM Cloud Terraform development for provisioning the resources or services in IBM Cloud.  Your Terraform templates are onboard into IBM Cloud private catalog and made available for an user through IBM Cloud catalog management.

## IBM Cloud Schematics action

IBM Cloud Schematics action allows you to build, update, scale, and remove multi-tier apps and app runtime environments by using Ansible playbooks. You can also use Ansible to set up continuous deployment pipelines for your apps or automate cloud resource operations. For more information, about Schematics action, see [Getting Started with configuration management](https://cloud.ibm.com/docs/schematics?topic=schematics-getting-started-ansible).

## About playbook

The playbook executes the python script to perform bulk onboard of Terraform templates that are existing in [Cloud-Schematics](https://github.com/Cloud-Schematics) public repository into IBM Cloud private catalog for the IBM Cloud user. This onboard leads to higher visibility of your templates in the form of products for IBM Cloud users to explore and enhance your templates and their provisioning. This saves development time to provision the resources.

## Prerequisites

Before you begin, make sure that you are assigned the following permissions
- To create a [private catalog](https://cloud.ibm.com/docs/account?topic=account-account-services#catalog-management-account-management) in IBM Cloud.
- To create an [create an IBM Cloud Schematics action](https://cloud.ibm.com/docs/schematics?topic=schematics-access).

## Running the playbook in Schematics by using the UI

1. Open the [Schematics action configuration page](https://cloud.ibm.com/schematics/actions/create?name=bulk-onboard-to-private-catalog1&url=https://github.ibm.com/Tanya-Shanker/catalog-automation/tree/integrated-extend).
2. Review the name for your action, and the resource group and region where you want to create the action. Then, click **Create**.
3. Select the `main.yaml` playbook that you want to run.
4. Select the **Verbosity** level to control the depth of information that will be shown when you run the playbook in Schematics.
5. Required: Expand the **Advanced options** to enter all the required input variables in key-value pairs as shown in the table, and in the screen capture.

    | Key | Value|
    | --- | --- |
    | GIT_BASE_URL | `Enter the base URL. For example, https://github.com/Cloud-Schematics` |
    | GITHUB_TOKEN | `Enter your Git repository private access token details` |
    | CATALOG_NAME | `Enter the catalog name. For example, bulkonboard_cloudschematicsrep` |
    | CATALOG_MANAGEMENT_APIKEY | `Enter your IBM Cloud API key` |
    
6. Click **Save**.   
7. Click **Check action** to verify your action details. The **Jobs** page opens automatically. You can view the results of this check by looking at the logs.
8. Click **Run action** to perform the onboarding on all the Terraform templates into IBM Cloud private catalog. You can monitor the progress of this action by reviewing the logs on the **Jobs** page.

## Verification

1. Open the [IBM Cloud catalog management](https://cloud.ibm.com/content-mgmt/catalogs).
2. Click your catalog name link to view the list of product offerings in the private catalog.

## Reference

Review the following links to find more information about IBM Cloud Schematics action and IBM Cloud catalog management:

- [IBM Cloud Schematics action documentation](https://cloud.ibm.com/docs/schematics)
- [IBM Cloud catalog management](https://cloud.ibm.com/docs/account?topic=account-accountfaqs)

## Getting help

For help and support with using this template in IBM Cloud Schematics, see [Getting help and support](https://cloud.ibm.com/docs/schematics?topic=schematics-schematics-help).

