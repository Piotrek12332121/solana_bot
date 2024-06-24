# solana_bot 
This is a simple bot that connects to available discord channel and informs  whether RSI indicator for SOL/USD trading pair is below 30 or above 70.

## Usage
Bot can be added to a server with a help of a link:

https://discord.com/oauth2/authorize?client_id=1254162765384515615&permissions=2048&integration_type=0&scope=bot

A docker image runs can be downloaded from docker hub:

https://hub.docker.com/repository/docker/opornypiotrek/solana_bot/general

By using command:
``` bash
docker pull opornypiotrek/solana_bot:latest
``` 
And then run locally with a help of command:
``` bash
docker run solana_bot
``` 
