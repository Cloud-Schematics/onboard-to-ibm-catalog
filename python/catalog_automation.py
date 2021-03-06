#!/usr/bin/python3
from ibm_platform_services.catalog_management_v1 import *
import ibm_cloud_sdk_core
from github import Github
import os
import github
import re
import sys
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

WhiteListExtn = (".tf")
AllowedType   = {"terraform"}
ReadmeFiles   = {"README.md", "README.MD", "Readme.MD", "Readme.md", "readme.md", "readme.MD"}
BlackListExtn = (".php5,.pht,.phtml,.shtml,.asa,.cer,.asax,.swf,.xap,.tfstate,.tfstate.backup")
BlackListedRepo = {'arch-multizone-vpc-vsi-lb', 'catalog-templates','cluster-with-logging-monitoring-addons',
'multitier-vpc','multitier-vpc-example','multitier-vpc-with-transit-gateway','multizone-secure-iks-with-cis',
'multizone-vpc','multizone-vpc-gen2','openshift-cluster-on-classic','openshift-hub-and-spoke-vpc-arch',
'openshift-on-vpc-no-public-endpoint-bastion-vsi-architecture','openshift-on-vpc-private-service-endpoint',
'roks-on-vpc','vmc-cluster-edge-pool','vsi-operations-scheduler-solution'}

def GetRepoContent(client, path) :
    contents = []
    try :
     contents = client.get_contents(path=path)
    except github.GithubException as err:
        print(err)
        return contents, err
    return contents, ''

def GetCatalogService() :
    return CatalogManagementV1.new_instance()

def IsDir(contentType) :
    if contentType == "dir":
        return True
    return False

def HasBlacklistedExtensions(name) :
    if name.lower().endswith(BlackListExtn) :
        return True
    return False

def HasAllowedExtension(name) :
    if name.lower().endswith(WhiteListExtn) :
        return True
    return False

def IsValidType(name) :
    if name.lower() in AllowedType :
        return True
    return False
    
def IsReadmePresent(name) :
    if name in ReadmeFiles :
        return True
    return False

def GetOrgName(url) :
    urlSplit = re.findall('([\w\-\.]+)', url)
    protocol = urlSplit[0]
    hostname = urlSplit[1]
    org = urlSplit[2]
    print(protocol)
    print(hostname)
    print(org)
    return org

def GetRepoUrl(url) :
    repoUrl = url[:url.rindex("/")]
    return repoUrl

def FetchRepositories(client, orgName) :
    try :
        org = client.get_organization(orgName)
        org.login
        repos = org.get_repos(type='public')
        print("No of repo fetched : ", repos.totalCount)
    except github.GithubException as err :
        print(err)
        return [] 

    list = []
    validRepos = []
    for r in repos :
        dir = {}
        dir["name"] = r.name
        dir["description"] = r.description
       
        if not dir['description'] :
            dir['description'] = r.name

        list.append(dir)

    for repo in list :
        try : 
            gitRepo = org.get_repo(repo["name"])
        except github.GithubException as err:
            print(err)
            continue
        
        print("--------------Validating Repo : ", repo["name"], " for Vulnerability checks, Mandatory Files and Valid Release------------")
        if repo['name'] in BlackListedRepo:
            print("Skipping repo : ", repo["name"])
            continue

        response, err = ValidateRepoContent(gitRepo, "")
        if err != '' :
            print("Skipping repo : ", repo["name"], ". Error occured : ", err)
            continue 

        invalid, type = CheckErrorExists(response=response)
        if invalid :
            print("Skipping repo : ", repo["name"], "due to ", type)
            continue
        if not ValidateMandatoryFiles(gitRepo):
            print("Skipping repo : ", repo["name"], " since mandatory file missing")
            continue
        doc_url = GetReadmeURL(gitRepo)

        tagName, url, err = ValidateRelease(gitRepo)
        if err != '' or not(url):
            print("Skipping repo : ", repo["name"], " since valid release is missing")
            continue
        repo["repo_url"] = GetRepoUrl(url)
        repo["asset_url"] = url
        repo["docs_url"] = doc_url
        repo["release_tag"] = tagName
        validRepos.append(repo)
       
    print("Validated repo : ", len(validRepos))
    return validRepos


def ValidateRepoContent(client, path):
    response = {
        "BlacklistedExtn" : False,
        "WhitelistedExtn" : False
    }

    dir, err = GetRepoContent(client, path)
    if err != '' :
        return response, err
        
    while dir  :
        content = dir.pop(0)
        if not(IsDir(content.type)):
            if HasBlacklistedExtensions(content.name):
                response["BlacklistedExtn"] = True
            elif HasAllowedExtension(content.name):
                response["WhitelistedExtn"] = True
        elif response["BlacklistedExtn"] == True or response["WhitelistedExtn"] == True:
            break
        elif IsDir(content.type) :
            response, err = ValidateRepoContent(client, content.path)   
    return response, err


def ValidateRelease(client) :
    assetUrl, tagName = '', ''
    assets = []
    try :
        assets = client.get_latest_release().get_assets()
        tagName = client.get_latest_release().tag_name

    except github.GithubException as err:
        print(err)
        return tagName, assetUrl, err
    
    for asset in assets :
        print("------------- asset :", asset.browser_download_url)
        if asset.browser_download_url.lower().endswith(".tgz") :
            assetUrl = asset.browser_download_url
            break

    return tagName, assetUrl, ''


def ValidateMandatoryFiles(client) :
    valid = False
    dir, err = GetRepoContent(client,"")
    if err != '' :
        return valid

    for content in dir :
        if not(IsDir(content.type)) and IsReadmePresent(content.name):
            valid = True
    
    return valid

def GetReadmeURL(client):
    readme = []
    try :
        readme = client.get_readme()

    except github.GithubException as err:
        print(err)
        return ''

    return readme.html_url

def GetCatalog(service,iam_token) :
    response = []
    # kwargs = {
    #     'headers' : {
    #         'Authorization' : 'Bearer ' + iam_token
    #         }
    # }

    try: 
        response = service.list_catalogs()
        #kwargs=kwargs
    except ibm_cloud_sdk_core.ApiException as err:
        print(err)
        return response, err

    return response, ''

def DeleteOffering(service, catalogID, offeringID) :
    try:
        service.delete_offering(catalog_identifier=catalogID, offering_id=offeringID)
    except ibm_cloud_sdk_core.ApiException as err:
        print(err)
        return err
    return ''

def ListOffering(service,catalogID) :
    response = []
    try:
        response = service.list_offerings(catalog_identifier=catalogID)
    except ibm_cloud_sdk_core.ApiException as err:
        print(err)
        return response, err
    return response, ''

def CreateCatalog(catalogName,service,iam_token) :
    label = catalogName
    shortDesc = "Catalog to bulk onboard all the templates"

    response, err = GetCatalog(service,iam_token)
    if err != '' :
        print("Error occured while getting the catalog: ", err)
        return ''

    resources = response.result['resources']

    catalogExists = 'false'
    catalogID = ''
    for resource in resources:
        if (label == resource['label']):
            catalogExists = 'true'
            catalogID=resource['id']
            break
    if (catalogExists == 'false'):
        try:
            print("Creating a catalog")
            response = service.create_catalog(label=label, short_description=shortDesc)
        except ibm_cloud_sdk_core.ApiException as err:
            print("Error occurred while creating a catalog :", err)
        else:
            catalogID = response.result['id']
    else:
        print("Catalog already exists with given label, updating the offerings in the catalog") 
    
    return catalogID

def OfferingManagement(repoList, service, catalogID):
    offeringResponse = {}
    response, err = ListOffering(service,catalogID)
    if err != '' :
        print("Error occurred while getting a list of offerings :", err)
        return
    
    offeringCount = response.result['total_count']
    print(offeringCount)
    resources = response.result['resources']
    deleted = CheckRepoExists(repoList,resources)
    offeringResponse["deleted"] = deleted
    
    for repo in repoList :
        offeringResponse["keywords"] = []
        for resource in resources:
            if (repo['name'] == resource['label']):
                offeringResponse['offeringStatus'] = 'update'
                offeringResponse['offeringID']=resource['id']
                kind = resource['kinds'][0]
                offeringResponse['existingVersions'] = kind['versions']
                if len(resource['keywords']) !=0 :
                    offeringResponse["keywords"] = resource['keywords']
                break
        else :
                offeringResponse['offeringStatus'] = 'create'  
        if len(offeringResponse["keywords"])!=0 and CheckReleaseExists(repo["release_tag"], offeringResponse["keywords"]) :
            print("---------- Skipping this version due to same release tag ---------------")
            continue
        OfferingOperations(service, catalogID,repo, offeringResponse)

def OfferingOperations(service,catalogID, repo, offeringResponse) :  
    name = repo['name']
    tgzURL = repo['asset_url']
    tagName = repo["release_tag"]
    offeringID = ''
    newVersion = '1.0.0'
    keywords = []
    
    tags = ['dev_ops']
    repoInfo = {}
    repoInfo['type'] = "public_git"
    offering_icon_url ="https://globalcatalog.cloud.ibm.com/api/v1/1082e7d2-5e2f-0a11-a3bc-f88a8e1931fc/artifacts/terraform.svg"
    offering_docs_url = repo['docs_url']
    short_description = repo['description']
    if len(offeringResponse["deleted"]) != 0 :
        for offering in offeringResponse["deleted"] :
            print("-------------- Removing offering of deleted repository ---------------")
            err = DeleteOffering(service,catalogID, offering['id'])
            if err != '' :
                print("Error occurred while deleting offering : ", err)
    
    config = []
    configItem = {}
    config.append(configItem)

    if offeringResponse["offeringStatus"] == 'create' :
        print("creating new offering")
        targetKinds = ["terraform"]

        keywords.append(tagName)

        try :
            response = service.import_offering(catalog_identifier=catalogID, target_kinds=targetKinds, tags=tags,  zipurl=tgzURL, target_version=newVersion, repo_type="public_git", include_config=True)
        except ibm_cloud_sdk_core.ApiException as err:
            print("Skipping this repo as error occurred while creating new offering :",err)
            return
        
        offeringID = response.result['id']
        rev = response.result['_rev']
        kinds = response.result['kinds']


    elif offeringResponse["offeringStatus"] == 'update':
        targetVer = CreateVersion(offeringResponse['existingVersions'])
        keywords = offeringResponse["keywords"]
        offeringID = offeringResponse["offeringID"]
        
        keywords.append(tagName)
        try:
            response = service.import_offering_version(catalog_identifier=catalogID, offering_id=offeringID, zipurl=tgzURL, target_version=targetVer, repo_type="public_git", tags=tags, include_config=True)
        except ibm_cloud_sdk_core.ApiException as err:
            print("Skipping this repo as error occurred while creating new offering version:",err)
            return
        rev = response.result['_rev']
        kinds = response.result['kinds']

    try :
        service.replace_offering(catalog_identifier=catalogID, offering_id=offeringID,keywords=keywords,id=offeringID, rev=rev, name=name, label=name, kinds=kinds, repo_info=repoInfo, tags=tags, offering_icon_url=offering_icon_url, offering_docs_url=offering_docs_url,short_description=short_description)
    except ibm_cloud_sdk_core.ApiException as err:
        print("Skipping this repo as error occurred while updating offering:",err)
    print(offeringID)

def CheckReleaseExists(releaseTag, keywords) :
    if releaseTag in keywords :
        return True
    return False

def CheckRepoExists(repoList, offeringList) :
    deleted = []
    list = []
    for repo in repoList :
        list.append(repo["name"])

    for offering in offeringList :
        if offering['label'] not in list: 
            deleted.append(offering)
    return deleted

def CheckErrorExists(response) :
    exists = False
    type = ''
    if response["BlacklistedExtn"] :
        exists = True
        type = "Vulnerable files"
    elif not (response["WhitelistedExtn"]):
        exists = True
        type = "Missing required files"
    return exists, type

def CreateVersion(existingVersions) :
    versionList = []
    done = False
    v1,v2,v3 = 1,0,0
    for oldVersion in existingVersions :
        versionList.append(oldVersion['version'])
    version = str(v1)+'.'+str(v2)+'.'+str(v3)
    while ~done  :
        if version in versionList :
            v3 = v3 +1
            if v3 >= 10 :
                v3 = 0
                v2 = v2 + 1
            if v2 >= 10 :
                v2 = 0
                v1 = v1+1
            version = str(v1)+'.'+str(v2)+'.'+str(v3)
        else :
            break
    return version

def main() :
     # reading access token from env variable
    base_url = sys.argv[1]
    token = sys.argv[2]
    catalogName = sys.argv[4]
    os.environ["CATALOG_MANAGEMENT_APIKEY"] = sys.argv[3]
    os.environ["CATALOG_MANAGEMENT_AUTH_TYPE"] = 'iam'

    g = Github(login_or_token=token)
    org = GetOrgName(base_url)

    if "ibm" in base_url :
        g = Github(base_url="https://github.ibm.com/api/v3", login_or_token=token)
    else :
        g = Github(login_or_token=token)

    validRepoList = FetchRepositories(g, org)
    service = GetCatalogService()
    catalogID = CreateCatalog(catalogName,service,"")
    OfferingManagement(validRepoList,service,catalogID)
main()
