*Note: This is part 4 of a multi-part tutorial on FastApi and React. If you want to start from the beginning (which I recommend!😉) here's [part 1](https://dev.indooroutdoor.io/the-poll-app-from-django-tutorial-with-fastapi-and-react-1)!*

Welcome to part **4** of this tutorial! Today we'll see how to connect a React app to our awesome FastAPI backend! As always, [here's the repository](https://github.com/jbrocher/fast-api-poll-4) with the code we'll be writing during this article.


Last time we added the following routes to our API:
 - `/polls/`:  Lists all the existing questions
 - `/polls/{id}/`:  Displays a poll details, including the associated results

Now our goal is to use them to display the same information as in the original [Django tutorial](https://docs.djangoproject.com/en/3.2/intro/tutorial03/), using React: 
 - An index page for listing the polls
 - A Form for each poll
 - A Result page for each poll

In fact, since we'll be using React we can go one step further and merge the two last views together in a mutli-purpose detail view with the following specs: 
 1. First when arriving on `/polss/{id}/` the user should see the title of the poll and the available choices
 2. Then the user submits their own vote by clicking on one of the choices
 3. Finally once the vote is processed by the API, the current vote count is displayed to the user under each choice

As in the Django tutorial, we'll keep the actual vote submission for the next part though ! 

We'll use [Create React App](https://reactjs.org/docs/create-a-new-react-app.html) to build our UI in React. CRA is an awesome collection of scripts that take care of bundling, transpiling, and all the boilerplate code you might need setup a React project. This way we can get straight to coding ! 

## Setting up the project

For this tutorial, our UI Will live in the same project than our API. In real life though, you'd probably want to have a separate repository. From the root of the project run the following command to create the UI : 

 - `yarn create react-app ui --template typescript`

 OR if you prefer npm

 - `npx create-react-app ui --template typescript`

Note: We'll be using [typescript](https://www.typescriptlang.org/) for this tutorial. Don't worry you don't need to have a deep understanding of types to follow along tho, we'll stay pretty basic ! This will mainly prevent us to make mistakes when using data coming from the API.

We'll also need the following libraries to build our UI: 
 - [Axios](https://github.com/axios/axios): An awesome library to make requests. 
 - [React Router](https://reactrouter.com/): For client side navigation
 - [react-query](https://mui.com/): Painless data synchronization with the server
 - [Material UI](https://mui.com/components/lists/): Not necessary, but great to quickly prototype something if youd don't have any design skills. (Like me 👌)

Note: None of these are *strictly* necessary, but this is of my go to setup when I need to quicly build a small SPA. I must say I'm pretty satisfied with it, but if you have any feedback [Reach out on Twitter](https://twitter.com/home) 🐦! 


Our project is ready. Without further ado let's dive in ! 

<center>

![Bring it on](https://media.giphy.com/media/dUHdTk3tvry9NETa67/giphy.gif)

*I will!*
</center>


## Setting up react-query

We'll start by setting up react-query. React query allows to define a [default query function](https://react-query.tanstack.com/guides/default-query-function). As we'll only be using `useQuery` to communicate with our API, we'll  set it ot use Axios's GET function. That way we can use our endpoints URLs, both as [query keys](https://react-query.tanstack.com/reference/useQuery#_top) and argument for axios. 


I like to put my query function in an `utils` folder like so:


 ```typescript

// utils/queryFn.ts

import axios from "axios";

// We use the built-in QueryFunction type from `react-query` so we don't have to set it up oursevle
import { QueryFunction } from "react-query";

export const queryFn: QueryFunction = async ({ queryKey }) => {
  // In a production setting the host would be remplaced by an environment variable
  const { data } = await axios.get(`http://localhost:80/${queryKey[0]}`);
  return data;
};

 ```

Then we just need to configure the QueryClient to use our default function: 

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

## Setting up react router

We also need to setup ou client side routing. As explained in the introduction, we'll create two routes: The Poll index and the Poll details. For now we'll just put some placeholder in there until we get to building the actual views in the next section 😄! 


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
          <Route path=":questionId/" element={<div>Poll Form</div<} />
          <Route path=":questionId/results/" element={<div>Poll Results</div<} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
 ```



Now launch the app with `yarn start` and both routes should become available!

![The routes](https://cdn.hashnode.com/res/hashnode/image/upload/v1638712757443/Snlmu2A-x.png?auto=compress)

Now all that's left to do is to build a `PollIndex` and `PollResult` components to replace the placeholders! These components will be responsible for querying the API using `react-query` and display the results ! 

## Building the Poll index

We'll start building the Poll Index. We want to list all the existing polls, and maybe make them link to the corresponding Form while we're at it !


<center>
 
![The time has comme](https://media.giphy.com/media/0VxdFBlV73nIWeVSH7/giphy.gif)

</center>

... ~~To Lip-Sync FOR YOUR LIFE!~~ to query our endpoints with `useQuery`!  

### Types definition

First, since we're using typescript, we need to describe the type we expect to receive from our API. That's where FastAPI automatic documentation really shines in my opinion. When you - or others - want to build something that interface with our API (which should be expected when working on an Application Programming *Interface*), all you have to do is consult the `/docs` endpoint. 

Let's have a look to both our endpoints: 

Here's the documented respone shape for `/polls/`

<center>

![Poll endpoint response](https://cdn.hashnode.com/res/hashnode/image/upload/v1638628547064/HyoxEp3qE.png?auto=compress)

</center>

And the one for `/polls/{id}`:

<center>

![Poll detail response](https://cdn.hashnode.com/res/hashnode/image/upload/v1638628618152/SSEyaZMU0.png?auto=compress)

</center>

Pretty straightforward, le's translate that into typescript, and we'll be guaranteed to communicate with our API correctly! Here's the types we'll be workgin with:

```typescript


export interface Choice {
  id: number;
  choice_text: string;
  votes: number;
}

export interface Question {
  id: number;
  pub_date: string;
  question_text: string;
}

export interface QuestionResults extends Question {
  choices: Choice[];
}

```

We're done with typescript !


Now, I like to put all my pages components inside a `routes` folder and then mimick the actual route structure of the app. With the latest version of [react-router out](https://reactrouter.com/docs/en/v6/upgrading/v5), I need to check what the current best practices are though!

Create `routes/Poll/index.ts`, with the following Implementation:

```typescript

//Poll/index.ts

import React from "react";

// The type we've just defined
import { Question } from "types";
import { useQuery } from "react-query";

// Routing
import { Link} from "react-router-dom";


// Material ui stuff
import { styled } from "@mui/material/styles";
import Card from "@mui/material/Card";
import Typography from "@mui/material/Typography";
import Container from "@mui/material/Container";
import Box from "@mui/material/Box";
import Page from "components/template/Page";

const StyledLink = styled(Link)`
  text-decoration: none;
`;

const PollIndex: React.FunctionComponent = () => {

  // Syncing our data
  const { data: questions, isSuccess } = useQuery<Question[]>("polls/");

  // In real life we should handle isError and isLoading
  // displaying an error message or a loading animation as required. 
  // This will do for our tutorial
  if (!isSuccess) {
    return <div> no questions </div>;
  }

  return (
    <Page title="Index">
      <Container maxWidth="sm">
        {questions?.map((question) => (
          <Box marginY={2}>
            <StyledLink to={`${question.id}/results/`}>
              <Card key={question.id}>
                <Typography color="primary" gutterBottom variant="h3">
                  {question.question_text}
                </Typography>
              </Card>
            </StyledLink>
          </Box>
        ))}
        <Outlet />
      </Container>
    </Page>
  );
};

export default PollIndex;

```

And then replace the placeholder in `App.tsx`: 

```typescript

// App.tsx


import PollIndex from "routes/Poll";

...

function App() {
  return (
  ...
  <Route>
    ...

    <Route path="/" element={<PollIndex />}></Route>
  </Routes>
  )
}

```

The most important bit here is `const { data: questions, isSuccess } = useQuery<Question[]>("polls/");`. As you can see I'am passing the `useQuery` hook the expected type of our response. Otherwise `data` would be of type `unkown` and we don't want that ! 

For the rest, displaying the list of question is as easy a mapping over the query results. Let's see how that looks:



<center>

![Poll index](https://cdn.hashnode.com/res/hashnode/image/upload/v1638629389333/zJka6fykW.png?auto=compress)

</center>


Not bad uh ? 

<center>

![It's beautiful](https://media.giphy.com/media/p8GJOXwSNzQPu/giphy.gif)

<small> *Now, now, no need to cry* </small>

</center>

We'll build the Details view using exactly the same method ! 


## Building the detail page

This one will live next to the `Polls/index.tsx` page, let's call it `Polls/Details.tsx`. This time, as this page will be accessed at `polls/<poll_id>` we'll use the `useParam` hook from `reat-router-dom` to retrieve the id, and pass it to our API. Like so : 

```typescript 

// Detail.tsx

import React, { useState } from "react";

// types
import { QuestionResults } from "types";

// routing
import { useParams } from "react-router-dom";

// querying
import { useQuery } from "react-query";


// Material ui stuff
import Card from "@mui/material/Card";
import Page from "components/template/Page";
import Chip from "@mui/material/Chip";
import CardContent from "@mui/material/CardContent";
import CardHeader from "@mui/material/CardHeader";
import CardActionArea from "@mui/material/CardActionArea";
import Typography from "@mui/material/Typography";
import Grid from "@mui/material/Grid";


const Details = () => {
  const { questionId } = useParams();

  // This state variable controls
  // displaying the results
  const [hasVoted, setHasVoted] = useState(false);

  // We can use the id from use param
  // directly with the useQuery hook
  const questionQuery = useQuery<QuestionResults>(`polls/${questionId}/`);

  if (!questionQuery.isSuccess) {
    return <div> loading </div>;
  }

  return (
    <Page title={questionQuery.data.question_text}>
      <Grid spacing={2} container>
        <Grid item xs={12}>
          <Typography variant="h2">
            {questionQuery.data.question_text}
          </Typography>
        </Grid>
        {questionQuery.data.choices.map((choice) => (
          <Grid item xs={12} md={6}>
            <Card key={choice.id}>
              <CardActionArea onClick={() => setHasVoted(true)}>
                <CardHeader title={choice.choice_text}></CardHeader>
                <CardContent>
                  {hasVoted && <Chip label={choice.votes} color="success" />}
                </CardContent>
              </CardActionArea>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Page>
  );
};

export default Details;

```

That's it! Look pretty much the same as the index, we're juste using `map` over the choices of a specific poll to display them. The results display are controlled using
a simple `useState` hook. However if this data was really sensitive, we'd have to restrict access to it on the server as well !

Just replace the placeholder in `App.tsx` and admire the result ! 
```typescript

// App.tsx


import PollDetails from "routes/Poll/Details";

...

function App() {
  return (
  ...
  <Route>
    ...

    <Route path="/" element={<PollIndex />}></Route>
    <Route path="/" element={<PollDetails />}></Route>
  </Routes>
  )
}

```



<center>

![Detail results](https://cdn.hashnode.com/res/hashnode/image/upload/v1638632086531/L3YqjDcfh.gif?auto=compress)

<small> *A very scientific survey I made* </small>

</center>


Looks great !


## Thanks for reading !

That's a wrap for part 4! Hope you liked it, next time we'll see how to actually submit the vote to our API and save it to the database! 😃

As always if you have any question you can reach out to me on [Twitter](https://twitter.com/JiBRocher) 🐦!


## References

1. [react-query](https://react-query.tanstack.com/overview)
2. [react-router](https://reactrouter.com/)
3. [FastAPI](https://fastapi.tiangolo.com/)
