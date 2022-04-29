# 과제 설명
\- 소켓 통신을 활용하여 [Server](https://github.com/Syzseisus/ComputerNetwork/blob/main/MidTerm_Replace_HW/my_server.py), 
[Client](https://github.com/Syzseisus/ComputerNetwork/blob/main/MidTerm_Replace_HW/my_client.py) 프로그램 작성 (Python)  
\- TCP 기반 소켓 프로그래밍 작성 후  
&#x2004;&#x2004;Client에서는 HTTP 프로토콜의 GET/HEAD/POST/PUT Request를 요청하여  
&#x2004;&#x2004;Server에서는 Client의 Request에 따라 응답 메시지를 구성하여 Response하도록 구현  
&#x2004;&#x2004;(TCP 기반 Client, Server 구현한 프로그램 파일을 제출)  
* 예) Method-응답 xxx의 case 5개 이상 수행  
GET-응답 4xx, GET-응답 2xx, HEAD-응답 1xx, POST-응답 2xx, POST-응답 1xx 등  
* 소켓 통신은 PC가 2대 이상이면 Client, Server 실행은 분리하여 진행을 권장  
2대 이상 환경이 안되는 경우는 localhost로 진행도 가능  
* HTTP 명령어 수행 결과를 WireShark로 캡쳐하여 제출하는 경우는 가산점 부여



## 목록
1. [구조](#구조)
2. [client의 Request 형식](#client의-request-형식)
3. [server의 Response 형식](#server의-response-형식)
4. [구현가능한 Method와 응답](#구현가능한-method와-응답)
5. [코드 설명](#코드-설명)
   1. [server.py](#1-serverpy)
   2. [client.py](#2-clientpy)
6. [작동예시](#작동예시)
7. [WireShark로 캡쳐한 통신](#wireshark로-캡쳐한-통신)



## 구조
* TCP socket programming
* server의 host와 port를 사용해서 client 연결하는 localhost 연결
* HTTP 기반으로 통신하되 `if-else`문을 기반으로 request와 response를 해석한다



## client의 Request 형식
>{METHOD} / HTTP/1.1  
>Host: 127.0.0.1/{PATH}  
>Content-Type: text/html  
>Connection: keep-alive  
>Content-Length: {len(REQUEST_BODY)}  
>  
>{REQUEST_BODY}  

* `METHOD` : `HEAD`, `GET`, `POST`, `PUT` 중 하나
* `PATH` : `HEAD`와 `GET`은 \*.html 파일의 이름을 받고  
`POST`와 `PUT`은 각각 기본적으로 create와 update를 받으나 혼용 가능하다.
* `REQUEST_BODY` : `POST`, `PUT`을 통해 서버에 생성하고자 하는 데이터.  
`key1=val1&...&key2=val2` 형식으로 작성해야 한다.



## server의 Response 형식
>HTTP/1.1 {code} {status}  
>HOST: {HOST}/{path}  
>Content-Type: text/html  
>Connection: keep-alive  
>Content-Length: {len(body)}  
>DATE: {dateteim.now()}  
>  
>{body}  
* Request의 해석에 따라 다음 중 하나로 `code`와 `status`가 정해진다.
    * `100 CONTINUE`
    * `200 OK`
    * `400 BAD_REQUEST`
    * `404 NOT_FOUND`
    * `405 NOT_ALLOWED_METHOD`
* `HOST` : 현 서버의 IP
* `path` : `request`로 들어온 `path`와 같은 값이다.
* `body` : `HEAD`를 제외한 `request`의 `response`는 해당하는 본문을 `body`로 갖는다.
   * 예시는 [함수 설명](#1-serverpy) 참조



## 구현가능한 Method와 응답
client에서 `method`, `path`, `body`, `IP`를 다음과 같이 입력해서 `request`할 때  
server의 `response` header의 status와 code:  
[결과](#작동예시)
1. `('HEAD', 'dummy.html', '', IP)` : `100 CONTINUE`
2. `('GET ', 'dummy.html', '', IP)` : `200 OK`
3. `('POST', 'create', '', IP)` : `100 CONTINUE` → `client`에서 `key=val` 입력 다시 받고 `200 OK`
4. `('POST', 'create', 'User-ID=K2022031&Grade=F', IP)` : `200 OK`
5. `('PUT' , 'update', 'Grade=A+&Major=Artificial Intelligence', IP)` : `200 OK`
6. `('GET' , 'dummy.html', '', IP)` : `200 OK`
---
7. `('HEAD', 'dummy.html', '', '1.1.1.1')` : `400 BAD_REQUEST`
8. `('GET' , 'foo.exe', '', IP)` : `405 METHOD_NOT_ALLOWED`
9. `('HEAD', 'foo.html', '', IP)` : `404_NOT_FOUND`
10. `('FOO' , 'dummy.html', '', IP)` : `405 METHOD_NOT_ALLOWED`
11. `('PUT' , 'foo', '', IP)` : `405 METHOD_NOT_ALLOWED`
---
12. `('POST', 'create', 'Grade=B', IP)` : `400 BAD_REQUEST`
13. `('POST', 'create', '', IP)` : `400 BAD_REQUEST`
---
14. `('END', '' , '', IP)` → client와 server 종료



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
    - `root_dir` : \*.html 파일 저장되어 있는 곳 (=cmd로 python 실행시키는 폴더)
    - `HOST`, `IP`, `PORT` : server 주소
    - `DB` : `POST`, `PUT` request를 통해 서버에 저장된 데이터
    - `POST_continue` : `POST 100`이 발생했을 때 server가 기존 client와 연결을 유지하고 있게 하기 위함
    - `STATUS` : `status_code`와 `status_statement`를 묶어놓은 dictionary
    ```python
   root_dir = "D:/ComputerNetwork/"
   HOST = 'localhost'
   IP = '127.0.0.1' if HOST == 'localhost' else HOST
   PORT = 8080
   DB = {}
   POST_continue = False
   STATUS = {100:'CONTINUE', 200:'OK',
             400:'BAD_REQUEST', 404:'NOT_FOUND', 405:'METHOD_NOT_ALLOWED'}
    ```
3. Request 처리
    - HTTP protocol로 들어온 request를 해석하고 적절한 response 반환
    - 첫 번째 `if` 문 : `method` 확인
    - 두 번째 `if-else` 문 : `url`의 형식 확인
    - 세 번째 `if-else` 문 : request로 들어온 `host` 확인
    - 네 번째 `if-else` 문 : `path` 확인
    - 다섯 번째 `if-else` 문 : \*.html 파일이 제대로 읽히는 지 확인
    - 여섯 번째 `if-elif` 문 : `HEAD`와 `GET` method 구분하여 response 반환
    - 일곱 번째 `if-elif` 문 : `POST`와 `PUT` method 구분하여 response 반환
    ```python
      def from_request_to_response(method, url, request_body):
          if method not in ["HEAD", "GET", "POST", "PUT"]:
              body = f"NOT ALLOWED METHOD: {method}"
              response = response_formatting(405, url.split('/')[1][:-1], body)
              response += body

          if '/' in url:

              host, path = url.split('/')
              path = path[:-1]
              
              if host == IP:
              
                  if 'html' in path:
                      body = open_html(path)
                      
                      if body == None:
                          body = f"CANNOT FIND {path}"
                          response = response_formatting(404, path, body)
                          response += body
                          
                      else:
                          if   method == "HEAD": response = HEAD(path, body)
                          elif method == "GET" : response =  GET(path, body)
                          
                  elif (path == 'create') or (path == 'update'):
                      if   method == "POST": response = POST(path, request_body)
                      elif method == "PUT" : response =  PUT(path, request_body)

                  else:
                      body = f"NOT ALLOWED PATH: {path}"
                      response = response_formatting(405, path, body)
                      response += body

              else:
                  body = f"DIFFERENT HOST: {host}"
                  response = response_formatting(400, path, body)
                  response += body

          else:
              body = f"WRONG ADDRESS: {url}"
              response = response_formatting(404, "?", body)
              response += body

          return response
    ```
4. response 작성
    * 모든 `response`는 [언급했듯](#server의-response-형식) 아래의 format을 따릅니다.
    ```python
      def response_formatting(code, path, body=''):
      
          return f'''\
      HTTP/1.1 {code} {STATUS[code]}\r
      Host: 127.0.0.1/{path}\r
      Content-Type: text/html\r
      Connection: keep-alive\r
      Content-Length: {length}\r
      DATE: {datetime.now().strftime("%a, %d %b %Y %H:%M:%S KST")}\r\n\n'''
    ```
5. Method function
    * Method에 따른 response를 반환합니다.
    * `HEAD` : `100 CONTINUE`를 헤더로 \*.html 본문의 길이를 포함하여 반환합니다.
        ```python
        def HEAD(path, body):
            response = response_formatting(100, path, body)

            return response
        ```
    * `GET` : `200 OK`를 헤더로 \*.html 본문의 길이를 포함하며, 본문을 `body`로 반환합니다.  
추가로 `DB`에 데이터가 있다면 같이 `body`로 반환합니다.
        ```python
        def GET(path, body):
            if DB:
                body += "\nData in DB (created by POST/PUT):\r\n"
                for key in DB:
                    body += f"\t{key}:{DB[key]}\r\n"
            body = body[:-2]

            response = response_formating(path, body)
            response += body

            return response
        ```
    * `POST` : `request_body`가 없으면 `100 CONTINUE`를, 있으면 `200 OK`를 헤더로 하며 추가된 데이터를 `body`로 반환합니다.
        ```python
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

                  else:
                      body = f"ALREADY EXIST KEY: {key}"
                      response = response_formatting(400, path, body)
                      response += body
                      return response
                      
              body = "post OK "
              request_body.replace('&', '/')
              request_body.replace('=', ':')
              body += f"{request_body}"

              response = response_formatting(200, path, body)
              response += body

          return response
        ```
    * `PUT` : `request_body`가 없으면 `400 BAD REQUEST`를, 있으면 `200 OK`를 헤더로 하여 추가/업데이트된 데이터를 `body`로 반환합니다.
        ```python
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
7. 서버 생성
    * Variable에서 지정해둔 `HOST`와 `PORT`를 주소로 TCP 서버를 만듭니다.
        ```python
        server_socket = socket(AF_INET, SOCK_STREAM)
        server_socket.bind( (HOST, PORT) )
        server_socket.listen()
        ```
8. client와 통신(1) - accept
    * client의 connection을 기다렸다가 (`while True`) accept합니다.
    * `POST 100 CONTINUE`가 발생한 경우 새로 connection을 요청하는 client가 나오지 않기 때문에 accept을 스킵합니다.
        ```python
            if not POST_continue:
                client_socket, address = server_socket.accept()
        ```
9. client와 통신(2) - receive request
    * client의 request를 수신합니다.
        ```python
            request = client_socket.recv(65535).decode('utf-8')
        ```
10. client와 통신(3) - request 해석, response 반환
    * request를 적절히 분해 후 `from_request_to_response` 함수로 적절한 response를 만듦니다.
    * `if`문은 client에서 'END'를 보낼 경우 server를 끄기 위한 부분입니다.
        ```python
            if 'END' in request: break

            request = request.split('\n')

            method = request[0].split()
            method = method[0]
            url = request[1][6:]
            request_body = request[-1]

            response = from_request_to_response(method, url, request_body)
        ```
11. client와 통신(4) - response 보내기
      * 그렇게 만들어진 response를 client에게 보냅니다.
      * 만약 `POST 100 CONTINUE`인 경우 accept을 스킵하기 위해 `POST_continue`변수를 변경합니다.
        ```python
            client_socket.sendall(response.encode('utf-8'))
            POST_continue = 'What do you want to' in response.split('\n')[-2]
        ```
12. 종료
      * `while True`가 끝나면 client와 server를 종료합니다.
      ```python
      client_socket.close()
      server_socket.close()      
      ```



### 2. [client.py](https://github.com/Syzseisus/ComputerNetwork/blob/main/MidTerm_Replace_HW/my_client.py)
1. `import`
    * 소켓 통신을 위한 `socket`
        ```python
        from socket import *
        ```
2. 변수
    * `IP`, `PORT` : 연결하고자 하는 서버의 주소입니다.
        ```python
        IP = '127.0.0.1'
        PORT = 8080
        ```
3. Test Case
   * 설정해둔 `test_case`를 바탕으로 통신을 진행합니다.
   * [여기](#구현가능한-method와-응답)에 나와있는 순서와 같습니다.
      ```python
      test_case = [
          ('HEAD', 'dummy.html', '', IP),
          ('GET ', 'dummy.html', '', IP),
          ('POST', 'create', '', IP),
          ('POST', 'create', 'User-ID=K2022031&Grade=F', IP),
          ('PUT' , 'update', 'Grade=A+&Major=Artificial Intelligence', IP),
          ('GET' , 'dummy.html', '', IP),
          ('HEAD', 'dummy.html', '', '1.1.1.1'),
          ('GET' , 'foo.exe', '', IP),
          ('HEAD', 'foo.html', '', IP),
          ('FOO' , 'dummy.html', '', IP),
          ('PUT' , 'foo', '', IP),
          ('POST', 'create', 'Grade=B', IP),
          ('PUT' , 'create', '', IP),
          ('END', '' , '', IP)
      ]
      ```
5. request 작성
    * `test_case`에서 가져온 `method`, `url`, `body`, `IP`를 바탕으로 [언급했던 양식으로](#client의-request-) request를 작성합니다. 
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
6. request 작성
    * `tes_case`를 이용해 request를 작성합니다.
    * `method`에 END가 들어올 경우 `while True`를 빠져나옵니다.
        ```python
          method, path, body, target = test_case[test]
          if method == 'END': 
              request = 'END'
              client_socket.sendall(request.encode('utf-8'))
              break
          else:
              request = request_formatting(method, path, body, target)
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
    * response로 `POST 100 CONTINUE`가 오면 `request_body`를 다시 설정하여
    * request를 다시 만들어서 전송하고,
    * response를 수신합니다.
        ```python
            if 'What do you want to' in response.split('\n')[-2]:
                while True:
                    body = 'User-Affiliation=KMU'
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
server에서 request를 볼 수 있고,  
client에서 response를 볼 수 있습니다.
1. `('HEAD', 'dummy.html', '', IP)` : `100 CONTINUE`  
   * server :  
      ![server_1](https://user-images.githubusercontent.com/83002480/165908549-b365a88a-a311-410f-aba6-5b158efed544.png)  
   * client :  
      ![client_1](https://user-images.githubusercontent.com/83002480/165907956-c745fe06-39dd-45e9-a284-f643a56c0167.png)  
2. `('GET ', 'dummy.html', '', IP)` : `200 OK`  
   * server :  
      ![server_2](https://user-images.githubusercontent.com/83002480/165908576-3edb5449-5883-485a-876e-83d4d2aa368d.png)  
   * client :  
      ![client_2](https://user-images.githubusercontent.com/83002480/165908027-37d4f2b5-bb64-4d99-b959-aee49bf61657.png)  
3. `('POST', 'create', '', IP)` : `100 CONTINUE` → `client`에서 `key=val` 입력 다시 받고 `200 OK`    
   * server :  
      ![server_3](https://user-images.githubusercontent.com/83002480/165908669-0676d2fe-3e10-45e7-a0e3-d0917f4f3f99.png)  
   * client :  
      ![client_3](https://user-images.githubusercontent.com/83002480/165908091-61ca0d0e-8d4b-4fbe-99fb-ff4f7bf769e1.png)  
4. `('POST', 'create', 'User-ID=K2022031&Grade=F', IP)` : `200 OK`  
   * server :  
      ![server_4](https://user-images.githubusercontent.com/83002480/165908711-89b6bb0f-7bc8-4099-9e00-9017a76151af.png)  
   * client :  
      ![client_4](https://user-images.githubusercontent.com/83002480/165908117-b4822863-6aca-4771-83ff-c3eebc2d7b67.png)  
5. `('PUT' , 'update', 'Grade=A+&Major=Artificial Intelligence', IP)` : `200 OK`  
   * server :  
      ![server_5](https://user-images.githubusercontent.com/83002480/165908754-bade0867-b494-48de-a591-a23fccdaad6d.png)  
   * client :  
      ![client_5](https://user-images.githubusercontent.com/83002480/165908161-da1d4787-c5d0-4521-a1be-320f2c659df1.png)  
6. `('GET' , 'dummy.html', '', IP)` : `200 OK`  
   * server :  
      ![server_6](https://user-images.githubusercontent.com/83002480/165908796-cd5b86d7-6055-44b1-a4be-babdb1510eca.png)  
   * client :  
      ![client_6](https://user-images.githubusercontent.com/83002480/165908215-53e371b2-4e87-48be-8162-a75e201e4202.png)  
---
7. `('HEAD', 'dummy.html', '', '1.1.1.1')` : `400 BAD_REQUEST`  
   * server :  
      ![server_7](https://user-images.githubusercontent.com/83002480/165908841-72d67f40-bcad-45af-9d4b-a5386c322a0b.png)  
   * client :  
      ![client_7](https://user-images.githubusercontent.com/83002480/165908240-78fd3bbc-d491-4f96-9e2e-a0273d10b001.png)  
8. `('GET' , 'foo.exe', '', IP)` : `405 METHOD_NOT_ALLOWED`  
   * server :  
      ![server_8](https://user-images.githubusercontent.com/83002480/165908878-edeb16d6-cc32-4f75-896e-e6cf6a74be30.png)  
   * client :  
      ![client_8](https://user-images.githubusercontent.com/83002480/165908256-d68eed5a-cd0a-44d3-b358-65ef68243e27.png)  
9. `('HEAD', 'foo.html', '', IP) : `404_NOT_FOUND`  
   * server :  
      ![server_9](https://user-images.githubusercontent.com/83002480/165908903-5c018879-7281-466c-9989-f504cdbde36d.png)  
   * client :  
      ![client_9](https://user-images.githubusercontent.com/83002480/165908279-613582c4-9745-4013-8922-38564bfa56f1.png)  
10. `('FOO' , 'dummy.html', '', IP)` : `405 METHOD_NOT_ALLOWED`
      * server :  
      ![server_10](https://user-images.githubusercontent.com/83002480/165908923-e5a43371-bfb8-4abd-8a6c-5557598aef1e.png)  
      * client :  
      ![client_10](https://user-images.githubusercontent.com/83002480/165908311-961c6bc0-5d69-499a-8041-c03ee38f3cfa.png)  
11. `('PUT' , 'foo', '', IP)` : `405 METHOD_NOT_ALLOWED`  
      * server :  
      ![server_11](https://user-images.githubusercontent.com/83002480/165908948-fc988fda-c040-4ff9-a7de-7f4851d4876d.png)  
      * client :  
      ![client_11](https://user-images.githubusercontent.com/83002480/165908341-d427be7a-4d52-47c7-b72d-223cd43f94e0.png)  
---
12. `('POST', 'create', 'Grade=B', IP)` : `400 BAD_REQUEST`  
      * server :  
      ![server_12](https://user-images.githubusercontent.com/83002480/165908963-285a81bb-a52d-4a66-96f0-8d9db27d12c2.png)  
      * client :  
      ![client_12](https://user-images.githubusercontent.com/83002480/165908363-85a82d23-38ab-4ae1-a2e1-4fd94496f9d1.png)  
13. `('POST', 'create', '', IP)`: `400 BAD_REQUEST`  
      * server :  
      ![server_13](https://user-images.githubusercontent.com/83002480/165908999-e94ca8e4-d878-4767-b370-f73ff80b63ea.png)  
      * client :  
      ![client_13](https://user-images.githubusercontent.com/83002480/165908404-8e1a2f19-fe8c-4816-9a6a-4f32e7ba1b01.png)  
---
14. `('END', '' , '', IP)` → `client`와 `server` 종료  
      * server :  
      ![server_14](https://user-images.githubusercontent.com/83002480/165909033-87f21cbf-5c40-47f0-800b-f333836a5c67.png)  
      * client :  
      ![client_14](https://user-images.githubusercontent.com/83002480/165908431-73619548-e39a-4cbe-8697-e40b4a86b122.png)  



## WireShark로 캡쳐한 통신
   ![WireShark](https://user-images.githubusercontent.com/83002480/165909676-5cafd415-6817-4a1b-be47-2a3f1d6e0877.png)
