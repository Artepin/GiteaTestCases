import os

import docker
import requests
import base64
import subprocess as sub

def start_gitea():
    command = 'docker-compose up -d'
    os.chdir('/home/andy/gitea')
    os.system(command)
    print()


def stop_gitea():
    command = 'docker-compose down'
    os.chdir('/home/andy/gitea')
    os.system(command)
    print()

def auth():
    username = "user1"
    passwd = "732password"
    headers = {
        # Already added when you pass json=
        # 'Content-Type': 'application/json',
        'accept': 'application/json',
    }

    json_data = {
        'name': 'test222',
    }

    response = requests.post('http://localhost:3000/api/v1/users/user1/tokens', headers=headers, json=json_data, verify=False, auth=(username, passwd))
    print(response)
    if response.status_code ==400:
        response = requests.delete('http://localhost:3000/api/v1/users/user1/tokens/test222', headers=headers, json=json_data, verify=False, auth=(username, passwd))
        response = requests.post('http://localhost:3000/api/v1/users/user1/tokens', headers=headers, json=json_data, verify=False, auth=(username, passwd))
        sha = find_param("sha",response)
        return sha
    if response.status_code ==201:
        sha = find_param("sha", response)
        return sha




def request(req):
    headers = {
        'accept': 'application/json',
        'authorization': 'Basic cm9vdDpyb290',
    }
    response = requests.get("http://localhost:3000"+req,headers=headers)
    return response

def create_user():
    headers = {
        'accept': 'application/json',
        'authorization':'Basic cm9vdDpyb290',
        # Already added when you pass json= but not when you pass data=
        # 'Content-Type': 'application/json',
    }

    json_data = {
        'email': 'user@example.com',
        'full_name': 'user1',
        'login_name': 'user1',
        'must_change_password': True,
        'password': 'password',
        'send_notify': True,
        'source_id': 0,
        'username': 'user1',
        'visibility': 'public',
    }

    response = requests.post('http://localhost:3000/api/v1/admin/users', headers=headers, json=json_data)
    print()


def find_param(param,response):
    response = response.text.split(",")
    for i in response:
        if param in i:
            res = i.split(":")[1]
            result = res.split('"')[1]
            print()
            return result


def user_is_here(user):
    list_of_users = []
    response = request('/api/v1/admin/users')
    content = response.content
    ans = content.decode('UTF-8')
    spis = ans.split('}')
    for i in spis:
        elem = i.split(',')
        for j in elem:
            if "login" in j and "_" not in j:
                login = j.split(':')[1]
                list_of_users.append(login)
    for i in list_of_users:
        if user in i:
            return True
    return False


def encode_import_text(text):
    text = base64.b64encode(bytes(text, "UTF-8")).decode("UTF-8")
    return text

def decode_export_text(text):
    text = base64.b64decode(text).decode("UTF-8")
    return text

def create_repo(name,token):
    headers = {
        'accept': 'application/json',
        'authorization': 'token '+token,
    }

    json_data = {
        'auto_init': True,
        'default_branch': 'master',
        'description': 'test',
        'gitignores': '',
        'issue_labels': '',
        'license': '',
        'name': name,
        'private': False,
        'readme': '',
        'template': True,
        'trust_model': 'default',
    }

    response = requests.post('http://localhost:3000/api/v1/user/repos', headers=headers, json=json_data)
    if (response.reason == 'Conflict'):
        print("Репозиторий с именем " + name + " уже создан")
    else:
        print(response.reason)


def push_file(token):
    str = "test_text_for_me"
    str = encode_import_text(str)
    headers = {
        'accept': 'application/json',
        'authorization': 'token '+token,
        # Already added when you pass json= but not when you pass data=
        'Content-Type': 'application/json',
    }

    json_data = {
        'author': {
            'email': 'artemkozlov68@gmail.com',
            'name': 'root',
        },
        'branch': 'master',
        'committer': {
            'email': 'artemkozlov68@gmail.com',
            'name': 'root',
        },
        'content': str,
        'dates': {
            'author': '2022-08-30T06:42:19.818Z',
            'committer': '2022-08-30T06:42:19.818Z',
        },
        'message': '',
        'new_branch': 'master',
        # 'sha':"",
        'signoff': True,
        # 'type':'file',
    }




    response = requests.post('http://localhost:3000/api/v1/repos/user1/test/contents/testfile2.md', headers=headers,json=json_data)
    # info = requests.get('http://localhost:3000/api/v1/repos/root/test/contents/readme2.md', headers=headers,json=json_data)
    # sha = find_param("sha",info)
    # json_data['sha'] = sha
    # response2 = requests.get('http://localhost:3000/api/v1/repos/root/test/contents/readme2.md', headers=headers,json=json_data)


start_gitea()
token = auth()
# create_user()
print(user_is_here("user1"))
create_repo('my_test_repo2',token)
push_file(token)
stop_gitea()


