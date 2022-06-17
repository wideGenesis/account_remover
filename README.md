## Деплой

sudo docker build --no-cache -t mycintainerregistry.azurecr.io/account_remover:latest .

sudo docker run -d --name account_remover -p 50500:8000 \
        mycintainerregistry.azurecr.io/account_remover:latest

sudo docker run -it --name account_remover -p 50500:8000 \
        mycintainerregistry.azurecr.io/account_remover:latest /bin/bash

sudo docker exec -it account_remover bash

When running in Azure Web App consider increasing WEBSITES_CONTAINER_START_TIME_LIMIT up to 600-1200.
Also only 1 worker must be running in container in Azure.


## Technology stack

**Back-end**

![Python](https://img.shields.io/badge/-Python-black?style=flat-square&logo=Python)
![FastAPI](https://img.shields.io/badge/-FastAPI-%2300C7B7?style=flat-square&logo=FastAPI)
![ORMAR](https://img.shields.io/badge/-ORMAR-DD0031?style=flat-square&logo=ORMAR)
![SqlAlchemy](https://img.shields.io/badge/-SqlAlchemy-FCA121?style=flat-square&logo=SqlAlchemy)

**Databases**

![Postgresql](https://img.shields.io/badge/-Postgresql-%232c3e50?style=flat-square&logo=Postgresql)
![Redis](https://img.shields.io/badge/-Redis-FCA121?style=flat-square&logo=Redis)

**Tools**

![Docker](https://img.shields.io/badge/-Docker-46a2f1?style=flat-square&logo=docker&logoColor=white)
![IntelliJ](https://img.shields.io/badge/-IntelliJ%20IDEA-ffce5a?style=flat-square&logo=jetbrains)

![Linux](https://img.shields.io/badge/Linux-black?style=flat-square&logo=linux)
![Git](https://img.shields.io/badge/-Git-black?style=flat-square&logo=git)

## 𝗦𝘁𝗮𝘁𝘀

![github stats](https://github-readme-stats.vercel.app/api?username=wideGenesis&show_icons=true&theme=dracula&include_all_commits=true&count_private=true)
