FROM    python:3.9
ENV     PYTHONFAULTHANDLER            1
ENV     PYTHONUNBUFFERED              1
ENV     PYTHONHASHSEED                random
ENV     PYTHONDONTWRITEBYTECODE       1
ENV     PIP_NO_CACHE_DIR              off
ENV     PIP_DISABLE_PIP_VERSION_CHECK on
ENV     PIP_DEFAULT_TIMEOUT           100

EXPOSE  8000
ENV     DEBIAN_FRONTEND               newt

WORKDIR /api
COPY    . .
RUN     pip install -r requirements.txt
