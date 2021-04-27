# ServerDNS
Desarrollado con los siguientes requisitos 🛠️:
* Entrega el día 3 de Mayo de 2021 a las 11:00AM
Desarrollarlo en C/C++ sobre GNU/Linux.
* El DNS server debe ser estándar (RFC1035).
* Se requiere únicamente la conversión de nombres a direcciones IP sobre el protocolo de transporte UDP.
* El servidor debe estar en capacidad de responder simultáneamente a múltiples solicitudes DNS por parte de los clientes.
* El servidor DNS debe poder resibir Query y Responder con un Query Response.

## Instalación en GNU/Linux

### Abre la Terminal

_Luego accede a la carpeta serverDNS con el siguiente comando:_
```
cd serverDNS
```
_Luego ejecuta usando super usuario:_
```
sudo python3 main.py
```
Listo, ahora el servidor esta en espera de datos para procesar y responder.
* Abre otra terminar ya sea en el mismo computador o uno en la red LAN
_Ejeuta comando dig en el localhost si es el caso o la ip privada_
```
dig javeriana.edu.co @localhost
```
Fin..

## License
[GPL v3](https://choosealicense.com/licenses/gpl-3.0/)
 
