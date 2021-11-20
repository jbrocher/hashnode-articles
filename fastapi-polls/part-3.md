## Introduction

 - Welcome to part 3 of the FastAPI tutorial
 - We'll pick up where we left off in part 2 where we set up the database
 - Today as in part 3 of django tutorial we'll create a views to dipslay the list of question and their results
 - Their is a key differnce though, as we're not working with a monolithe like Django. FastAPI is only concerned with build the API, and doesn't handle 
 rendering the ui (well except for the brillant automatic documentation)
 - This means we need to build the UI separatly, and we'll use reactjs for that!

 - Menu: 
  - Creating the CRUD endpoints using pydantic and SQLAlchemy
  - Creating a small SPA in React with `create-react-app` to display the result


## Crud
 - Thanks to the work we did last time, our database is already configure. Spin everything up with `docker-compose up ` and let's get coding
 - The first thing we'll do is creating some crud utilities for reading from our database. Add a `crud.py` file in your poll app, and create those two functions: 
 - We'll creat a function to list all the existing question and a specific one by filtering on its id
 - We'll use SQLAlchmey for quering the database

 ```python

 # crud.py

from sqlalchemy import select
from sqlalchemy.orm import Session

from polls import models
from polls import schemas


def get_question(db: Session, question_id: int):
    question_query = select(models.Question).where(models.Question.id == question_id)
    question = db.execute(question_query).one().Question
    return question


def list_questions(db: Session):
    question_query = select(models.Question)
    questions = db.execute(question_query).scalars().all()
    return questions
```
- last time I talked about how sqlalhemy make queryin the Database more expiclit, here we are !
- the `select(models.Question).where(models.Question.id == question_id)` is equivalent to the following SQL statement : 

 ```sql

  SELECT
   * 
  FROM
    polls_question 
  WHERE polls_question.id = 1

  ```

- As you can see, it very similar. This means that if you're confident with SQL , you'll peek up SQLAlchemy queryng sytem in no time !
- The only thing that might not be obvious here is the way the related choices are fetched. In SQL land we'd need to perform the following join to 
get the choices associated with each question (and thus created duplicated questions). 

```SQL

SELECT 
  *
FROM 
  polls_question as question
  LEFT JOIN polls_choice as choice on choice.question_id = question.id
```

With SQLAlchemy, the [relationship](https://docs.sqlalchemy.org/en/14/orm/relationships.html) will take care of that for us, as we'll see in the next section ! 


## Pydantic models

- Now that ou CRUD is ready, we need a way to serialize our answer. That's where pydantic comes in
- We used it last time to load our environment variables, but it can do much more !
- They play the same role as DRF serializers:
  - Deserialzer and validate intpu from outside the API
  - Serializer and validate output from our endpoint

- One last thing before we dive in : pydantic also uses the term "models" like SQLAlchemy. This tends to make this kind of tutorial a bit confusing if it's your first time workng with pydantic. Thus (like in the Fastapi doc) I will be refering to Pydantic models as Schemas !

With this out of the way, let's write the necessary schemas to serialze our questions. Add a  `schemas.py` file to your poll app, and create the followig models : 

```python

# app/polls/schemas.py

import datetime
from typing import List

import pydantic


class Choice(pydantic.BaseModel):
    choice_text: str
    votes: int

    class Config:
        orm_mode = True


class Question(pydantic.BaseModel):

    id: int
    question_text: str
    pub_date: datetime.datetime

    class Config:
        orm_mode = True


class ReadQuestionChoices(ReadQuestion):
    choices: List[BaseChoice]
```


 - Contray to DR there is no way out of the box to generate pydantic models from sqlalchemy models
 - Talking about models for pydantic and sqlalchemy can be confusing, so like in the FastAPI doc, when refering to pydantic we'll use the workd "schema" instead
 - All of this is still a wip in FastAPI, a solution is being developed 
  - SQLmodel
  - The solution from reddit user
 - We can use Recursive models, and they will be able to read from our models relationships !



## Endpiont 
 - We need to configure the CORS header so this works with our front

## Front

 - Install ui with create-react-app
 - Install additional dependencies
  - material ui for the front
  - axios and react-query for the queries
  - react-router (v6) for the routing

### Index
 - We'll create the pol index component and the associated route
