# Onboard Terraform templates into IBM Cloud private catalog

For an high reusability and ease of IBM Cloud Terraform development for provisioning the resources or services in IBM Cloud.  The Terraform templates from [IBM Cloud Cloud-Schematics repository](https://github.com/Cloud-Schematics) can be onboard into private catalogs and made available for an user through IBM Cloud catalog management.

## IBM Cloud Schematics action

IBM Cloud Schematics action allows you to build, update, scale, and remove multi-tier apps and app runtime environments by using Ansible playbooks. You can also use Ansible to set up continuous deployment pipelines for your apps or automate cloud resource operations. For more information, about Schematics action, see [Getting Started with configuration management](https://cloud.ibm.com/docs/schematics?topic=schematics-getting-started-ansible).

## About playbook

The playbook executes the python script to perform bulk onboard of Terraform templates that are existing in [Cloud-Schematics](https://github.com/Cloud-Schematics) public repository into IBM Cloud private catalog for the IBM Cloud user. This onboard leads to higher visibility of your templates in the form of products for IBM Cloud users to explore and enhance your templates and their provisioning. This saves development time to provision the resources.

## Prerequisites

Before you begin, make sure that you are assigned the following permissions
- To create a [private catalog](https://cloud.ibm.com/docs/account?topic=account-account-services#catalog-management-account-management) in IBM Cloud.
- To create an [create an IBM Cloud Schematics action](https://cloud.ibm.com/docs/schematics?topic=schematics-access).

**Note**
The templates that contains complex variables such as list, map, tuple, object input variables are not supported in private catalogs. The workaround is you need to adjust the template to takes simple string type.

## Running the playbook in Schematics by using the UI

1. Open the [Schematics action configuration page](https://cloud.ibm.com/schematics/actions/create?name=ansible-is-instance-actions&url=https://github.com/Cloud-Schematics/onboard-to-ibm-catalog).
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

    **Example of the screen capture**
    ![List of the onboarded Terraform template in private catalog](images/private_catalog_list.png)
3. You can further click the required offerings, accept the license, and click **Install** to create the workspace. **Note** Ensure you provide all the required input variables as per the readme file of the offering in the **Settings** page to provision the resources through Schematics workspace.

## Reference

Review the following links to find more information about IBM Cloud Schematics action and IBM Cloud catalog management:

- [IBM Cloud Schematics action documentation](https://cloud.ibm.com/docs/schematics)
- [IBM Cloud catalog management](https://cloud.ibm.com/docs/account?topic=account-accountfaqs)

## Getting help

For help and support with using this template in IBM Cloud Schematics, see [Getting help and support](https://cloud.ibm.com/docs/schematics?topic=schematics-schematics-help).

