'''
This File creates client and send request.
When user inputs {METHOD}, {PATH} and {REQUEST_BODY},
then this file make HTTP-protocol-like request as:
    {METHOD} / HTTP/1.1
    Host: {IP}/{PATH}               # IP is hard coded as Variable.
    Content-Type: text/html
    Connection: keep-alive
    Content-Length: {len(REQUEST_BODY)}

    {REQUEST_BODY}

and sendall request to connected server,
receive RESPONSE and print {RESPONSE}

If server sends response 100 CONTINUE of POST request,
user has to re-input request body to successfully POST.

You can END this inputing "EXIT" as {METHOD}
'''
from socket import *

def request_formating(method, url, body, IP):
    '''
    Use input {method}, {url}, {body}
    and variable {IP}

    Return HTTP-protocol-like request
    '''

    return f'''\
{method} / HTTP/1.1\r
Host: {IP}/{url}\r
Content-Type: text/html\r
Connection: keep-alive\r
Content-Length: {len(body)}\r\n\n{body}'''


### Variables: be aware of IP == server.IP / PORT == server.POST
IP = '127.0.0.1'
PORT = 8080


### Send request and Receive response until user input EXIT
while True:
    ## Create client socket and connect to server
    client_socket = socket(AF_INET, SOCK_STREAM)
    client_socket.connect( (IP, PORT) )

    print('\n', "="*10, f" CONNECTED - {IP}:{PORT} ", "="*10, '\n', sep='')

    ## User input
    print(">>> ENTER REQUEST:\n")

    method = input("input method in [HEAD, GET, POST, PUT, EXIT(end)]: ")
    if method.upper() == "EXIT":        # Disconnect when user inputs EXIT
        request = "END"
        client_socket.sendall(request.encode('utf-8'))
        break
    else:
        url  = input("input html url or create/update for POST/PUT: ")
        body = input("input request details:")
        body = body if body else ''
        request = request_formating(method, url, body, IP)

    ## Send request
    print("\n>>> Send Request ...")
    client_socket.sendall(request.encode('utf-8'))

    ## Receive response
    print("\n>>> Receive Response ...\n")
    response = client_socket.recv(65535).decode('utf-8')
    
    # If receive POST 100 CONTINUE
    if 'What do you want to' in response.split('\n')[-1]:
        while True:
            body = input("input request details again:")
            if body:
                request = request_formating(method, url, body, IP)
                print("\n>>> Send content wanted to be POST ...")
                client_socket.sendall(request.encode('utf-8'))
                print("\n>>> Receive Response ...\n")
                response = client_socket.recv(65535).decode('utf-8')
                break

    ## Print received response
    print(response)

    ## End
    print("="*20, " ENDED ", "="*21, '\n', sep='')
    client_socket.close()

    
### Close client when break
client_socket.close()
print("\nClient is successfully closed")
