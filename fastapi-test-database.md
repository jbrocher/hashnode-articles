# FastAPI: Testing a Database


  If you haven't heard of it yet, [FastAPI](https://fastapi.tiangolo.com/) is a micro-framewok that allows developers to make full use of modern Python."Micro" here, means that rather than trying to cover every use case, it focuses on doing a single thing extremely well: giving you the tools to build a fast (duh) API. Everything else is up to you which allows you to tailor you architecture to perfectly fit your needs. 

  However it does mean that you have to set up yourself some things that usually comes out of the box in other frameworks. For example, if you want to use a relational database, 
  you'll have to choose and install an ORM. SQLAlchemy is the one documented by Fast API. There is a [guide](https://fastapi.tiangolo.com/tutorial/sql-databases/) to help you set it up, and a [tutorial](https://fastapi.tiangolo.com/advanced/testing-database/?h=test+data) wich gives some indications on how to go about testing it. But if like me, you come from Django, you might still struggle to configure everything so that each test works in isolation, and leaves the database as it was before running. 

  That's what we'll be covering in this article ! 

  *The code presented in this article is fully available on [Github](https://github.com/jbrocher/hashnode-testing-database-fastapi). Simply clone the repo and call `docker-compose up` to launch everything.* 


---

## Setting up The project

  First things first, we need something to test ! We'll create a small project with an endpoint to create an "Item" with a title and a description and store it in the database. I personnaly prefer to use docker-compose to run a Fastapi image as well as a Postgres database next to it. But it's not mandatory.

  Let's get to it then ! 

### Setting up SQLAlchemy

  SQLAlchemy works by creating a [declarative base](https://docs.sqlalchemy.org/en/14/orm/mapping_api.html#sqlalchemy.orm.declarative_base), which allows us to describe our Database tables as Python classes that inherits it. Let's configure it in a file called `database.py`:


  ```python

    # database.py

    from sqlalchemy import create_engine
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker

    # We're using postgres but you could use
    # any other engine supported by SQlAlchemy
    SQLALCHEMY_DATABASE_URL = "postgresql://test-fastapi:password@db/db"

    engine = create_engine(
        SQLALCHEMY_DATABASE_URL
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    Base = declarative_base()
  ```

  Now we can create our Item model by inherting `Base`

### Models, schemas, and CRUD utils
  
  For our `Item` model, we simply create a file called `models.py` and declare it using the `Base` we've juste configured :

  ```python

      # models.py
    

      from sqlalchemy import Column
      from sqlalchemy import Integer
      from sqlalchemy import String

      from .database import Base


      class Item(Base):
          __tablename__ = "items"

          # Don't forget to set an index ! 
          id = Column(Integer, primary_key=True, index=True)

          title = Column(String, index=True)

          description = Column(String, index=True)

  ```

  We also need to define the corresponding [Pydantic](https://pydantic-docs.helpmanual.io/) schemas. FastAPI uses them to perform validation and serailization : 

  ```python

    # schemas.py
    from typing import Optional

    from pydantic import BaseModel


    class ItemBase(BaseModel):
        title: str
        description: Optional[str] = None


    class ItemCreate(ItemBase):
        pass


    class Item(ItemBase):
        id: int

        class Config:
            orm_mode = True

  ```

  And finally some CRUD utils for handling our `Item` instances :  
  ```python
    
    # crud.py

    from sqlalchemy import select
    from sqlalchemy.orm import Session

    from . import schemas
    from .models import Item


    def get_items(db: Session):
        items = select(Item)
        return db.execute(items).scalars().all()


    def create_item(db: Session, item: schemas.ItemCreate):
        db_item = Item(**item.dict())
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item

  ```

 Now that we're done with everything database related, we can create the endpoint that we'll be testing ! 

### The endpoint itself

  Create a `main.py` file and add the following lines to it : 

  ```python

      # main.py

      from typing import List

      from fastapi import Depends
      from fastapi import FastAPI
      from sqlalchemy.orm import Session

      from . import crud
      from . import models
      from . import schemas
      from .database import engine
      from .database import SessionLocal

      app = FastAPI()

      # Here we create all the tables directly in the app
      # in a real life situation this would be handle by a migratin tool
      # Like alembic
      models.Base.metadata.create_all(bind=engine)


      # Dependency
      def get_db():
          db = SessionLocal()
          try:
              yield db
          finally:
              db.close()

      @app.post("/items/", response_model=schemas.Item)
      def create_item(item: schemas.ItemCreate, db: Session = Depends(get_db)):
          return crud.create_item(db, item)

  ```

Notice that we pass the SQLAlchemy Session as a dependency to our endpoint. This is important to note as it'll help us easily test our endpoint as we'll see in the next section. 


We can check that our endpoint works thanks to the Swagger available on the `/docs` endpoint. Another awesome feature of FastAPI ! 

![Items endpoint](https://cdn.hashnode.com/res/hashnode/image/upload/v1635078348118/SE73hLXOC.png?auto=compress)

That's great! But our goal here is to test the endpoint automatically with some unit tests. We need to make sure that our tests don't affect the main database. We also want them to be deterministic and reusable, let's see how to do exactly that ! 

--- 
## Testing the endpoint

### Basic testing

  First let's try the method described in the [official documentation](https://fastapi.tiangolo.com/advanced/testing-database/). The idea here is to 
  leverage FastAPI [Dependency](https://fastapi.tiangolo.com/tutorial/dependencies/) system. Since our endpoint receives its session by dependency injection, we can use [Dependency overrides](https://fastapi.tiangolo.com/tutorial/dependencies/) to replace it with a session pointing to a test Database. 

  To to that, create a file called `test_database.py` to write our tests, and add the following code to it : 


 ```python 
  
  # test_database.py
  SQLALCHEMY_DATABASE_URL = "postgresql://test-fastapi:password@db/test-fastapi-test"

  engine = create_engine(SQLALCHEMY_DATABASE_URL)
  TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

  def override_get_db():
      try:
          db = TestingSessionLocal()
          yield db
      finally:
          db.close()

  app.dependency_overrides[get_db] = override_get_db

```

This will replace all instances of the `get_db` dependency with the `override_get_db` which return a `Session` connected to our test database. This 
does one aspect of what we're looking for:  we can run ou tests without affecting our main database. 


Let's write a test and run it with pytest to see if that works as expected.


 ```python 

def test_post_items():

    # We grab another session to check 
    # if the items are created
    db = override_get_db() 
    client = TestClient(app)

    client.post("/items/", json={"title": "Item 1"})

    client.post("/items/", json={"title": "Item 2"})

    items = crud.get_items(db)
    assert len(items) == 2
 ```



  <center>

  ![test database](https://cdn.hashnode.com/res/hashnode/image/upload/v1635068579627/7AFO-ykoa.png?auto=compress)

  </center>


  It works perfectly ! Or does it ? We also want our tests to be deterministics, so if we run pytest again we should get the same result...


 <center>
  
  ![test fails](https://cdn.hashnode.com/res/hashnode/image/upload/v1635074467203/og4MI9utd.png?auto=compress)

 </center>

 But we dont ! The items created the first time we ran the test are still in the database, so now we have 
 4 of them instead of 2. Now, we could delete the items manually. However,  this is not something we want to do, because this will
 become really tedious to maintain once we have more tests that validate more complex behaviors. 

 Luckily for use there IS a better way ! 


### Enter transactions

 To solve our problem we'll make use of [SQL Transactions](https://www.w3resource.com/sql/controlling-transactions.php). Essentially 
 transactions are a way to keep a set SQL instructions private to other database connections, until they are commited. And, if the changes 
 should not be commited, they can be rolled back ! Let's add try to add that to our dependency override. Disclaimer the following block of code doesn't actually works, we'll see why in a minute :


```python


    # The following doesn't work
    # changes won't be rolled back !
    def override_get_db():
        try:
            db = TestingSessionLocal()
            db.begin()
            yield db
        finally:
            db.rollback()
            db.close()

    app.dependency_overrides[get_db] = override_get_db

```

  In a FastAPI dependency, everything that comes after the yield instuction is executed after the path operation has run. So that's a great place to 
  try to roll back the changes made during the test. This looks good, but as I said, it doesn't work yet

  That's because a call to commit always commit the [outermost transaction](https://docs.sqlalchemy.org/en/14/orm/session_transaction.html#commit-as-you-go), so we can't nest transactions thath way. This is a conscious choice from the SQLAlchemy developers to 
  avoid creating confusing and hard to predict behaviors. 

  Luckily for us they have provided an [escape hatch](https://docs.sqlalchemy.org/en/14/orm/session_transaction.html?highlight=transactions#joining-a-session-into-an-external-transaction-such-as-for-test-suites) designed to be used test suites. Indeed, a Session can be bound to an existing transaction, by opening it this way : 

  ```python

    def override_get_db():
      connection = engine.connect()

      # begin a non-ORM transaction
      transaction = connection.begin()

      # bind an individual Session to the connection
      db = Session(bind=connection)
      # db = Session(engine)

      yield db

      db.rollback()
      connection.close()
  ```

  And this time it will work ! 

  <center>

  ![Test passes](https://cdn.hashnode.com/res/hashnode/image/upload/v1635068882325/rIUktA5fT.png?auto=compress)
  
  </center>

  Now we can run our test as many times as we want, and it will always pass. But we're not quite done yet. This works for data created by the endpoint, 
  but what if we wanted to seed the database during our test, say for testing an endpoint listing the available items ? The dependency override won't work in this case,  because it only deals with 
  the dependency injection system. 


### Fixtures everywhere ! 

  Let's quickly implement the example I was just talking about: a READ endpoint that lists the existing items in the database : 


```python

    @app.get("/items/", response_model=List[schemas.Item])
    def read_items(db: Session = Depends(get_db)):
        return crud.get_items(db)
```

  In order to test it we'd want to create a bunch of items before calling the endpoint, while having the database revert back to its original state after the test. The solution is simple : define our test database session in a fixture as well : 

  ``` python 

    # conftest.py

    @pytest.fixture(scope="session")
    def db_engine():
        engine = create_engine(SQLALCHEMY_DATABASE_URL)
        if not database_exists:
            create_database(engine.url)

        Base.metadata.create_all(bind=engine)
        yield engine


    @pytest.fixture(scope="function")
    def db(db_engine):
        connection = db_engine.connect()

        # begin a non-ORM transaction
        transaction = connection.begin()

        # bind an individual Session to the connection
        db = Session(bind=connection)
        # db = Session(db_engine)

        yield db

        db.rollback()
        connection.close()


    # 
    @pytest.fixture(scope="function")
    def client(db):
        app.dependency_overrides[get_db] = lambda: db

        with TestClient(app) as c:
            yield c
  ```

  Pytest fixtures works like FastAPI dependencies: everything after the yield instruction is ran after exiting the scope pass as a paramter to the decorator.  Our `db` fixture rollsback the session after each test, and we can use it to seed the database. I've also put the dependency override in a fixture  alongside the client. That way each 
  time we use the client, the override will be in place.


Now we can create the fixture we want and test our new endpoint :
```python

    @pytest.fixture
    def items(db):
        create_item(db, schemas.ItemCreate(title="item 1"))
        create_item(db, schemas.ItemCreate(title="item 2"))
```


```python

# test_database.py"
def test_list_items(items, client):
    response = client.get("/items")
    assert len(response.json()) == 2
```

And again our tests pass without issues no matter how many time we run them ! 


<center>

![test pass](https://cdn.hashnode.com/res/hashnode/image/upload/v1635075764407/uP77OX5cW.png?auto=compress)

</center>


<center>
Hooray !

![yes !](https://media.giphy.com/media/msKNSs8rmJ5m/giphy.gif)

</center>

---

## That's all folks ! 

That's it for today, now you know how to properly test you FastAPI app when using a relational database. Thanks for reading, I'll 
write another article on FastAPI soon ! 

---

## References

1. [FastAPI website](https://media.giphy.com/media/msKNSs8rmJ5m/giphy.gif)
2. [Testing relational database](https://media.giphy.com/media/msKNSs8rmJ5m/giphy.gif)
3. [SQLAlchemy docs](https://www.sqlalchemy.org/)
4. [Transactions in SQLAlchemy](https://www.google.com/search?q=transactions+sql+alchemy&oq=transactions+sql+alchemy&aqs=chrome..69i57j69i60l2.3943j0j7&sourceid=chrome&ie=UTF-8)
