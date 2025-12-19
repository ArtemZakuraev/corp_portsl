FROM alpine:latest

RUN apk add --no-cache openssl

WORKDIR /certs

CMD ["sh", "-c", "openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout onlyoffice.key -out onlyoffice.crt -subj '/C=RU/ST=Moscow/L=Moscow/O=CorpPortal/CN=localhost' -addext 'subjectAltName=DNS:localhost,DNS:127.0.0.1,IP:127.0.0.1' && cp onlyoffice.crt /output/ && cp onlyoffice.key /output/"]



