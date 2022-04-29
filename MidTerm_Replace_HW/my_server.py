'''
Send response as:
    HTTP/1.1 {code} {status}
    HOST: {HOST}/{path}
    Content-Type: text/html
    Connection: keep-alive
    Content-Length: {len(body)}
    DATE: {dateteim.now()}

    {body}

with respect to received request from server.
'''
from datetime import datetime
from socket import *

### Variables
## html file root folder
root_dir = "D:/ComputerNetwork/"

## Address
HOST = 'localhost'
IP = '127.0.0.1' if HOST == 'localhost' else HOST
PORT = 8080

## POST/PUT
DB = {}     # create/update {key:value} with POST/PUT
POST_continue = False   # skip acception for POST 100 CONTINUE response

## Status
STATUS = {100:'CONTINUE', 200:'OK',
          400:'BAD_REQUEST', 404:'NOT_FOUND', 405:'METHOD_NOT_ALLOWED'}


### Interpretate request / Detect error / Return response
def from_request_to_response(method, url, request_body):
    '''
    1. code = 400, status = BAD_REQUEST
       body = "DIFFERNET HOST: {input host}"
    2. code = 404, status = NOT_FOUND
       1) body = "WRONG ADDRESS: {input url}"
       2) body = "CANNOT FIND {input path}"
    3. code = 405, status = MEHOTD_NOT_ALLOWED
       1) body = "NOT ALLOWED METHOD: {input method}"
       2) body = "NOT ALLOWED PATH: {input path}"
    '''
    if method not in ["HEAD", "GET", "POST", "PUT"]:    # Error 3-1
        body = f"NOT ALLOWED METHOD: {method}"
        response = response_formatting(405, url.split('/')[1][:-1], body)
        response += body

    if '/' in url:

        host, path = url.split('/')
        path = path[:-1] # Eluminate "\r"
        if host == IP:

            # HEAD & GET: read html file
            if 'html' in path:
                
                # save html file in body
                body = open_html(path)
                if body == None:    # Error 2-2
                    body = f"CANNOT FIND {path}"
                    response = response_formatting(404, path, body)
                    response += body
                
                # Return response corresponse to HEAD and GET
                else:
                    if   method == "HEAD": response = HEAD(path, body)
                    elif method == "GET" : response =  GET(path, body)

            
            # Actually, POST for creating new content and PUT for updating
            # But both 'create' and 'update' are allowed to be input as path of POST and PUT
            elif (path == 'create') or (path == 'update'):
                if   method == "POST": response = POST(path, request_body)
                elif method == "PUT" : response =  PUT(path, request_body)

            else:   # Error 3-2
                body = f"NOT ALLOWED PATH: {path}"
                response = response_formatting(405, path, body)
                response += body

        else:   # Error 1
            body = f"DIFFERENT HOST: {host}"
            response = response_formatting(400, path, body)
            response += body

    else:   # Error 2-1
        body = f"WRONG ADDRESS: {url}"
        response = response_formatting(404, "?", body)
        response += body
    
    return response


### Basic response format
def response_formatting(code, path, body=''):
    '''
    Use {path} in request and input {body}
    Return HTTP-protocol-like response
    '''
    length = len(body) if body else 0

    return f'''\
HTTP/1.1 {code} {STATUS[code]}\r
Host: 127.0.0.1/{path}\r
Content-Type: text/html\r
Connection: keep-alive\r
Content-Length: {length}\r
DATE: {datetime.now().strftime("%a, %d %b %Y %H:%M:%S KST")}\r\n\n'''


### Method function
def HEAD(path, body):
    '''
    code = 100, status = CONTINUE
    get body from `open_html` function, but
    exclude {body}
    '''
    response = response_formatting(100, path, body)

    return response
    
def GET(path, body):
    '''
    code = 200, status = OK
    get body from `open_html` function
    include {body}
    '''
    if DB:
        body += '\nData in DB (created by POST/PUT):\r\n'
        for key in DB:
            body += f"\t{key}:{DB[key]}\r\n"
    body = body[:-2]    # eliminate last \r\n

    response = response_formatting(200, path, body)
    response += body

    return response

def POST(path, request_body):
    '''
    1. code = 100, status = CONTINUE
       body = "What do you want to POST to create?
               (key=value pairs separated with &)"
    2. code = 200, status = OK
       body = "post OK: {key:value pairs separated with /}"
    3. code = 400, status = BAD_REQUEST
       body = "ALREADY EXIST KEY: {key}"
    '''
    # 1.
    if request_body == '':
        body = "What do you want to POST to create?\n(key=value pairs separated with &)"
        response = response_formatting(100, path, body)
        response += body

    else:
        global DB
        pairs = request_body.split('&')
        for pair in pairs:
            key, val = pair.split('=')
            if key not in DB:
                DB[key] = val
            
            # Error 3
            else:
                body = f"ALREADY EXIST KEY: {key}"
                response = response_formatting(400, path, body)
                response += body
                return response

        # 2.
        body = "post OK "
        request_body.replace('&', '/')
        request_body.replace('=', ':')
        body += f"{request_body}"
        
        response = response_formatting(200, path, body)
        response += body
    
    return response

def PUT(path, request_body):
    '''
    1. code = 200, status = OK
       body = "put OK:
                   Updated:
                      {{key}:{new_one} from {old_one}} separated with \n
                   Created:
                      {key:value} pairs separated with /"
              from received request
    2. code = 400, status = BAD_REQUEST
       body = "EMPTY KEY=VALUE PAIRS"
    '''
    # Error 2-1
    if request_body == '':
        body = "EMPTY KEY=VALUE PAIRS"
        response = response_formatting(400, path, body)
        response += body
    
    else:
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
        
        # 1.
        body = "put OK:\r\n"
        update_body = "\tUpdated -\r\n"
        create_body = "\tCreated -\r\n\t\t"
        for key in request_keys:
            if key in old_values:
                update_body += f"\t\t{key}:{DB[key]} from {old_values[key]}\n"
            else:
                create_body += f"{key}:{DB[key]}/"
        body += update_body + create_body[:-1]

        response = response_formatting(200, path, body)
        response += body

    return response
        

### Read html
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


### Create server (TCP)
server_socket = socket(AF_INET, SOCK_STREAM)
server_socket.bind( (IP, PORT) )
server_socket.listen()


### Waiting for client(s)
while True:
    '''
    In TCP, server needs to be always on.
    '''
    print(f"The server ({IP}:{PORT}) is ready to receive ...")

    ## Accept client
    # skip accept from other client when POST_continue == True
    if not POST_continue:
        client_socket, address = server_socket.accept()
        print('\n', "="*22, f" CONNECTED - {address[0]}:{address[1]:5d} ", "="*22, '\n', sep='')

    ## Receive request
    print(">>> Receiving request ...")

    request = client_socket.recv(65535).decode('utf-8')
    print(request)

    if 'END' in request:
        print("client request END. Quit server.")
        break
    
    request = request.split('\n')

    ## Interprete request
    method = request[0].split()
    method = method[0]
    url = request[1][6:]   # request[1] = Host: {url}
    request_body = request[-1]
    
    ## Return response
    response = from_request_to_response(method, url, request_body)

    ## Send response
    print("\n>>> Sending response ...")
    client_socket.sendall(response.encode('utf-8'))
    
    # If send POST 100 CONTINUE
    POST_continue = 'What do you want to' in response.split('\n')[-2]

    ## End
    print("="*33, " ENDED ", "="*33, '\n\n', sep='')

### Close client and server when break
client_socket.close()
server_socket.close()
print("\nServer is successfully closed")
