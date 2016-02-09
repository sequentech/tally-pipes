# agora-results-tests

En este repositorio, se irá almacenando todas la codificación relacionada con la creación de tests unitarios para las funcionalidades del módulo Agora-Results del proyecto open soure Agora-Voting.


## A tener en cuenta - Entorno virtual

Para que funcionen los tests se debe de estar seguro que se está en el entorno virtual de Agora Results.

Este entorno virtual se puede instalar desde la guía documentada en la propia Agora Results de Agora Voting

Para activar el entorno virtual deseado solo es necesario ejecutar el siguiente comando:

```sh
$ workon nombre_entorno
```

## Instalación de Agora Results Tests

Si se desea crear un nuevo entorno virtual y hacer una instalación desde cero se tiene que seguir este procedimiento para la instalación:

El primer paso es crear ese entorno virtual y trabajar bajo él, esto se puede hacer con el comando

```sh
$ mkvirtualenv nombre_entorno
```

El segundo paso es clonar el proyecto con Git (la ruta del proyecto fue proporcionada por el equipo de trabajo).Una vez hecho esto, debemos situarnos con una terminal en la carpeta creada y ejecutar un archivo Shell:

```sh
$ sh install_agora_results_tests.sh
```

Con este Shell se instalarán en el entorno virtual todas las dependencias y el proyecto agora results, ademas de instalar y configurar pybuilder. Despues de esto solo haría falta ejecutar el proyecto. 

## Uso

Para ejecutar los test se debe de usar el siguiente comando

```sh
$ pyb
```

Para poder visualizar mejor los errores que pudieran haber se usa el siguiente comando

```sh
$ pyb -v
```
