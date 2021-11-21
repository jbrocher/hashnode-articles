
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

 
