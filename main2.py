
'''
Licencia GPL v3
Autores: Alejandro Sacristan Leal & Camilo Jose Narvaez Montenegro & Loui Gerald Quintero & Juan Pablo Urrego
Materia: Comunicación y Redes
Desarrollo: Servidor DNS
Fecha de Entrega: 2/5/2021
'''

import socket, glob, json

# Estandar DNS
LocalHost = '192.168.13.102' #Local Host
OpenDNS = '208.67.220.220' # IP de OpenDNS
DNSPort = 53 # Puerto DNS estandar
SIZE = 512 # Mensajes UDP de 512 octetos or lee
serverDNSAddressPort = (OpenDNS, DNSPort) # Datos de Servidor DNS Amigo

# Creando y Configurando Servidor UDP
udpServerSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udpServerSocket.bind((LocalHost, DNSPort))



# Cliente UDP send queryAsk from original cliente to OpenDNS and return the queryResponds of OpenDNS
def foreingResolver(dataGramFromFriendDNS, serverDNSAddressPort):
    
# Creando Nuevo UDP Socket
    UDPSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Enviando datagrama del cliente a OpenDNS
    UDPSocket.sendto(dataGramFromFriendDNS, serverDNSAddressPort)
    queryRespondDNSFriend, addrDNSfriend = UDPSocket.recvfrom(512)

#Retornando Datagrama de OpenDNS    
    return queryRespondDNSFriend



# Servidor DNS
try:
    while True:
        print("Dancing...")

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
    