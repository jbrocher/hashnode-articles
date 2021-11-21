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
 - All of this is not ideal, and lead to a bit of code duplication, as there are a lot of common logics between the pydantic schemas, and SQLAlchemy models. Tiangolo, the author of FastAPI, got us covered tho ! A months ago he released [SQLModel](https://sqlmodel.tiangolo.com/) a library  that aims to fill that gap by wrapping Pydantic and SQLAlchemy. 
 - I will not dive more into it during the early part of this tutorial tho, as I believe it's important to understand the problem a tool is designed to solve before using it !
 - We can use Recursive models, and they will be able to read from our models relationships !


 - the orm mode here allows Pydantic to use SQLAlchemy attributes. This also means that when serializing our reponse, if we use the `ReadQuestionChoices` schemas, it will automatically perfomr the join I was mentionning earlier, and offer us a nice nested structure where each question is associated with an array of related choices.
 - We can still simplyfi these models a bit though, as Pydantic support, before moving on to the endpoint, we'll factor the common attribtes between `ReadQuestion` and `ReadQuestionChoices`: 

```python


import datetime
from typing import List

import pydantic


class BaseChoice(pydantic.BaseModel):
    choice_text: str
    votes: int

    class Config:
        orm_mode = True


class BaseQuestion(pydantic.BaseModel):
    question_text: str
    pub_date: datetime.datetime

    class Config:
        orm_mode = True


# We only include the id when reading
# That way we can reuse base question
# When creating our write schemas
class ReadQuestion(BaseQuestion):
    id: int


class ReadQuestionChoices(ReadQuestion):
    choices: List[BaseChoice]
```
- There all good ! 

## Endpiont 

 - Let's implement the endpoints ! 
 - In Django's tutorial, there are 3 views: 
  - The index view: Listing the existing questions
  - The detail view: Listing the choices associated with question. Later used to render the form;
  - The results view: Listing the results of the questions

However we're not building a monolith here ! We'll be using React in the next section to create the UI. There we'll be creating these 3 views but for now we're on the API side of things and we only need 2 endpoints: 
  - An endpoint to list the existing questions: `/polls/`;
  - And endpiont to dipslay the details of the questins: `/polls/{id}`


In `polls/endpoints.py` create those two path operations : 

```python

# polls/endpoints.py

from typing import List

from . import schemas
from . import crud

@router.get("/", response_model=List[schemas.ReadQuestion])
async def index():
    return crud.list_questions(db)


@router.get("/{id}/", response_model=schemas.ReadQuestionChoices)
async def question_detail(id: int):
  try:
      return crud.get_question(db, id)
  except NoResultFound:
      raise HTTPException(
          status_code=404,
          detail="Token does not exist",
      )

```

There are a few things going on here: 
- We've added a second argument to the `router.get` call : the `response_model`. This response model will be applied to the value returned by the path operation, before sending the response to the client. We're using the `List` type from the standard `typing` package to specify that we returns several questions in the index.
- In the `question_detail` path operation, we specify the {id} in the router url, and FastAPI is smart enough to automatically pass it as the first parameter to our path operations ! 
- We're using fastapi [HTTPException](https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-in-path-operation-decorators/?h=exceptions#raise-exceptions) to automatically return a 404 error if there is no question matching the providing ID.

The type int and path parameters are also used by FastAPI to generate the automatic documentation !

However, If you've been paying attention you might have noticed that something is missing. Our crud utils need a `Session` objects to communicate with the database. We're passing them a variable called `db` here, but it's not defined anywhere yet ! 

To retrieve this Session objects, we'll use one of FastAPI main selling point: its [dependency injection system](https://fastapi.tiangolo.com/tutorial/dependencies/) ! 

**What is dependeny injection** ? 

If you've alredy work with a Framework before, you should be familiar with the term. Dependency injection is a form of inversion of control that allows a "client" to specify
the dependencies it needs an trust that an other agent, oftenime the framework, will provide them at the right time. 

For example in Django's view, the `self.request` object available in Class Based view is a dependency injection pattern ! Hope this clears at up !

<center>

![Fascinating](https://media.giphy.com/media/vp122eOzO0Hxm/giphy.gif)

<small> *Isn't it ?* </small>

</center>

The dependency we're looking to inject is a Session. To do so, we declare a function that returns a session using the `SessionLocal` we created in `database.py` we created in  [part 2](https://dev.indooroutdoor.io/building-the-poll-app-from-the-django-tutorial-with-fastapi-and-react-2)

```python

# polls/endpoints.py


# Database session as a dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

```

The code after the yield instructions will be execute right after our path operation is done sending the response. This way we can make sure the session is closed correctly ! Now we can use the `Depends` function providing from FastAPI:


```python

# polls/endpoints.py


...

from fastapi import Depends

...


@router.get("/", response_model=List[schemas.ReadQuestion])
async def index(db=Depends(get_db)):
    return crud.list_questions(db)


@router.get("/{id}/", response_model=schemas.ReadQuestionChoices)
async def question_detail(id: int, db=Depends(get_db)):
    try:
        return crud.get_question(db, id)
    except NoResultFound:
        raise HTTPException(
            status_code=404,
            detail="Token does not exist",
        )


```

Now everything should be working ! You can try out your endpoints using the automatic documentation available at `localhost/docs`. Create a few questions using [PGAdmin](https://dev.indooroutdoor.io/building-the-poll-app-from-the-django-tutorial-with-fastapi-and-react-2) or a psql client to create a few questions and choices, and try it out ! 

<center>

![Testing the endpoints](https://cdn.hashnode.com/res/hashnode/image/upload/v1637488798054/R0775c0Wt.gif?auto=compress)

</center>


Awesome ! But we this isn't enough for our end user tho, we can't ask them to use our poll app using the automatic documentation... we need something better !

We need to do one last thing before we start building our UI though, setting the cors headers so the browser let our SPA make request to the FastAPI app. This is pretty straightforward, we just need to use the `CORSMiddleware` in `main.py`: 


```python

# main.py

...

from fastapi.middleware.cors import CORSMiddleware


origins = ["http://localhost:3000"]

...

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

...
```



## Let's build an UI ! 

We'll use [Create React App](https://reactjs.org/docs/create-a-new-react-app.html) to build our UI in React. CRA is an awesome collection that take care of bundling, transpiling, and allthe boilerplate code you might need to setup at the begining of a react project. This way we can get straight to coding ! 

For this tutorial, our UI Will live in the same project than our API. From the root of the project run the following command to create the UI : 

 - `yarn create react-app ui --template typescript`

 OR if you prefer npm

 - `npx create-react-app ui --template typescript`

Note: We'll be using typescript for this tutorial. Don't worry you don't need to have a deep understanding of types to follow along tho, we'll stay pretty basic ! This will mainly prevent us to make mistakes when using data coming from the API.

### Installing the dependencies

To create the same views as the Django tutorial, we'll need the following libraries : 
 - [Axios](https://github.com/axios/axios): An awesome library to make requests. 
 - [React Router](https://reactrouter.com/): For client side navigation
 - [react-query](https://mui.com/): Painless server side synchronization
 - [Material UI](https://mui.com/components/lists/): Not strictly necessary, but great for decent UI without beging a designer

Note: None of these are *strictly* necessary, but this is may go to setup when I need to quicly build a small SPA. I must say I pretty satisfied with it, but if you have any feedback [Reach out on Twitter](https://twitter.com/home) 🐦! 


### Setting up react-query

First we'll quickly set up react-query : 

 - Create the default query function
 - I like to put these kind of stuff in an `utils` folder

 ```typescript

// utils/queryFn

import axios from "axios";

// We use the built-in QueryFunction type from `react-query` so we don't have to set it up oursevle
import { QueryFunction } from "react-query";

export const queryFn: QueryFunction = async ({ queryKey }) => {
  const { data } = await axios.get(`http://localhost:80/${queryKey[0]}`);
  return data;
};

 ```
 - When using react query for quering the app, we simply need to pass the endpoint we want to query
 - Then to finish setting up react-query we simply write our app into a client provider

```typescript

// index.tsx

import React from "react";
import ReactDOM from "react-dom";
import "./index.css";
import App from "./App";
import reportWebVitals from "./reportWebVitals";
import { queryFn } from "./utils/queryFn";
import { QueryClient, QueryClientProvider } from "react-query";

// Configuring the queryclient to use
// our query function
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      queryFn: queryFn,
    },
  },
});

ReactDOM.render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <App />
    </QueryClientProvider>
  </React.StrictMode>,
  document.getElementById("root")
);

```

### Setting up react router

 - We also need to set up react router so we can start working with routes :
 - Replace the content of `App.tsx` by this :


 ```typescript

import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import PollIndex from "routes/Poll";
import Results from "routes/Poll/Results";

import CssBaseline from "@mui/material/CssBaseline";
import "./App.css";

function App() {
  return (
    <div className="App">
      <CssBaseline />
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<div>Poll Index</div<}></Route>
          <Route path=":questionId/results/" element={<div>Poll Results</div<} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
 ```


Now you should see the the following at `localhost:3000/`

![Poll index ](https://cdn.hashnode.com/res/hashnode/image/upload/v1637492732745/TKHnqx8R9.png?auto=compress)


And the results at `localhost:3000/1/results` (Or any `localhost:3000/{id}/results` url for that matter)

![Poll results](https://cdn.hashnode.com/res/hashnode/image/upload/v1637492803037/Yrouprs2h.png?auto=compress)


Now all that's let to do is to build a `PollIndex` and `PollResult` component to replace the place holders! First of all let's create a template for our pages. That 
way we can display a nice AppBar on both component while keeping the code DRY. Create a file in `src/components/templates/Page.tsx` (Creating the folders as needed).

And define the Page component like so: 


```typescript

// Page.tsx



```

 
