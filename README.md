# shorten-service

## set up with docker image
1. pull this repo and this image `kcw998998/side:shorten-service`
2. execute the commands below
```
docker pull kcw998998/side:shorten-service
docker-compose up --build
```
## APIs intro
### create-url (post)
- payload
```
{
    "original_url": "https://www.google.com"
}
```
- response
```
{
    "short_url": "8ffdefbdec956b595d257f0aaeefd623",
    "success": true,
    "expiration_date": "2025-02-02T10:59:30.130352",
    "reason": ""
}
```
### rediect-url (get)
- put the url in browser ex: `http://8ffdefbdec956b595d257f0aaeefd623`

## rate-limiting principle
- at most 3 times in 5 seoconds
- return status code 429 if exceeds the limit
