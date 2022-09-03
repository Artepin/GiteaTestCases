import os
import configparser
import requests
import base64
import subprocess


def start_gitea():
    cur_dir = os.getcwd()
    sub = subprocess.run('whoami', stdout=subprocess.PIPE)
    user = sub.stdout.decode('ASCII').split("\n")[0]
    os.chdir('/home/' + user + '/gitea')
    start_docker = subprocess.run(['docker-compose','up','-d'], capture_output=True)
    # os.system('docker-compose up -d')
    output = start_docker.stderr.decode('ASCII').split("\n")
    os.chdir(cur_dir)
    for i in output:
        if 'done' in i:
            return True


def stop_gitea():
    cur_dir = os.getcwd()
    sub = subprocess.run('whoami', stdout=subprocess.PIPE)
    user = sub.stdout.decode('ASCII').split("\n")[0]
    os.chdir('/home/' + user + '/gitea')
    os.system('docker-compose down')
    os.chdir(cur_dir)
    print()


def get_root_token():
    username = "root"
    return get_token(username, username)


def get_user_token():
    config = configparser.ConfigParser()
    config.read('./token.ini')
    return config['DEFAULT']['USER_TOKEN']


def get_token(username, passwd):
    config = configparser.ConfigParser()
    # cur_dir = os.getcwd()
    path = "./token.ini"
    if os.path.exists(path):
        config.read(path)
    else:
        config['DEFAULT'] = {}
        config['DEFAULT']['TOKEN'] = ''
        config['DEFAULT']['USER_TOKEN'] = ''
    if username == 'root':
        gitea_part_token = call_part_token(username, passwd)
        print("Проверка наличия токена в файле.")

        if gitea_part_token in config['DEFAULT']['TOKEN'] and gitea_part_token !='':
            print("Nокен актуален.")
            # return config['DEFAULT']['TOKEN']
        else:
            print('Токен не актуален. Запрос нового токена.')
            config['DEFAULT']['TOKEN'] = str(auth(username, passwd))
            with open(path, 'w') as configfile:
                config.write(configfile)
        return config['DEFAULT']['TOKEN']
    else:
        gitea_part_token = call_part_token(username, passwd)
        if gitea_part_token in config['DEFAULT']['USER_TOKEN'] and gitea_part_token !='':
            print("Токен пользователя актуален.")
            # return config['DEFAULT']['USER_TOKEN']
        else:
            print('Токен не актуален. Запрос нового токена пользователя.')
            config['DEFAULT']['USER_TOKEN'] = str(auth(username, passwd))
            with open(path, 'w') as configfile:
                config.write(configfile)
        return config['DEFAULT']['USER_TOKEN']


def call_part_token(username, passwd):
    headers = {
        'accept': 'application/json',
    }

    json_data = {
        'name': 'test',
    }
    response = requests.get('http://localhost:3000/api/v1/users/' + username + '/tokens', headers=headers,json=json_data, verify=False, auth=(username, passwd))
    if len(response.text) < 4:
        return ''
    else:
        part_token = find_param('token_last_eight', response)
        return part_token


def auth(username, passwd):
    headers = {
        'accept': 'application/json',
    }

    json_data = {
        'name': 'test',
    }
    response = requests.post('http://localhost:3000/api/v1/users/' + username + '/tokens', headers=headers,
                             json=json_data, verify=False, auth=(username, passwd))
    print(response)
    sha = find_param("sha", response)
    return sha


def find_param(param, response):
    response = response.text.split(",")
    for i in response:
        if param in i:
            res = i.split(":")[1]
            result = res.split('"')[1]
            print()
            return result


def request(req, token):
    headers = {
        'accept': 'application/json',
        'authorization': 'token ' + token,
    }
    response = requests.get("http://localhost:3000" + req, headers=headers)
    return response


def create_user(root_token):
    username = "user1"
    password = "password"
    if not user_is_here(username):
        headers = {
            'accept': 'application/json',
            'authorization': 'token ' + root_token,
        }

        json_data = {
            'email': 'user@example.com',
            'full_name': username,
            'login_name': username,
            'must_change_password': False,
            'password': password,
            'send_notify': True,
            'source_id': 0,
            'username': username,
            'visibility': 'public',
        }

        response = requests.post('http://localhost:3000/api/v1/admin/users', headers=headers, json=json_data)
    user_token = get_token(username, password)



def user_is_here(user):
    list_of_users = []
    response = request('/api/v1/admin/users', root_token)
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


def create_repo(name, token):
    headers = {
        'accept': 'application/json',
        'authorization': 'token ' + token,
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


def info(token):
    headers = {
        'accept': 'application/json',
        'authorization': 'token ' + token,
    }
    response = requests.get('http://localhost:3000/api/v1/users/')
    return response


def push_file(token,path):
    name_of_file, content = get_file(path)
    str = "test_text_for_me"
    content = encode_import_text(content)
    inf = info(token)
    headers = {
        'accept': 'application/json',
        'authorization': 'token ' + token,
        # Already added when you pass json= but not when you pass data=
        'Content-Type': 'application/json',
    }

    json_data = {
        'author': {
            'email': find_param('email', inf),
            'name': find_param('username', inf),
        },
        'branch': 'master',
        'committer': {
            'email': find_param('email', inf),
            'name': find_param('username', inf),
        },
        'content': content,
        'dates': {
            'author': '2022-08-30T06:42:19.818Z',
            'committer': '2022-08-30T06:42:19.818Z',
        },
        'message': '',
        'new_branch': 'master',
        'signoff': True,
    }
    response = requests.post('http://localhost:3000/api/v1/repos/user1/test/contents/'+name_of_file, headers=headers,
                             json=json_data)

def get_file(path):
    with open(path, 'r') as file:
        file_name = file.name
        temp_name = file_name.split('/')
        file_name = temp_name[len(temp_name)-1]
        return file_name, file.read()


start_gitea()
root_token = get_root_token()
create_user(root_token)
user_token = get_user_token()
create_repo('test', user_token)
cur_dir = os.getcwd()
sub = subprocess.run('whoami', stdout=subprocess.PIPE)
user = sub.stdout.decode('ASCII').split("\n")[0]
push_file(user_token,cur_dir + '/test.txt')
stop_gitea()
