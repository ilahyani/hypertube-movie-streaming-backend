FROM node:22

RUN apt-get update && apt-get upgrade -y

WORKDIR /app

COPY ./package.json ./

RUN npm install -g npm@latest

RUN npm i

CMD [ "npm", "run", "dev" ]