# HeadHunter vacancies parser

## Description

Simple microservice for parsing HeadHunter website one time a week and store URLs of new vacancies for each word 
combination for search.

After storing vacancies the microservice build the top of employers by vacancies per week for each word combination for
search and send message in Slack with new vacancies count.

## Running

### Preparation

To run this microservice you need to install Docker and Docker Compose. For Windows and Max OS Docker Compose goes 
with Docker by default.

With Linux OS you need to install Docker Compose by yourself and do some post-installation steps.

- Windows https://docs.docker.com/docker-for-windows/install/

- Max https://docs.docker.com/docker-for-mac/install/

- Linux
    1) Docker https://docs.docker.com/install/linux/docker-ce/ubuntu/

    2) Post-installation steps for Linux https://docs.docker.com/install/linux/linux-postinstall/

    3) Docker Compose https://docs.docker.com/compose/install/

After installation of Docker and Docker Compose you need to build the microservice image. For this purpose enter next
command in your ```Terminal``` or ```Command Prompt```:

```shell script
docker build -t worker:latest .
```

### Running

To run microservice, enter next command in your ```Terminal``` or ```Command Prompt```:

```shell script
docker-compose up
```

To run microservice in detached (background) mode, enter next command in your ```Terminal``` or ```Command Prompt```:

```shell script
docker-compose up -d
```

To bring down Docker Compose containers of microservice and the associated volumes, you need to enter next command 
in your ```Terminal``` or ```Command Prompt```:

```shell script
docker-compose down -v
```
