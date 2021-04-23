import socket, glob, json

# Estandar DNS
LocalHost = '127.0.0.1'
OpenDNS = '208.67.220.220'
DNSPort = 53
SIZE = 512 # Mensajes UDP de 512 octetos or lees

# Creando y Configurando Servidor UDP
udpService = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udpService.bind((LocalHost, DNSPort))

# Servidor DNS Amigo
serverDNSAddressPort = (OpenDNS, DNSPort)


# Funcion que carga al sistema de la carpeta zonas todos los archivos .zone
def cargaZonas():

    jsonzone = {}
    zonefiles = glob.glob('zones/*.zone')

    for zone in zonefiles:
        with open(zone) as zonedata:
            data = json.load(zonedata)
            zonename = data["$origin"]
            jsonzone[zonename] = data
    return jsonzone

def getFlags(flags):

    byte1 = bytes(flags[:1])
    byte2 = bytes(flags[1:2])

    rflags = ''
    QR = '1'

    OPCODE = ''
    for bit in range(1,5):
        OPCODE += str(ord(byte1) & (1<<bit))

    AA = '1'
    TC = '0'
    RD = '0'

    # Byte 2
    RA = '0'
    Z = '000'
    RCODE = '0000'

    return int(QR+OPCODE+AA+TC+RD, 2).to_bytes(1, byteorder='big')+int(RA+Z+RCODE, 2).to_bytes(1, byteorder='big')

def getQuestionDomain(data):

    state = 0
    expectedlength = 0
    domainstring = ''
    domainparts = []
    x = 0
    y = 0
    for byte in data:
        if state == 1:
            if byte != 0:
                domainstring += chr(byte)
            x += 1
            if x == expectedlength:
                domainparts.append(domainstring)
                domainstring = ''
                state = 0
                x = 0
            if byte == 0:
                domainparts.append(domainstring)
                break
        else:
            state = 1
            expectedlength = byte
        y += 1

    questiontype = data[y:y+2]

    return (domainparts, questiontype)

# Se Carga las Zonas
zonedata = cargaZonas()

def getzone(domain):
    global zonedata

    zone_name = '.'.join(domain)
    return zonedata[zone_name]

def getrecs(data):
    domain, questiontype = getQuestionDomain(data)
    qt = ''
    if questiontype == b'\x00\x01':
        qt = 'a'

    zone = getzone(domain)

    return (zone[qt], qt, domain)

def buildquestion(domainname, rectype):
    qbytes = b''

    for part in domainname:
        length = len(part)
        qbytes += bytes([length])

        for char in part:
            qbytes += ord(char).to_bytes(1, byteorder='big')

    if rectype == 'a':
        qbytes += (1).to_bytes(2, byteorder='big')

    qbytes += (1).to_bytes(2, byteorder='big')

    return qbytes

def rectobytes(domainname, rectype, recttl, recval):

    rbytes = b'\xc0\x0c'

    if rectype == 'a':
        rbytes = rbytes + bytes([0]) + bytes([1])

    rbytes = rbytes + bytes([0]) + bytes([1])

    rbytes += int(recttl).to_bytes(4, byteorder='big')

    if rectype == 'a':
        rbytes = rbytes + bytes([0]) + bytes([4])

        for part in recval.split('.'):
            rbytes += bytes([int(part)])
    return rbytes

# Funcion que resive el datagrama del cliente y construye el queryRespond
def queryResponse(dataGram):

    # Get Transaction ID
    transactionID = dataGram[:2]
    # Get the flags
    flags = getFlags(dataGram[2:4])
    # Get Question Count
    QDcount = b'\x00\x01'
    # Get Answer Count
    ANScount = len(getrecs(dataGram[12:])[0]).to_bytes(2, byteorder='big')
    # Get NameServer Count
    NScount = (0).to_bytes(2, byteorder='big')
    # Get Additonal Count
    ADDcount = (0).to_bytes(2, byteorder='big')

    # Construyendo el QueryRespond
    # DNS Header
    DNSheader = transactionID + flags + QDcount  + ANScount + NScount + ADDcount
    # DNS body
    DNSbody = b''

    # Resolviendo el Query y extrayendo el dominio y si ip
    records, recType, domainName = getrecs(dataGram[12:])
    DNSquestion = buildquestion(domainName, recType)

    # Si el dominio preguntado por el cliente no se encuentra en el archivo zona
    # Se procede a enviar el datagrama a un servidor DNS amigo para que lo resuelva
    # y nos envie el queryRespond al cual se le extraen los datos y se copia en nuestra
    # carpeta de zona y se envia ese QueryRespond intacto al Cliente.

    # Falta trabajar en eso y eso tendria que ir en este espacio antes de retornar un error

    # Uniendo la respuesta de resolucion de dominio a la estructura QueryRespound
    for record in records:
        DNSbody += rectobytes(domainName, recType, record["ttl"], record["value"])

    return DNSheader + DNSquestion + DNSbody
  

# Main
# Bucle infinito del Servidor DNS
try:
    while 1:

    # 1 Configurando Servidor UDP para la recepcion de datagramas UDP no mas de 512 octetos
        dataGram1, addrCliente = udpService.recvfrom(SIZE)

    # 2 Procesando datagrama y construyedo el queryRespond
        queryRespond = queryResponse(dataGram1)
        print("Query Recibido Cliente ")
        print(addrCliente)
        print(dataGram1)
        print(" ")
   
    # 3 Enviando el query Responds al mismo cliente
        udpService.sendto(queryRespond, addrCliente)
        print("Query Enviado Cliente ")
        print(addrCliente)
        print(queryRespond)
        print(" ")
        print("---------------------------")
        print("Esperando mas Datagramas...")
        print("---------------------------")
        print(":)")
        print(" ")
        
except KeyError:
    print(" ")
    print("Enviando Datagrama a OpenDNS...")
    print(":)")
    print(" ")
    

except KeyboardInterrupt:
    print(" ")
    print(" ")
    print(' Adios Amigo Que la Fuerza te Acompañe...')
    print(" :)")
    print(" ")
    udpService.close()
