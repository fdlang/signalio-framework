FROM python:3.11

# Establecer el directorio de trabajo
WORKDIR /usr/src/app

# Copiar solo el archivo de requerimientos para instalar dependencias
COPY requirements.txt .

# Instalar las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Ahora copiar el resto de los archivos
COPY . .

# Especificar el comando por defecto, si tienes uno
CMD ["python", "trading_app.py"]
