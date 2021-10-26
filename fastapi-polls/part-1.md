# Making the Djano Polls app with FastAPI and React - Part 1

 - First part of a series where we'll be recreatign the polls app from the django tutorial
 - The goal is to help people like me coming from django adopt fastapi 
 - We'll mirror the tutorial. Each part will have its own repo
 - Today we'll simply see:
    - How to set up a fastapi project
    - How to create a poll app (And what it means in fasta api)

## Setting up the project

- Fastapi is easy to setup
    - You just need fastapi, uvicorn and a main.py file
    - We could use a virtual env
    - I prefer docker for ease of deployemnet
### The docker image

- Create the following docker file

```python 

FROM python:3.9

WORKDIR /app

# Install Poetry
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | POETRY_HOME=/opt/poetry python && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false


# Copy using poetry.lock* in case it doesn't exist yet
COPY ./app/pyproject.toml ./app/poetry.lock* /app/

RUN poetry install --no-root --no-dev

COPY ./app /app


CMD ["uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "80"]


```

This need a bit of commenting : 
- We use poetry as a package manager. This makes development easy
  - I use dev dep: black
- We use uvicorn and in production you should use a container manager as per [the docs](https://fastapi.tiangolo.com/deployment/docker/#build-a-docker-image-for-fastapi)

- Reload means the app will relaod in real time

- We use app 
:! 

### The fastapi app

 - As as said we only need a main.py
 - Coming from django I will use a main app and sub-app. The poll app will be a sub app

 ![directory structure](https://cdn.hashnode.com/res/hashnode/image/upload/v1635273859524/n4H8JXTCP.png?auto=compress)

 - Behold ! Here comes the hello world !
 - In the main.py file write the following code:

```python

from fastapi import FastAPI


app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}

```

### Launching the app

- you need to build the dokcer image: `docker build -t poll-app .`
- And then run it `docker run -v app:/app poll-app`
- The volume is good for developing we could also use docker-compose

- test your endpoint : 
![the endpoint](https://cdn.hashnode.com/res/hashnode/image/upload/v1635274086447/WFE1yO918.png?auto=compress)

- Fastapi goodies the docs ! 

![docs](https://cdn.hashnode.com/res/hashnode/image/upload/v1635274196047/B9w6r4ub3.png?auto=compress)


## Creating a poll app

 - We'll create a new folder for the poll app and use [api router](https://fastapi.tiangolo.com/tutorial/bigger-applications/#apirouter)


 - create a `polls/routes.py` file and write : 


```python

  from fastapi import APIRouter

  router = APIRouter()


  @router.get("/")
  async def index():
      return {"message": "polls index"}


```


 - You shouldn't need to restart anythign
 - Checkout the docs ! 
