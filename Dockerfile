FROM python:3.11

# Establecer el directorio de trabajo
WORKDIR /usr/src/app

# Copiar los archivos del proyecto al contenedor
COPY . .

# instalar las dependencias
RUN pip install -r requirements.txt
