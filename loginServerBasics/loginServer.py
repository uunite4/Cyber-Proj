import socket
import userDBController as db
import secrets
import string

LOGIN_SERVER_IP = "127.0.0.1"
LOGIN_SERVER_PORT = 8080

def generateToken(length=16):
    alphabet = string.ascii_letters + string.digits
    token = ''.join(secrets.choice(alphabet) for i in range(length))
    return token

def intialize():
    loginSocket = socket.socket()
    loginSocket.bind((LOGIN_SERVER_IP, LOGIN_SERVER_PORT))
    loginSocket.listen()
    return loginSocket

def recieveData(loginSocket):
    (client_socket, client_address) = loginSocket.accept()
    print("Client connected")

    loginData = client_socket.recv(1024).decode()
    return loginData.split("="), client_socket, client_address

def handleLogin(loginData):
    usersDB = db.getAll()["users"]
    for user in usersDB:
        if user["username"] == loginData[0] and user["password"] == loginData[1]:
            # USER EXISTS
            return user["token"]

    return 404

def handleSignup(loginData):
    usersDB = db.getAll()
    if (handleLogin(loginData) == 404):
        # DOESN'T EXIST, CAN ADD
        token = generateToken()
        newUser = {
            "username": loginData[0],
            "password": loginData[1],
            "token": token
        }
        db.writeUser(newUser)
        return token
    else:
        return "ALREADY FOUND"

def sendTokenToLB(token):
    # WE ACTUALLY NEED A CONNECTION HERE BUT BECAUSE
    # WE DONT HAVE A LOAD BALANCER I'M JUST GOING TO RETURN
    # A MADE-UP IP THAT IS SUPPOSE TO BE THE IP OF THE GAME SERVER.
    return "38.97.84.242"


def main():
    loginSocket = intialize()
    loginData, clientSocket, clientAddress = recieveData(loginSocket)
    global userToken
    if (loginData[2] == "LOGIN"):                                   # LOGIN
        userToken = handleLogin(loginData)
        if (userToken == 404):
            pk = "ERROR=ERROR: NO USER FOUND"
            clientSocket.send(pk.encode())
            clientSocket.close()
            return
    else:                                                           # SIGNUP
        userToken = handleSignup(loginData)
        if (userToken == "ALREADY FOUND"):
            pk = "ERROR=ERROR: USER ALREADY FOUND"
            clientSocket.send(pk.encode())
            clientSocket.close()
            return

    # NOW WE GOT THE TOKEN (WHETHER WE CREATED A NEW USER OR JUST AUTHENTICATED THEM)
    gameServerIP = sendTokenToLB(userToken)
    pk = "OK=" + userToken + "=" + gameServerIP
    clientSocket.send(pk.encode())
    clientSocket.close()

if __name__ == "__main__":
    main()