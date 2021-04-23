/*
Licencia GPL v3
Autores: Alejandro Sacristan Leal & Camilo Jose Narvaez Montenegro & Loui Gerald Quintero
Materia: Comunicación y Redes
Desarrollo: Servidor DNS
Fecha de Entrega: 2/5/2021
*/

/************* DNS SERVER CODE *******************/
/************* UDP SERVER CODE *******************/

#include <stdio.h>
#include <iostream>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#include <netdb.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <netinet/in.h>


#define portDNS 53
#define UDPmessagesSize 512

void respondQuery(char* data); // Manejo de datos del Datagrama

char* servidorUDP(){

  int udpSocket, n; // Variables auxiliales
  socklen_t fromClientLength, serverLength;
  struct sockaddr_in serverAddr, fromClientAddr; // Sockets for server and client
  struct hostent *hostClient; // host del cliente que envia mensajes
  char *hostaddrp;	/* dotted decimal host addr string */
  char *DataGramUDP; // UDP messages 512 octets or less
  
  /*Create UDP socket*/
  udpSocket = socket(AF_INET, SOCK_DGRAM, 0);
  if(udpSocket < 0){std::cout<<"Opening Socket\n";}

  serverLength = sizeof(serverAddr);
  bzero((char *)&serverAddr, sizeof(serverAddr));

  /*Configuration Server*/

  serverAddr.sin_family = AF_INET; // IP v4
  serverAddr.sin_port = htons(53); //Puerto 53
  serverAddr.sin_addr.s_addr = htonl(INADDR_ANY); // 127.0.0.1
  

  if(bind(udpSocket, (struct sockaddr *)&serverAddr, serverLength) < 0){
    std::cout<<"Binding Error\n";
  }

  fromClientLength = sizeof(fromClientAddr);
  DataGramUDP = new char[UDPmessagesSize];

  
  while (1){

    n = recvfrom(udpSocket,DataGramUDP,sizeof(DataGramUDP),0,(struct sockaddr *) &fromClientAddr, &fromClientLength);
    if(n<0){ std::cout<<" No RecibiendoDatagramCLiente";}

    std::cout<<"Datagram del Cliente:\n";
    for(int i = 0; i < 513; i){std::cout<<DataGramUDP[i];}

    //Funcion DNS QueryResponds



    n = sendto(udpSocket, DataGramUDP, n, 0,(struct sockaddr *)&fromClientAddr, fromClientLength);
    if (n  < 0){ std::cout<<"No EnviandoQueryRespond\n";}
  }
  return DataGramUDP;
}

int main(){

  char* DataGramUDP;

  DataGramUDP = servidorUDP();

  return 1;
}