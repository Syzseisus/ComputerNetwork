'''
Send request as:
    {METHOD} / HTTP/1.1
    Host: 127.0.0.1/{PATH}
    Content-Type: text/html
    Connection: keep-alive
    Content-Length: {len(REQUEST_BODY)}

    {REQUEST_BODY}
'''
from socket import *


### Variables: be aware of IP == server.IP / PORT == server.POST
IP = '127.0.0.1'
PORT = 8080


### Test case
test_case = [
    # method, path, body
    # 1. Correctly Act
    ('HEAD', 'dummy.html', '', IP),
    ('GET ', 'dummy.html', '', IP),
    ('POST', 'create', '', IP),     # -> will resend "User-Affiliation=KMU"
    ('POST', 'create', 'User-ID=K2022031&Grade=F', IP),
    ('PUT' , 'update', 'Grade=A+&Major=Artificial Intelligence', IP),
    ('GET' , 'dummy.html', '', IP),
    # 2. Bad Act
    # 1) Detected in `from_request_to_response`
    ('HEAD', 'dummy.html', '', '1.1.1.1'),
    ('GET' , 'foo.exe', '', IP),
    ('HEAD', 'foo.html', '', IP),
    ('FOO' , 'dummy.html', '', IP),
    ('PUT' , 'foo', '', IP),
    # 2) Detected in `POST`, `PUT`
    ('POST', 'create', 'Grade=B', IP),
    ('PUT' , 'create', '', IP),
    # 3. END
    ('END', '' , '', IP)
]


### Return Request
def request_formatting(method, path, body, IP=IP):
    '''
    Use input {method}, {url}, {body}
    and variable {IP}

    Return HTTP-protocol-like request
    '''

    return f'''\
{method} / HTTP/1.1\r
Host: {IP}/{path}\r
Content-Type: text/html\r
Connection: keep-alive\r
Content-Length: {len(body)}\r\n\n{body}'''


### Send request and Receive response until user input EXIT
test = 0   # for test case
while True:
    print("#"*7, f"Test {test:02d}:\n {test_case[test]}")

    ## Create client socket and connect to server
    client_socket = socket(AF_INET, SOCK_STREAM)
    client_socket.connect( (IP, PORT) )

    print('\n', "="*22, f" CONNECTED - {IP}:{PORT} ", "="*23, '\n', sep='')
    
    ## Make request
    method, path, body, target = test_case[test]
    if method == 'END': 
        request = 'END'
        client_socket.sendall(request.encode('utf-8'))
        break
    else:
        request = request_formatting(method, path, body, target)
        test += 1  # for test case

    ## Send request
    print("\n>>> Send Request ...")
    client_socket.sendall(request.encode('utf-8'))

    ## Receive response
    print("\n>>> Receive Response ...\n")
    response = client_socket.recv(65535).decode('utf-8')
    
    # If receive POST 100 CONTINUE
    if 'What do you want to' in response.split('\n')[-2]:
        while True:
            # body = input("input request details again:")
            body = 'User-Affiliation=KMU'
            if body:
                request = request_formatting(method, path, body, IP)
                print("\n>>> Send content wanted to be POST ...")
                client_socket.sendall(request.encode('utf-8'))
                print("\n>>> Receive Response ...\n")
                response = client_socket.recv(65535).decode('utf-8')
                break

    ## Print received response
    print(response)

    ## End
    print("="*33, " ENDED ", "="*33, '\n\n', sep='')
    client_socket.close()

### Close client when break
client_socket.close()
print("\nClient is successfully closed")
