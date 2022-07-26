import requests
import json
import time
import sys
from github import Github, GithubIntegration




def get_access(repo):
    with open("aeg-sca.2022-05-06.private-key.pem", "r") as secret:
        private_key = secret.read()
    #print(private_key)
    GITHUB_APP_ID = "25"
    integration = GithubIntegration(
        GITHUB_APP_ID, private_key, base_url="https://ghe.tusimple.io/api/v3")
    install = integration.get_installation("TuSimple", repo)
    access = integration.get_access_token(install.id)
    return access.token

def get_head_sha(repo):
    ghe_token = "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"
    user = "guoqing.zhang"
    url = "https://ghe.tusimple.io/api/v3/repos/TuSimple/{}/pulls".format(repo)
    re = requests.get(url=url,auth=(user,ghe_token))
    #print(re.status_code)
    state=json.loads(re.text)[0]
    ref = state['head']["ref"]
    sha = state['head']["sha"]
    #print(state)
    return ref,sha



def check_run(repo,head_sha,time):
    token=get_access(repo)
    data = {
        "name":"SCA","head_sha":head_sha,"status":"in_progress",
        "external_id":"42","started_at":time,"output":{"title":"Parasoft","summary":"","text":""}
        }
    header = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": "token {}".format(token)
    }
    url = "https://ghe.tusimple.io/api/v3/repos/TuSimple/{}/check-runs".format(repo)
    re = requests.post(url=url,headers=header,data=json.dumps(data))
    print(re.status_code)
    run_id = (json.loads(re.content))['id']
    #print(re.content)
    #print(run_id)
    if int(re.status_code) == 201:
        print("check run success")
        print("The check run on repo: {}".format(repo))
        print("The check run id is {}".format(run_id))
    else:
        print(re.content)
        print('can not run a check.')
        exit(-1)
    return run_id


def check_updata(repo,head_sha,time_s,run_id):
    token=get_access(repo)
    time_end = time.strftime("%Y-%m-%d{}%H:%M:%S{}",time.localtime()).format("T","Z")
    data = {"name":"SCA","head_sha":head_sha,
            "started_at":time_s,"status":"completed",
            "conclusion":"success","completed_at":time_end,
            "output":{"title":"Parasoft",
                    "summary":"There are 0 failures, 2 warnings, and 1 notices.",
                    "text":"You may have some misspelled words on lines 2 and 4. You also may want to add a section in your README about how to install your app.",
                    "annotations":[{"path":"README.md","annotation_level":"warning","title":"Spell Checker",
                    "message":"Check your spelling for 'banaas'.","raw_details":"Do you mean 'bananas' or 'banana'?",
                    "start_line":2,"end_line":2},
                    {"path":"README.md","annotation_level":"warning",
                    "title":"Spell Checker","message":"Check your spelling for 'aples'",
                    "raw_details":"Do you mean 'apples' or 'Naples'","start_line":4,"end_line":4}],
                    "images":[{"alt":"Super bananas","image_url":"http://example.com/images/42"}]
                }
        }
    header = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": "token {}".format(token)
    }
    url = "https://ghe.tusimple.io/api/v3/repos/TuSimple/{}/check-runs/{}".format(repo,run_id)
    re = requests.patch(url=url,headers=header,data=json.dumps(data))
    print(re.status_code)



if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("must input test repo name")
        exit(1)
    else:
        repo = sys.argv[1]

    ref,head_sha= get_head_sha(repo)
    #print(head_sha,ref)
    time_start = time.strftime("%Y-%m-%d{}%H:%M:%S{}",time.localtime()).format("T","Z")
    run_id = check_run(repo,head_sha,time_start)
    #print("The check run id is {}".format(run_id))
    output = {
        "ref":ref,
        "head_sha":head_sha,
        "time_start":time_start,
        "run_id":run_id
    }
    json.dump(output,open('configuration.json','w'),indent=4)
