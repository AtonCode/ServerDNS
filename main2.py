'''
Licencia GPL v3
Autores: Alejandro Sacristan Leal & Camilo Jose Narvaez Montenegro & Loui Gerald Quintero & Juan Pablo Urrego
Materia: Comunicación y Redes
Universidad: Pontificia Universidad Javeriana de Bogotá Colombia
Semestre: 2021-10
Desarrollo: Servidor DNS con MasterFile solo tipo A  y Foreing Resolver
Fecha de Entrega: 2/5/2021

'''

import socket, glob, json

# Estandar DNS
LocalHost = '192.168.13.102' # Local Host
OpenDNS = '208.67.220.220' # IP de OpenDNS
DNSPort = 53 # Puerto DNS estandar
SIZE = 512 # Mensajes UDP de 512 octetos or lees
foreingResolverAddress = (OpenDNS, DNSPort) # Datos de Servidor DNS Amigo


# Creando y Configurando Servidor UDP
udpServerSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udpServerSocket.bind((LocalHost, DNSPort))

# Cargar Zonas para respuesta Autoritativa del MasterFile
def getMasterFile():
    jsonZona = {}
    zonaFile = glob.glob('MasterFile/*.zona')
    
    for zona in zonaFile:
        with open(zona) as MaterFileData:
            data = json.load(MaterFileData)
            zonaName = data["$origin"]
            jsonZona[zonaName] = data

    return jsonZona

MaterFileData = getMasterFile()

def searchDomineMasterFiles(domainName):
    try:

        global MaterFileData
        zonaName = '.'.join(domainName)
        return MaterFileData[zonaName]

    except KeyError:
        return False


# Edit Flags
def hackFlags(flags):

    # Byte Uno
    byteUNO = bytes(flags[:1])
    QR = '1'
    Opcode = ''
    AA = '1' # Respuesta Autoritativa
    TC = '0'
    RD = '0'

    for bit in range(1,5):
        Opcode += str(ord(byteUNO)&(1<<bit))


    # Byte Dos
    byteDOS = bytes(flags[1:2])
    RA = '0'
    Z = '000'
    RCODE = '0000'

    # Uniendo las Partes que componen el flag y conviertiendolas a bytes
    newFlags = (int(QR+Opcode+AA+TC+RD, 2).to_bytes(1, 'big')) + (int(RA+Z+RCODE, 2).to_bytes(1, 'big'))

    return  newFlags

def dsnQuestionToBytes(domainName, tipo):
    dsnQuestionInBytes = b''

    for part in domainName:
        lenght = len (part)
        dsnQuestionInBytes += bytes([lenght])

        for char in part:
            dsnQuestionInBytes += ord(char).to_bytes(1, 'big')
    if tipo == 'a':
        dsnQuestionInBytes += (1).to_bytes(2,'big')
    dsnQuestionInBytes += (1).to_bytes(2,'big')

    return dsnQuestionInBytes



# Query section
def queryQuestionDomain(dataGram):

    aux = 0
    auxTwo = 0
    flag = 0
    dataLeng = 0
    domainNameChar = ''
    domainName = []

    for byte in dataGram:
        if flag == 1:
            if byte != 0:
                domainNameChar += chr(byte)
            aux +=1
            if aux == dataLeng:
                domainName.append(domainNameChar)
                domainNameChar = ''
                flag = 0
                aux = 0
            if byte == 0:
                domainName.append(domainNameChar)
                break
        else:
            flag = 1
            dataLeng = byte
        
        auxTwo += 1
    questionType = dataGram[auxTwo:auxTwo+2]


    return (domainName, questionType)


def searchTypeADominesMasterFiles(dataGram):

    domainName, questionType = queryQuestionDomain(dataGram)
    questionTypeChar = ''
    if questionType == b'\x00\x01':
        questionTypeChar = 'a'

    zona = searchDomineMasterFiles(domainName)

    return (zona[questionTypeChar], questionTypeChar, domainName)

def booleanFindZone(dataGram):

    domainName, questionType = queryQuestionDomain(dataGram[12:])
    questionTypeChar = ''
    if questionType == b'\x00\x01':
        questionTypeChar = 'a'

    zona = searchDomineMasterFiles(domainName)

    if zona == False:
        return True
    else:
        return False
         
    

def convertDNSbodyTObytes(domainname, questionTypeChar, ttl, value):
    DNSbody = b'\xc0\x0c'
    if questionTypeChar == 'a':
        DNSbody = DNSbody + bytes([0]) + bytes([1])
        DNSbody = DNSbody + bytes([0]) + bytes([1])
        DNSbody += int(ttl).to_bytes(4, byteorder='big')
    if questionTypeChar == 'a':
        DNSbody = DNSbody + bytes([0]) + bytes([4])
        for part in value.split('.'):
            DNSbody += bytes([int(part)])
    return DNSbody

# Domain Name System Query
def makeQueryRespondDNS(dataGram):

    errorNotFindZone = booleanFindZone(dataGram)
    if errorNotFindZone == False:
        
        TansactionID = dataGram[:2]
        TransactionIDHex = ''
        for byte in TansactionID:
            TransactionIDHex += hex(byte)[:2]

        Flags = hackFlags(dataGram[2:4])

        QDCOUNT = b'\x00\x01'

        ANCOUNT = len(searchTypeADominesMasterFiles(dataGram[12:])[0]).to_bytes(2,'big')
    
        NSCOUNT = (0).to_bytes(2, 'big')
        ARCOUNT = (0).to_bytes(2, 'big')

        DNSheader = TansactionID + Flags + QDCOUNT + ANCOUNT + NSCOUNT + ARCOUNT
    
        DNSbody = b''
        zonaMasterfile, questionTypeChar, domainName = searchTypeADominesMasterFiles(dataGram[12:])
    
        dsnQuestion = dsnQuestionToBytes(domainName, questionTypeChar)

        for zona in zonaMasterfile:
            DNSbody += convertDNSbodyTObytes(domainName, questionTypeChar, zona["ttl"], zona["value"])
        
        QueryRespond =  DNSheader + dsnQuestion + DNSbody
    
    else:
        QueryRespond  = False

    
    return QueryRespond

    
# Guarda todas las peticiones DNS que se han enviado a foreingResolver
def cacheWrite(queryRespondDNSFriend, queryQuestion):

    domainName, domineType = getQuestionDomain(queryQuestion)

    try:
        flow = open('zones/cache.txt','a')
        flow.write(str(domainName,'UTF-8'))
        flow.write('\n')
        flow.write(str(domineType,'UTF-8'))
        flow.write('\n')
        flow.write(str(queryRespondDNSFriend))
        flow.write('\n')
        flow.close()

    except FileNotFoundError:
        print('Archivo no encontrado:')
        exit()


# Cliente UDP send queryAsk from original cliente to OpenDNS and return the queryResponds of OpenDNS
def foreingResolver(dataGramFromFriendDNS,addrCliente):
    
    # Creando Nuevo UDP Socket
    UDPSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Enviando datagrama del cliente a OpenDNS
    UDPSocket.sendto(dataGramFromFriendDNS, foreingResolverAddress)

    # Resibiendo QueryRespond del OpenDNS
    queryRespondDNSFriend, addrDNSfriend = UDPSocket.recvfrom(SIZE)

    # Enviando datagrama del cliente a OpenDNS
    UDPSocket.sendto(queryRespondForeginResolver, addrCliente)

    # Retornando Datagrama de OpenDNS    
    return queryRespondDNSFriend

# Servidor DNS
try:
    
    while True:
        print("Running...")

    # 1 Configurando Servidor UDP para la recepcion de datagramas UDP no mas de 512 octetos
        dataGram1, addrCliente = udpServerSocket.recvfrom(SIZE)
        print("Query Recibido Cliente ")
        print(addrCliente)
        print(dataGram1)
        print(" ")
        
        queryRespondForeginResolver = foreingResolver(dataGram1, addrCliente)
        print("Query Enviado Cliente desde ForeginResolver ")
        print(addrCliente)
        print(queryRespondForeginResolver)
        
        print(" ")
        print("---------------------------")
        print("Esperando mas Datagramas...")
        print("---------------------------")
        print(":)")
        print(" ")
        

        
        
    
except KeyboardInterrupt:
    udpServerSocket.close()
    print(" ")
    print(" ")
    print(' Adios Amigo Que la Fuerza te Acompañe...')
    print(" :)")
    print(" ")
    