from ibm_platform_services.catalog_management_v1 import *

def main() :
    catalogID = CreateCatalog()
    CreateOfferings(catalogID)

def GetCatalogService() :
    return CatalogManagementV1.new_instance()

def CreateCatalog() :
    service = GetCatalogService()
    label = "firstcatalog"
    shortDesc = "created from python script"

    response = service.list_catalogs()
    catalogCount = response.result['total_count']
    print(catalogCount)
    resources = response.result['resources']
    catalogExists = 'false'
    catalogID = ''
    for resource in resources:
        if (label == resource['label']):
            catalogExists = 'true'
            catalogID=resource['id']
            break
    if (catalogExists == 'false'):
        response = service.create_catalog(label=label, short_description=shortDesc)
        catalogID = response.result['id']
    else:
        print("Catalog already exists with given label") 
    
    return catalogID

def CreateOfferings(catalogID) :
    service = GetCatalogService()
    print(catalogID)
    id = catalogID
    name = "observability5"
    label = "observability5"
    tgzURL = "https://github.ibm.com/schematics-solution/terraform-ibm-observability/releases/download/v1.0.1/ibm-observability-1.0.1.tgz"

    version = {}
    version['tgz_url'] = tgzURL
    version['version'] = "1.0.4"
    version['repo_url'] = "https://github.ibm.com/schematics-solution/terraform-ibm-observability/releases/download/v1.0.1"

    versions = []
    versions.append(version)

    kind = {}
    kind['format_kind'] = "terraform"
    kind['install_kind'] = "terraform"
    kind['target_kind'] = "terraform"
    kind['versions'] = versions

    kinds = []
    kinds.append(kind)

    repoInfo = {}
    repoInfo['token'] = "655395e49a08c4c0810ef92c08e0a52b13a8b540"
    repoInfo['type'] = "enterprise_git"

    tags = ['dev_ops']


    response = service.list_offerings(catalog_identifier=id)
    offeringCount = response.result['total_count']
    print(offeringCount)
    resources = response.result['resources']
    offeringExists = 'false'
    offeringID = ''
    for resource in resources:
        if (label == resource['label']):
            offeringExists = 'true'
            offeringID=resource['id']
            break
    if (offeringExists == 'false'):
        print("creating new offering")
        version = {}
        version['tgz_url'] = tgzURL
        version['version'] = "1.0.4"
        version['repo_url'] = "https://github.ibm.com/schematics-solution/terraform-ibm-observability/releases/download/v1.0.1"

        versions = []
        versions.append(version)

        kind = {}
        kind['format_kind'] = "terraform"
        kind['install_kind'] = "terraform"
        kind['target_kind'] = "terraform"
        kind['versions'] = versions

        kinds = []
        kinds.append(kind)

        repoInfo = {}
        repoInfo['token'] = "655395e49a08c4c0810ef92c08e0a52b13a8b540"
        repoInfo['type'] = "enterprise_git"
        response = service.create_offering(catalog_identifier=id, name=name, label=label, kinds=kinds, repo_info=repoInfo, tags=tags)
        offeringID = response.result['id']
    else:
        targetVer = "1.0.6"
        response = service.import_offering_version(catalog_identifier=catalogID, offering_id=offeringID, zipurl=tgzURL, target_version=targetVer, repo_type="enterprise_git", tags=tags)

    print(offeringID)

main()