from github import Github
import os
import github
import re

from requests.models import Response

WhiteListExtn = (".tf")
AllowedType   = {"terraform", "ansible"}
ReadmeFiles   = {"README.md", "README.MD", "Readme.MD", "Readme.md", "readme.md", "readme.MD"}
BlackListExtn = (".php5,.pht,.phtml,.shtml,.asa,.cer,.asax,.swf,.xap,.tfstate,.tfstate.backup")

def main() :
    # reading access token from env variable
    base_url = os.getenv('BASE_URL')
    token = os.getenv('GITHUB_TOKEN', '...')

    g = Github(login_or_token=token)
    
    org = GetOrgName(base_url)
    
    validRepoList = FetchRepositories(g, org)

    for repo in validRepoList :
        print("Git Name : ", repo["name"])
        print("Git url : ", repo["git_url"])
    return validRepoList

def FetchRepositories(client, orgName) :
    try :
        org = client.get_organization(orgName)
        org.login
        repos = org.get_repos()
        print("No of repo fetched : ", repos.totalCount)
    except github.GithubException as err :
        print(err)
        return [] 


    list = []
    validRepos = []
    for r in repos :
        dir = {}
        dir["name"] = r.name
        dir["git_url"] = r.git_url
        list.append(dir)

    for repo in list :
        try : 
            gitRepo = org.get_repo(repo["name"])

        except github.GithubException as err:
            print(err)
            continue

        print("--------------Validating Repo : ", repo["name"], " for Vulnerability checks, Mandatory Files and Valid Release------------")
        response, err = ValidateRepoContent(gitRepo, "")
        if err != '' :
            print("Skipping repo : ", repo["name"], ". Error occured : ", err)
            continue 

        if CheckErrorExists(response=response) :
            print("Skipping repo : ", repo["name"])
            continue
        if not(ValidateMandatoryFiles(gitRepo)) :
            print("Skipping repo : ", repo["name"], " since mandatory file missing")
            continue
        valid, url, err = ValidateRelease(gitRepo)
        if err != '' or not(valid):
            print("Skipping repo : ", repo["name"], " since valid release is missing")
            continue

        repo["asset_url"] = url
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
                break
            elif HasAllowedExtension(content.name):
                response["WhitelistedExtn"] = True
        elif IsDir(content.type) & IsValidType(content.name) :
            response, err = ValidateRepoContent(client, content.path)   
    return response, err


def GetRepoContent(client, path) :
    contents = []
    try :
     contents = client.get_contents(path=path)
    except github.GithubException as err:
        print(err)
        return contents, err
    return contents, ''


def ValidateRelease(client) :
    validRelease = False
    assetUrl = ''
    assets = []
    try :
        assets = client.get_latest_release().get_assets()
    except github.GithubException as err:
        print(err)
        return validRelease, assetUrl, err
    
    for asset in assets :
        print("------------- asset :", asset.browser_download_url)
        if asset.browser_download_url.lower().endswith(".tgz") :
            assetUrl = asset.browser_download_url
            validRelease = True
            break
    return validRelease, assetUrl, ''


def ValidateMandatoryFiles(client) :
    valid = False
    
    dir, err = GetRepoContent(client,"")
    if err != '' :
        return valid

    for content in dir :
        if not(IsDir(content.type)) & IsReadmePresent(content.name):
            valid = True
    
    return valid


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

def CheckErrorExists(response) :
    exists = False
    if response["BlacklistedExtn"] :
        exists = True
    elif not (response["WhitelistedExtn"]):
        exists = True
    return exists
    
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

main()
