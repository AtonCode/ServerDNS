'''
Licencia GPL v3
Autores: Alejandro Sacristan Leal & Camilo Jose Narvaez Montenegro & Loui Gerald Quintero & Juan Pablo Urrego
Materia: Comunicación y Redes
Desarrollo: Servidor DNS
Fecha de Entrega: 2/5/2021

'''

import socket, glob, json, codecs

# Estandar DNS
LocalHost = '127.0.0.1' #Local Host
OpenDNS = '208.67.220.220' # IP de OpenDNS
DNSPort = 53 # Puerto DNS estandar
SIZE = 512 # Mensajes UDP de 512 octetos or lee
serverDNSAddressPort = (OpenDNS, DNSPort) # Datos de Servidor DNS Amigo

# Creando y Configurando Servidor UDP
udpServerSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udpServerSocket.bind((LocalHost, DNSPort))

# Edit Flags
def hackFlags(flags):

    # Byte Uno
    byteUNO = byte(flags[:1])
    QR = '1'
    Opcode = ''
    AA = '1' # Respuesta Autoritativa
    TC = '0'
    RD = '0'

    for bit in range(1,5):
        Opcode += str(ord((byteUNO)&(1<<bit)))


    # Byte Dos
    byteDOS = byte(flags[1:2])
    RA = '0'
    Z = '000'
    RCODE = '0000'

    # Uniendo las Partes que componen el flag y conviertiendolas a bytes
    newFlags = (int(QR+Opcode+AA+TC+RD, 2).to_bytes(1, byteorder='big')) + (int(RA+Z+RCODE, 2).to_bytes(1, byteorder='big'))

    return  newFlags



# Domain Name System Query
def makeQueryRespondDNS(dataGram):

    TansactionID = dataGram[:2]
    TransactionIDHex = ''
    for byte in TansactionID:
        TransactionIDHex += hex(byte)[:2]

    Flags = hackFlags(dataGram[2:4])



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
def foreingResolver(dataGramFromFriendDNS, serverDNSAddressPort):
    
    # Creando Nuevo UDP Socket
    UDPSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Enviando datagrama del cliente a OpenDNS
    UDPSocket.sendto(dataGramFromFriendDNS, serverDNSAddressPort)
    queryRespondDNSFriend, addrDNSfriend = UDPSocket.recvfrom(SIZE)

    # Guardando queryRespond en Cache.txt
    #cacheWrite(queryRespondDNSFriend, dataGramFromFriendDNS)

    #Retornando Datagrama de OpenDNS    
    return queryRespondDNSFriend



# Servidor DNS
try:
    while True:

    # 1 Configurando Servidor UDP para la recepcion de datagramas UDP no mas de 512 octetos
        dataGram1, addrCliente = udpServerSocket.recvfrom(SIZE)

    # 2 Enviando Datagrama a OpenDns y Resiviendo la respuesta
        queryRespond = foreingResolver(dataGram1, serverDNSAddressPort)
        
        print("Query Recibido Cliente ")
        print(addrCliente)
        print(dataGram1)
        print(" ")
   
    # 3 Enviando el query Responds al mismo cliente
        udpServerSocket.sendto(queryRespond, addrCliente)
        print("Query Enviado Cliente ")
        print(addrCliente)
        print(queryRespond)
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
    
