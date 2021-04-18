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
void respondQuery(char data);

int main(){

  int udpSocket, serverLength, fromClientLength, dataGram;
  struct sockaddr_in server, fromClient;
  char buffer[512]; // UDP messages 512 octets or less
  
  /*Create UDP socket*/
  udpSocket = socket(AF_INET, SOCK_DGRAM, 0);
  if(udpSocket < 0){printError("Opening Socket");}

  serverLength = sizeof(server);
  bzero(&server, serverLength);

  /*Configuration Server*/
  server.sin_family = AF_INET;//IP v4
  server.sin_addr.s_addr = INADDR_ANY; // 127.0.0.1
  server.sin_port = htons(5553); // Puerto 53

  if(bind(udpSocket, (struct sockaddr * )&server, serverLength) < 0){
    printError("Binding");
  }

  fromClientLength = sizeof(struct sockaddr_in);

  while (1){
    dataGram = recvfrom(udpSocket,buffer,512,0,(struct sockaddr *) &fromClient, &fromClientLength);
    if(dataGram<0){ printError(" ReciviendoDatagramCLiente");}

    printf("Datagram del Cliente:\n");
    /*printf(buffer);*/
    write(1,buffer,dataGram);

    //Funcion DNS QueryResponds

    dataGram = sendto(udpSocket,"Recived Your DataGram\n",22,0,(struct sockaddr *) &fromClient, fromClientLength);
    if (dataGram < 0){ printError(" EnviandoQueryRespond");}
  }
}

void printError(char *messageError){
      perror(messageError);
      exit(0);
}

void respondQuery(char data){

  //Get the transaction ID

  //Get the Flags

  //
  

}