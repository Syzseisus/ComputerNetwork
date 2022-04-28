from datetime import datetime
from socket import *

### Variables
root_dir = "D:/ComputerNetwork/"    # where .html files exist
HOST = '127.0.0.1'
IP = '127.0.0.1' if HOST == 'localhost' else HOST
PORT = 8080
DB = {}    # create {KEY:VALUE} with POST/PUT, update value of key with PUT
POST_continue = False   # for POST 100 CONTINUE

### Interpreting request / Return response
def HandlingData(url, method, request_body):
    '''
    Returns response correspond to {method}
    Return 4xx reponse when:
        1. method is not in [HEAD, GET, POST, PUT]
        2. there is no html file in root_dir
        3. path is not in [*.html, create, update]
        4. requested host != HOST
        5. format of url is not {host}/{path}
    respectively
    '''
    if method not in ["HEAD", "GET", "POST", "PUT"]:
        return STATUS_4xx(405, method)

    if '/' in url:

        host, path = url.split('/')
        path = path[:-1] # Eluminate "\r"
        if host == HOST:

            # HEAD & GET: read html file
            if 'html' in path:
                
                # save html file in body
                body = open_html(path)
                print("TYPE OF BODY:", type(body))
                if body == None:
                    response = STATUS_4xx(404, method)
                
                # Return response corresponse to HEAD and GET
                else:
                    if   method == "HEAD": response = HEAD(path, body)
                    elif method == "GET" : response =  GET(path, body)

            
            # Actually, POST for creating new content and PUT for updating
            # But both 'create' and 'update' are allowed to be input as path of POST and PUT
            elif (path == 'create') or (path == 'update'):
                if   method == "POST": response = POST(path, request_body)
                elif method == "PUT" : response =  PUT(path, request_body)

            else:
                response = STATUS_4xx(405, method)

        else:
            response = STATUS_4xx(400, method)

    else:
        response = STATUS_4xx(404, method)
    
    return response


def response_formating(path, body=''):
    '''
    Use {path} in request and input {body}

    Return HTTP-protocol-like response
    '''
    length = len(body) if body else 0

    return f'''\
Host: 127.0.0.1/{path}\r
Content-Type: text/html\r
Connection: keep-alive\r
Content-Length: {length}\r
DATE: {datetime.now().strftime("%a, %d %b %Y %H:%M:%S KST")}\r\n\n'''


### Method Function
def HEAD(path, body):
    '''
    HEAD returns only the length of body
    '''    
    # HEAD 100 CONTINUE
    response = CONTINUE
    response += response_formating(path, body)

    return response


def GET(path, body):
    '''
    GET returns both the length and contents of body
    Also returns contents in DB 
    '''
    # GET 200 OK
    response = OK

    # Add contents in DB
    if DB:
        body += "\nData in DB (created by POST/PUT):\r\n"
        for key in DB:
            body += f"\t{key}:{DB[key]}\r\n"

    response += response_formating(path, body)
    response += body

    return response


def POST(path, request_body):
    '''
    Create new {key}:{value} pairs
    which are expressed in {request_body} as {key}={value}&...&{key}={value}

    If {request_body} == None,
    Server ask the request_body to client

    If format is different or
    There is {key} already in DB,
    It returns BAD REQUEST
    '''
    # Ask input to client when {request_body} is empty
    if request_body == '':
        body = "What do you want to POST to create? (key=value with &)"

        # Add response to body
        response  = CONTINUE
        response += response_formating(path, body)
        response += body

        return response

    # Check format of {request_body}
    try:
        global DB
        contents = request_body.split('&')
        for key_value in contents:
            key, value = key_value.split('=')
            if key in DB:
                return STATUS_4xx(400, method)
            else:
                DB[key] = value
    
    except Exception as ex:
        return STATUS_4xx(400, method)

    # POST body = post OK key:value/key:value/...
    body = "post OK "
    request_body.replace('&', '/')
    request_body.replace('=', ':')
    body += f"{request_body}\r\n"

    # Add body to response
    response  = OK
    response += response_formating(path, body)
    response += body

    return response


def PUT(path, request_body):
    '''
    Create/update {key}:{value} pairs
    which are expressed in {request_body} as {key}={value}&...&{key}={value}

    Update if {key} in {DB} and
    Create if {key} not in {DB}

    If {request_body} == None or format is different,
    returns BAD REQUEST
    '''
    # Check whether {request_body} is empty or not
    if request_body == '':
        return STATUS_4xx(400, method)
    
    # Check format of {request_body}
    try:
        global DB
        old_values = {}
        request_keys = []
        contents = request_body.split('&')
        for key_value in contents:
            key, value = key_value.split('=')
            request_keys.append(key)
            if key in DB:
                old_val = DB[key]
                old_values[key] = old_val
                DB[key] = value
            else:
                DB[key] = value
            
    except:
        return STATUS_4xx(400, method)

    response = OK

    # PUT body =
    #     put OK:
    #         key updated: new_value from old_value
    #         key created: new_value
    #           ...
    body = "put OK:\r\n"
    for key in request_keys:
        if key in old_values:
            body += f"\t{key} updated: {DB[key]} from {old_values[key]}\r\n"
        else:
            body += f"\t{key} created: {DB[key]}\r\n"

    response += response_formating(path, body)
    response += body
    
    return response    
    

### html Function
def open_html(file_path):
    '''
    Read {file_path} and return body as:
    HEADS in {filepath}:
        {tag1}: {value1}
        {tag2}: {value2}
            ...
    CONTENTS in {filepath}:
        {line 1}
        {line 2}
            ...

    If {file_path} doesn't exist or something wrong with reading
    Return body = None to response 404 NOT FOUND
    '''
    try :
        with open(root_dir + file_path, encoding='utf-8') as f:
            body = f"HEADS in {file_path}:\n"
            lines = f.readlines()
            for line in lines:
                if   "<head>"  in line:
                    flag = "head"
                elif "<body>"  in line:
                    flag = "body"
                    body += f"CONTENTS in {file_path}:\n"
                elif "</head>" in line: continue
                elif "</body>" in line: break
                else:
                    tag = line[line.find('<') + 1:line.find('>')]
                    if flag == "head":
                        body += f"\t{tag}: {line[line.find('>') + 1: line.find('</')]}\n"
                    if flag == "body":
                        body += f"\t{line[line.find('>') + 1: line.find('</')]}\n"

    except:
        body = None
    
    return body


### Status
CONTINUE = "HTTP/1.1 100 CONTINUE\r\n"
OK       = "HTTP/1.1 200 OK\r\n"

# For 4xx, add method name
def STATUS_4xx(code, method):
    response = f"HTTP/1.1 {method} {code} "
    if   code == 400: response += f"BAD_REQUEST\r\n"
    elif code == 404: response += f"NOT_FOUND\r\n"
    elif code == 405: response += f"METHOD_NOT_ALLOWED"

    return response   
    

### Create server (TCP)
server_socket = socket(AF_INET, SOCK_STREAM)
server_socket.bind( (HOST, PORT) )
server_socket.listen()

### waiting for client(s)
while True:
    '''
    In TCP, server needs to be always on.
    '''
    print(f"The server ({IP}:{PORT}) is ready to receive ...")

    ## Accept client
    # skip accept from other client when POST_continue == True
    if not POST_continue:
        client_socket, address = server_socket.accept()
        print('\n', "="*8, f" CONNECTED - {address[0]}:{address[1]:5d} ", "="*9, '\n', sep='')

    ## Receive request
    print(">>> Receiving request ...")

    data = client_socket.recv(65535).decode('utf-8')
    print(data)

    if data == 'END':
        print("client request END. Quit server.")
        break
    
    data = data.split('\n')

    ##  Handling request
    method = data[0].split()
    method = method[0]
    url = data[1][6:]   # data[1] = Host: {url}
    request_body = data[-1]
    
    ## Send response
    response = HandlingData(url, method, request_body)
    print("\n>>> Sending response ...")
    client_socket.sendall(response.encode('utf-8'))
    
    # If send POST 100 CONTINUE
    if 'What do you want to' in response.split('\n')[-1]:
        POST_continue = True
    else:
        POST_continue = False

    ## End
    print("="*20, " ENDED ", "="*21, '\n', sep='')

### Close client and server when break
client_socket.close()
server_socket.close()
print("\nServer is successfully closed")
