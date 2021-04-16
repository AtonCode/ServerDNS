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
#include <stdlib.h>
#include <string.h>

#include <netdb.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <netinet/in.h>

void printError(char *messageError);

int main(){

  int udpSocket, serverLength, fromClientLength, i;
  struct sockaddr_in server, fromClient;
  struct sockaddr_storage serverStorage;
  socklen_t addr_size, client_addr_size;
  char buffer[1024];
  
  /*Create UDP socket*/
  udpSocket = socket(AF_INET, SOCK_DGRAM, 0);
  if(udpSocket < 0){printError("Opening Socket");}

  serverLength = sizeof(server);
  bzero(&server, serverLength);

  /*Configuration Server*/
  server.sin_family = AF_INET;
  server.sin_addr.s_addr = INADDR_ANY;
  server.sin_port = htons(53);

  if(bind(udpSocket, (struct sockaddr * )&server, serverLength) < 0){
    printError("Binding");
  }

  fromClientLength = sizeof(struct sockaddr_in);

}

void printError(char *messageError){
      perror(messageError);
      exit(0);
  }