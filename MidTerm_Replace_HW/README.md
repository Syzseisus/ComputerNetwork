# 과제 설명
\- 소켓 통신을 활용하여 [Server](https://github.com/Syzseisus/ComputerNetwork/blob/main/MidTerm_Replace_HW/my_server.py), 
[Client](https://github.com/Syzseisus/ComputerNetwork/blob/main/MidTerm_Replace_HW/my_client.py) 프로그램 작성 (Python)  
\- TCP 기반 소켓 프로그래밍 작성 후  
Client에서는 HTTP 프로토콜의 GET/HEAD/POST/PUT Request를 요청하여  
Server에서는 Client의 Request에 따라 응답 메시지를 구성하여 Response하도록 구현  
(TCP 기반 Client, Server 구현한 프로그램 파일을 제출)  
* 예) Method-응답 xxx의 case 5개 이상 수행  
GET-응답 4xx, GET-응답 2xx, HEAD-응답 1xx, POST-응답 2xx, POST-응답 1xx 등  
* 소켓 통신은 PC가 2대 이상이면 Client, Server 실행은 분리하여 진행을 권장  
2대 이상 환경이 안되는 경우는 localhost로 진행도 가능  
* HTTP 명령어 수행 결과를 WireShark로 캡쳐하여 제출하는 경우는 가산점 부여


## 구조
* TCP socket programming
* server의 host와 port를 사용해서 client 연결하는 localhost 연결
* HTTP 기반으로 통신하되 `if-else`문을 기반으로 request와 response를 해석한다


## client의 Request 형식
```
{METHOD} / HTTP/1.1
Host: 127.0.0.1/{PATH}
Content-Type: text/html
Connection: keep-alive
Content-Length: {len(REQUEST_BODY)}

{REQUEST_BODY}
```
* `METHOD`: `HEAD`, `GET`, `POST`, `PUT` 중 하나
* `PATH`: `HEAD`와 `GET`은 \*.html 파일의 이름을 받고  
`POST`와 `PUT`은 각각 기본적으로 create와 update를 받으나 혼용 가능하다.
* `REQUEST_BODY`: `POST`, `PUT`을 통해 서버에 생성하고자 하는 데이터.  
`key1=val1&...&key2=val2` 형식으로 작성해야 한다.


## server의 Response 형식
```
HTTP/1.1 {code} {status}
HOST: {HOST}/{path}
Content-Type: text/html
Connection: keep-alive
Content-Length: {len(body)}
DATE: {dateteim.now()}

{body}
```
* Request의 해석에 따라 다음 중 하나로 `code`와 `status`가 정해진다.
    * 100 CONTINUE
    * 200 OK
    * 404 NOT FOUND
    * 405 NOT ALLOWED METHOD
* `HOST`: 현 서버의 IP
* `path`: request로 들어온 `path`와 같은 값이다.
* `body`: `HEAD`를 제외한 request는 해당하는 본문을 `body`로 갖는다.
    * `GET`: \*.html의 내용이 출력된다.
    * `POST`/`PUT`: 요청했던 key와 value에 대해 `post/put OK k:v/.../k:v`


## 구현가능한 Method와 응답
1. HEAD
    * 100 CONTINUE: html 있을 때
    * 404 NOT FOUND: html 없을 때
2. GET
    * 200 OK: html 있을 떄
    * 404 NOT FOUND: html 없을 때
    * 405 NOT ALLOWED METHOD: \*.html이 아니게 적었을 떄
3. POST
    * 100 CONTINUE: body 입력하지 않았을 때
    * 200 OK: body 제대로 입력했을 때
    * 400 BAD REQUEST: body 제대로 입력하지 않았을 때
    * 405 NOT ALLOWED METHOD: path 이상하게 적었을 때 (create, update 아닐 때)
4. PUT
    * 200 OK: body 제대로 입력했을 때
    * 400 BAD REQUEST: body 제대로 입력하지 않았을 떄
    * 405 NOT ALLOWED METHOD: path 이상하게 적었을 때 (create, update 아닐 때)


## 코드 설명
### 1. [server.py](https://github.com/Syzseisus/ComputerNetwork/blob/main/MidTerm_Replace_HW/my_server.py)
1. `import`
    - 현재 시각 반환을 위한 `datetime`
    - 소켓 통신을 위한 `socket`
    ```python
    from datetime import datetime
    from socket import *
    ```
2. 변수
    - `root_dir`: \*.html 파일 저장되어 있는 곳 (=cmd로 python 실행시키는 폴더)
    - `HOST`, `IP`, `PORT`: server 주소
    - `DB`: `POST`, `PUT` request를 통해 서버에 저장된 데이터
    - `POST_continue`: `POST 100`이 발생했을 때 server가 기존 client와 연결을 유지하고 있게 하기 위함
    ```python
    root_dir = "D:/ComputerNetwork/"
    HOST = '127.0.0.1'
    IP = '127.0.0.1' if HOST == 'localhost' else HOST
    PORT = 8080
    DB = {}
    POST_continue = False
    ```
3. Request 처리
    - HTTP protocol로 들어온 request를 해석하고 적절한 response 반환
    - 첫 번째 `if` 문: `method` 확인
    - 두 번째 `if-else` 문: request로 들어온 `host` 확인
    - 세 번째 `if-else` 문: `path` 확인
    - 네 번째 `if-else` 문: \*.html 파일이 제대로 읽히는 지 확인
    ```python
    def HandlingData(url, method, request_body):
        if method not in ["HEAD", "GET", "POST", "PUT"]:
            return STATUS_4xx(405, method)

        if '/' in url:

            host, path = url.split('/')
            path = path[:-1]
            
            if host == HOST:

                if 'html' in path:

                    body = open_html(path)
                    print("TYPE OF BODY:", type(body))
                    if body == None:
                        response = STATUS_4xx(404, method)

                    else:
                        if   method == "HEAD": response = HEAD(path, body)
                        elif method == "GET" : response =  GET(path, body)

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
    ```
4. response 작성
    * 4xx를 제외한 response가 기본적으로 갖는 형식입니다.
    ```python
    def response_formating(path, body=''):
        length = len(body) if body else 0

        return f'''\
    Host: 127.0.0.1/{path}\r
    Content-Type: text/html\r
    Connection: keep-alive\r
    Content-Length: {length}\r
    DATE: {datetime.now().strftime("%a, %d %b %Y %H:%M:%S KST")}\r\n\n'''
    ```
5. Method function
    * Method에 따른 response를 반환합니다.
    * `HEAD`: `100 CONTINUE`를 헤더로 \*.html 본문의 길이를 포함하여 반환합니다.
        ```python
        def HEAD(path, body):
            response = CONTINUE
            response += response_formating(path, body)

            return response
        ```
    * `GET`: `200 OK`를 헤더로 \*.html 본문의 길이를 포함하며, 본문을 `body`로 반환합니다.  
추가로 `DB`에 데이터가 있다면 같이 `body`로 반환합니다.
        ```python
        def GET(path, body):
            response = OK

            if DB:
                body += "\nData in DB (created by POST/PUT):\r\n"
                for key in DB:
                    body += f"\t{key}:{DB[key]}\r\n"

            response += response_formating(path, body)
            response += body

            return response
        ```
    * `POST`: `request_body`가 없으면 `100 CONTINUE`를, 있으면 `200 OK`를 헤더로 하며 추가된 데이터를 `body`로 반환합니다.
        ```python
        def POST(path, request_body):
            if request_body == '':
                body = "What do you want to POST to create? (key=value with &)"

                response  = CONTINUE
                response += response_formating(path, body)
                response += body

                return response

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

            body = "post OK "
            request_body.replace('&', '/')
            request_body.replace('=', ':')
            body += f"{request_body}\r\n"

            response  = OK
            response += response_formating(path, body)
            response += body

            return response
        ```
    * `PUT`: `request_body`가 없으면 `400 BAD REQUEST`를, 있으면 `200 OK`를 헤더로 하여 추가/업데이트된 데이터를 `body`로 반환합니다.
        ```python
        def PUT(path, request_body):
            if request_body == '':
                return STATUS_4xx(400, method)

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
            
            body = "put OK:\r\n"
            for key in request_keys:
                if key in old_values:
                    body += f"\t{key} updated: {DB[key]} from {old_values[key]}\r\n"
                else:
                    body += f"\t{key} created: {DB[key]}\r\n"

            response += response_formating(path, body)
            response += body

            return response  
        ```
6. html function
    * \*.html 파일을 읽는 함수입니다.
    * 파일이 없는 등 파일을 읽는 중 오류가 발생하면 `body`로 `None`을 반환하여 `HandlingData` 함수에서 response로 `404 NOT FOUND`를 반환하도록 합니다.
        ```python
        def open_html(file_path):
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
        ```
7. 상태에 대한 변수와 함수
    * response로 보낼 헤더들을 상태 별로 구분해뒀습니다.
    * 4xx 상태들은 어떤 `method`에 의한 상태인지도 추가하였습니다.
        ```python
        CONTINUE = "HTTP/1.1 100 CONTINUE\r\n"
        OK       = "HTTP/1.1 200 OK\r\n"

        def STATUS_4xx(code, method):
            response = f"HTTP/1.1 {method} {code} "
            if   code == 400: response += f"BAD_REQUEST\r\n"
            elif code == 404: response += f"NOT_FOUND\r\n"
            elif code == 405: response += f"METHOD_NOT_ALLOWED"

            return response
        ```
8. 서버 생성
    * Variable에서 지정해둔 `HOST`와 `PORT`를 주소로 TCP 서버를 만듭니다.
        ```python
        server_socket = socket(AF_INET, SOCK_STREAM)
        server_socket.bind( (HOST, PORT) )
        server_socket.listen()
        ```
9. client와 통신(1) - accept
    * client의 connection을 기다렸다가 (`while True`) accept합니다.
    * `POST 100 CONTINUE`가 발생한 경우 새로 connection을 요청하는 client가 나오지 않기 때문에 accept을 스킵합니다.
        ```python
            if not POST_continue:
                client_socket, address = server_socket.accept()
        ```
10. client와 통신(2) - receive request
    * client의 request를 수신합니다.
        ```python
            data = client_socket.recv(65535).decode('utf-8')
        ```
11. client와 통신(3) - request 해석, response 반환
    * request를 적절히 분해 후 `HandlingData` 함수로 적절한 response를 만듦니다.
    * `if`문은 client에서 'END'를 보낼 경우 server를 끄기 위한 부분입니다.
        ```python
            if data == 'END': break

            data = data.split('\n')

            method = data[0].split()
            method = method[0]
            url = data[1][6:]   # data[1] = Host: {url}
            request_body = data[-1]

            response = HandlingData(url, method, request_body)
        ```
12. client와 통신(4) - response 보내기
    * 그렇게 만들어진 response를 client에게 보냅니다.
    * 만약 `POST 100 CONTINUE`인 경우 accept을 스킵하기 위해 `POST_continue`변수를 변경합니다.
        ```python
            client_socket.sendall(response.encode('utf-8'))
            
            if 'What do you want to' in response.split('\n')[-1]:
                POST_continue = True
            else:
                POST_continue = False
        ```


### 2. [client.py](https://github.com/Syzseisus/ComputerNetwork/blob/main/MidTerm_Replace_HW/my_client.py)
1. `import`
    * 소켓 통신을 위한 `socket`
        ```python
        from socket import *
        ```
2. 변수
    * `IP`, `PORT`: 연결하고자 하는 서버의 주소입니다.
        ```python
        IP = '127.0.0.1'
        PORT = 8080
        ```
3. request 작성
    * User가 `input`을 통해 입력해준 `method`, `url`, `body`와 variable `IP`를 이용해 request를 만듭니다.
        ```python
        def request_formating(method, url, body, IP):

            return f'''\
        {method} / HTTP/1.1\r
        Host: {IP}/{url}\r
        Content-Type: text/html\r
        Connection: keep-alive\r
        Content-Length: {len(body)}\r\n\n{body}'''
        ```
4. client 생성
    * TCP client를 생성합니다.
        ```python
            client_socket = socket(AF_INET, SOCK_STREAM)
        ```
5. server와 통신(1) - 연결
    * variables에 설정된 주소의 서버로 연결을 요청합니다. (TCP)
        ```python
            client_socket.connect( (IP, PORT) )
        ```
6. User의 입력
    * user의 입력을 통해 request를 만듭니다.
    * `method`에 END를 입력할 경우 `while True`를 빠져나옵니다.
        ```python
            method = input("input method in [HEAD, GET, POST, PUT, EXIT(end)]: ")
            if method.upper() == "EXIT":
                request = "END"
                client_socket.sendall(request.encode('utf-8'))
                break
            else:
                url  = input("input html url or create/update for POST/PUT: ")
                body = input("input request details:")
                body = body if body else ''
                request = request_formating(method, url, body, IP)
        ```
7. server와 통신(2) - request 전송
    * 그렇게 만든 request를 server로 전송합니다.
        ```python
            client_socket.sendall(request.encode('utf-8'))
        ```
8. server와 통신(3) - response 수신
    * 해당 request에 따라 server가 보낸 response를 받습니다.
        ```python
            response = client_socket.recv(65535).decode('utf-8')
        ```
9. server와 통신(4-1) - `POST 100 CONTINUE`
    * response로 `POST 100 CONTINUE`가 오면 user의 `input`을 다시 받고,
    * request를 다시 만들어서 전송하고,
    * response를 수신합니다.
        ```python
            if 'What do you want to' in response.split('\n')[-1]:
                while True:
                    body = input("input request details again:")
                    if body:
                        request = request_formating(method, url, body, IP)
                        client_socket.sendall(request.encode('utf-8'))
                        response = client_socket.recv(65535).decode('utf-8')
                        break
        ```
10. server와 통신(4-2) - 종료
    * server와 달리 client는 한 번 request와 response를 주고 받고나면 종료됩니다.
        ```python
            client_socket.close()
        ```


## 작동예시
### 100, 200 response
1. `dummy.html`에 대한 `HEAD` 요청  
   * client:  
   ![client_1](https://user-images.githubusercontent.com/83002480/165794763-d77bf8ad-fcee-4cf7-8117-ce228f61346f.png)  
   * server:  
   ![server_1](https://user-images.githubusercontent.com/83002480/165787031-9266ec8f-d11a-4306-ada8-ff93e06aecb8.png)  
2. `dummy.html`에 대한 `GET` 요청 (`DB` 생성 전)  
   * client:  
   ![client_2](https://user-images.githubusercontent.com/83002480/165794833-e51af60e-0231-49d6-8b1e-36022ba67b55.png)  
   * server:  
   ![server_2](https://user-images.githubusercontent.com/83002480/165787111-a90dd46a-4c25-46a2-aab2-22a086ba5009.png)  
3. `request_body`없이 `POST` 후 재 입력으로 `POST` 완료  
   * client:  
   ![client_3](https://user-images.githubusercontent.com/83002480/165794879-fe2e7406-4997-4c17-b968-6f5e5885f519.png)  
   * server:  
   ![server_3](https://user-images.githubusercontent.com/83002480/165787613-1ac80dc0-8d3a-4252-abd0-130c2ff2e11e.png)  
4. `request_body` 포함해서 바로 `POST`  
   * client:  
   ![client_4](https://user-images.githubusercontent.com/83002480/165794967-665ed80d-3fed-4456-83bf-8dad309668c9.png)  
   * server:  
   ![server_4](https://user-images.githubusercontent.com/83002480/165787341-89d55703-037e-4771-96c2-1dc3aaa4e9b7.png)  
5. 존재하는 key와 존재하지 않는 key를 하나 씩 `request_body`로 포함해서 `PUT`  
   * client:  
   ![client_5](https://user-images.githubusercontent.com/83002480/165795014-e7c6c787-f2b3-4540-b06b-c02df357ced5.png)  
   * server:  
   ![server_5](https://user-images.githubusercontent.com/83002480/165787668-a7dc9ff5-f86b-4b39-8209-07b92bdf021e.png)  
6. `DB` 생성 후 `dummy.html`에 대한 `GET` 요청  
   * client:  
   ![client_6](https://user-images.githubusercontent.com/83002480/165795075-239c1b8d-b78e-46e4-b0e3-84547b04a1ec.png)  
   *  server:  
   ![server_6](https://user-images.githubusercontent.com/83002480/165787730-8e3f02b2-556b-4619-8f6f-b4a06ced3a23.png)  
-----------------------------------------
### 4xx response
7. 존재하지 않는 method  
   * client:  
   ![client_7](https://user-images.githubusercontent.com/83002480/165795157-85f92d79-d74b-4952-89b9-9f3f39cec1ad.png)  
   * server:  
   ![server_7](https://user-images.githubusercontent.com/83002480/165787815-2c44ba0c-bd23-4777-8680-5467c8e7713f.png)  
8. 지원되지 않는 path 형식  
   * client:  
   ![client_8](https://user-images.githubusercontent.com/83002480/165795212-3490aa82-e85d-472b-9c95-d171bd8fcfee.png)  
   * server:  
   ![server_8](https://user-images.githubusercontent.com/83002480/165787906-61b69ec5-4ea9-4719-af53-eb1f8e4f090d.png)  
9. 존재하지 않는 html  
   * client:  
   ![client_9](https://user-images.githubusercontent.com/83002480/165795278-31fd76a5-8ad6-4dfe-81c1-e440cea86f27.png)  
   * server:  
   ![server_9](https://user-images.githubusercontent.com/83002480/165788490-abf21a94-49e0-460f-8f6a-de8c5a14bdf1.png)  
10. 존재하는 key에 대한 `POST` 요청  
   * client:  
   ![client_10](https://user-images.githubusercontent.com/83002480/165795333-db89660d-67c1-4993-b6d1-5a15468ff064.png)  
   * server:  
   ![server_10](https://user-images.githubusercontent.com/83002480/165788561-4c25f8e4-fa9b-42bc-94e7-60f0d9fa3712.png)  
11. 잘못된 형식의 `request_body`  
   * client:  
   ![client_11](https://user-images.githubusercontent.com/83002480/165795379-b85ed79a-1915-4872-9c6a-bfd15163d5f6.png)  
   * server:  
   ![server_11](https://user-images.githubusercontent.com/83002480/165788640-8819ebc4-5964-4635-a32d-4d6a62db3d90.png)  
12. `request_body == None`  
   * client:  
   ![client_12](https://user-images.githubusercontent.com/83002480/165795433-a7860a65-3f55-4961-aa76-3beca6582c03.png)  
   * server:  
   ![server_12](https://user-images.githubusercontent.com/83002480/165788707-bfa6e33d-f86a-4e80-9101-4dd0ebc58995.png)

### END protocol
13. `END` response
   * client:  
   ![client_13](https://user-images.githubusercontent.com/83002480/165795500-c8fbd39c-1e6b-4477-b41b-75f940ecd3ff.png)  
   * server:  
   ![server_13](https://user-images.githubusercontent.com/83002480/165788900-7ef623e5-3cc2-41a6-8e38-3c53cb266395.png)


## WireShark로 캡쳐한 통신
![image](https://user-images.githubusercontent.com/83002480/165795586-69d54c6a-46d5-4e6b-a025-b2db754f82fe.png)
