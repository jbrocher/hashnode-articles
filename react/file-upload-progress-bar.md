## Introduction

Forms are often tricky to get right with React. While there are great libraries like [formik](https://formik.org/) or [React Final Form](https://github.com/final-form/react-final-form) to do the heavy lefting for us, handling file upload still isn't always straight forward. 

In today's episode of React Tips & Tricks, we'll see how to handle and submit file Data, and how to display a progress bar !

##  A basic Form

Let's say we need to build a form to create blog posts, with an `input` for the title, and a `textarea` for the body.

Here's a simple implementation for such a form, using [Material UI](https://mui.com/) for the basic components: 
 
```typescript

import React, { useState } from "react";
import Box from "@mui/material/Box";
import TextField from "@mui/material/TextField";
import Button from "@mui/material/Button";

interface PostData {
  title: string;
  body: string;
}

const Form: React.FunctionComponent = () => {
  const [formValues, setFormValues] = useState<PostData>({
    title: "",
    body: "",
  });

  // Handlers for the input
  const handleTitleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setFormValues((prevFormValues) => ({
      ...prevFormValues,
      title: event.target.value,
    }));
  };

  const handleBodyChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setFormValues((prevFormValues) => ({
      ...prevFormValues,
      body: event.target.value,
    }));
  };

  return (
    <Box
      display="flex"
      height="100%"
      flexDirection="column"
      justifyContent="center"
      alignItems="center"
    >
      <Box marginY={2}>
        <TextField
          onChange={handleTitleChange}
          value={formValues.title}
          label="Post Title"
          name="title"
        />
      </Box>
      <Box marginY={2}>
        <TextField
          onChange={handleBodyChange}
          multiline
          minRows={5}
          label="Post Body"
          name="body"
        />
      </Box>
      <Box marginY={3}>
        <Button onClick={() => console.log("submit")}>Submit Post </Button>
      </Box>
    </Box>
  );
};

export default Form;
 ```

*Note: I'm not using any Form libraries here, as I want to focus on file handling. In a production setting I'd really recommend using somethign like [Formik](https://formik.org/docs/api/formik) to avoid re-inventing the wheel!*


This works like a charm, and renders the following output: 

<center>

![Post Form](https://cdn.hashnode.com/res/hashnode/image/upload/v1636902278730/212jbOdu_.png?auto=compress)

</center>

Great! But now say we also want to submit an image along with the title and the body, to serve as a cover for the article. This is a bit more complicated as we're not juste maniuplating strings anymore.


## Adding an image to the post

In order to be able to submit an image, we need to add 3 things to our Form : 
 - A button to upload a file from the client's computer;
 - A way to handle the file and store it in the sate;
 - A handler to submit our form;

Let's dive in ! 

### Adding the button

To add a file upload button to the form, we use an `input` of type `file`, wrapped in a `Button` component :

 ```JSX
  //Form.tsx

const Form: React.FunctionComponent = () => {
  
  ...

  return (
    ...

    <Box marginY={2}>
      <TextField
        onChange={handleBodyChange}
        multiline
        minRows={5}
        label="Post Body"
        name="body"
      />
    </Box>

    <Button variant="contained" component="label">
      <input type="file" hidden />
    </Button>

    <Box marginY={3}>
      <Button onClick={() => console.log("submit")}>Submit Post </Button>
    </Box>
  )
}

 ```

 Here we leverage the fact that a label (Here rendered as a Button) is [programmatically](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/label) linked to its input. Meaning, any click event on our "Button" component will be passed to the hidden input. This trick allows us to display any component we want to the user, while still benefiting fro the built-in file handling system.


### Controlling the component

 For now our input is [uncontrolled](https://reactjs.org/docs/uncontrolled-components.html): it's not linked to any state variable, so we can't declaratively use its value when submitting the form. We need to change that : 

 <center>

 ![Give me Control](https://media.giphy.com/media/YO3icZKE2G8OoGHWC9/giphy.gif)

 <small> *I agree with Dwight!* </small>
 
 </center>


 To control our input, as with a normal input, we need to pass it a handler. This handler uses the [File API](https://developer.mozilla.org/en-US/docs/Web/API/File) to retrieve the fiels data we interested in: 

```typescript 

interface PostData {
  title: string;
  body: string;
  image: File | null;
}

const Form: React.FunctionComponent = () => {

  // Add an image attribute
  // to our formData
  const [formValues, setFormValues] = useState<PostData>({
    title: "",
    body: "",
    image: null,
  });
  ...

  // Set up the handler
  const handleImageChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setFormValues((prevFormValues) => ({
      ...prevFormValues,
      image: event.target.files ? event.target.files[0] : null,
    }));
  };

  ...


return (
    ...
      <Button variant="contained" component="label">
        {formValues.image?.name ?? "Upload File"}
        {/* Bind the handler to the input */}
        <input onChange={handleImageChange} type="file" hidden />
      </Button>
    ...
  )
}


```

Now when the user uploads an image using our button, the `image` attribute will be populated with a File object. This object has a lot of useful
[properties](https://developer.mozilla.org/en-US/docs/Web/API/File), like the name of the file, and its type. We can use them to display the name file currently selected by the user inside our button. Also note that `target.files` is an **array**. Here we're only interested in the first value as we're only uploading one file, but the same method can be used with multiple files !

<center>

![showing the file name in a button](https://cdn.hashnode.com/res/hashnode/image/upload/v1636904350691/JxJAKcamS.png?auto=compress)

</center>

### Form submission


Finally, we need a way to submit the data. For testing purposes I've created a small API in Flask you can find it in the [repository](https://github.com/jbrocher/file-upload-progress-bar) for this article. It's just a single endpoint that listens for POST requests and returns a 201.

Now, we can't POST our Data as json because we're want to send a file and json doesn't handle binary data. We need to send [form-data](https://developer.mozilla.org/en-US/docs/Web/API/FormData) instead. We'll use [axios](https://github.com/axios/axios) to send the request, as it comes in handy to display the progress as we'll see in the next section.

**Note**: *Alternatively, we could [encode our image in BASE64](https://stackoverflow.com/questions/6150289/how-can-i-convert-an-image-into-base64-string-using-javascript) and send it as a string in the json payload. Of course in that case we'd also need to decode it in the backend.*


```typescript

  const handleSubmit = async () => {
    const formData = new FormData();
    formData.append("title", formValues.title);
    formData.append("body", formValues.body);
    formValues.image && formData.append("image", formValues.image);

    const response = await axios.post(<YOUR-API-ENDPOINT>, formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });

    return response.data

  };

```

Several things are happening here : 
 - First we create a new `FormData` object;
 - Then we add our fomvalues to the data;
 - Finally we post it to our endpoint using the correct content headers



## Showing progress

Our form submisssion is working hooray ! But we're not done yet ! 


<center>

![Hooray](https://media.giphy.com/media/JNrWNUUNZlIhG/giphy.gif)

</center>

Maybe the image our user will posting are going to be heavy, and maybe we'll do some slow processing server side too. 
As it's probably gonna take some times to process the request, we'd like to show a progress bar.  

That's where Axios saves the day! It comes with two built-ins callback hook to process progress data: 
  - `onUploadProgress`: send event during the upload phase;
  - `onDownloadProgress`: during the download phase;

Now all we have to do is to create a new state variable to stor the progress value and monitor the requests states ! Might as well write this logic in a custom hook, as
we'll probably want to reuse it later. (It's also easier to read). Here's how this looks : 

```typescript

// hooks.ts

import { useState } from "react";
import axios from "axios";

export const useUploadForm = (url: string) => {
  const [isSuccess, setIsSuccess] = useState(false);
  const [progress, setProgress] = useState(0);

  const uploadForm = async (formData: FormData) => {
    setIsLoading(true);
    await axios.post(url, formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
      onUploadProgress: (progressEvent) => {
        const progress = (progressEvent.loaded / progressEvent.total) * 50;
        setProgress(progress);
      },
      onDownloadProgress: (progressEvent) => {
        const progress = 50 + (progressEvent.loaded / progressEvent.total) * 50;
        console.log(progress);
        setProgress(progress);
      },
    });
    setSuccess(true)
  };

  return { uploadForm, isSuccess, progress };
};

```

Here I made the choice to represent the progress as evenly distributed between the uplaod and download steps, but you're free to do as you please ! It all depends on what you 
want to display to your users. I've also added `success` boolean we can use to do some conditionnal rendering. 

Now all we have to do is use our custom hook to submit the form, and somehow display the progress value! I'm using [linear progress](https://mui.com/api/linear-progress/) for thatfrom Material UI here.


 ```typescript

const Form: React.FunctionComponent = () => {
  const { isSuccess, uploadForm, progress } = useUploadForm(
    "http://localhost:5000/post"
  );
  ...

  const handleSubmit = async () => {
    const formData = new FormData();
    formData.append("title", formValues.title);
    formData.append("body", formValues.body);
    formValues.image && formData.append("image", formValues.image);
    return await uploadForm(formData);
  };

}

...

const Form: React.FunctionComponent = () => {
  return (

    ...

    <Box marginY={3}>
      <Button onClick={handleSubmit}>Submit Post </Button>
      <LinearProgress variant="determinate" value={progress} />
    </Box>
  )
}

```


Here's what it looks like : 

![Progress Bar Demonstration](https://cdn.hashnode.com/res/hashnode/image/upload/v1636906969200/aYHOb-Czr.gif?auto=compress)

Pretty neat  !



## Bonus Round ! 

I thought it would be a nice addition to show how to display a little success message after the bar reach 100%.

To do so we'll use our `isSuccess` indicator. But first well add an artificial pause after the request complete to let he user
admire the progress bar reaching 100%. Otherwise React will merge the states updates and dipslay the success message before the progress bar has finished animating.

```typescript

//hooks.ts

  const uploadForm = async (formData: FormData) => {

    ...

    await new Promise((resolve) => {
      setTimeout(() => resolve("success"), 500);
    });
    setIsSuccess(true);
    setProgress(0);
  };

```

And now using `isSuccess` we can conditionnaly render a success message : 

```typescript


{ isSuccess ? (
  <Box color="success.main" display="flex">
    <CheckIcon color="success" />
    <Typography>Success</Typography>
  </Box>
  ) : (
  <>
    <Button onClick={handleSubmit}>Submit Post </Button>
    <LinearProgress variant="determinate" value={progress} />
  </>
)}
```

<center>

![Success message](https://cdn.hashnode.com/res/hashnode/image/upload/v1636908105155/WSu_9b6N_.gif?auto=compress)

</center>


## Conclusion 

That's it for today, hope you learned something ! I'd love to hear about how you handle form submissions in your React projects, [Let me know on Twitter](https://twitter.com/JiBRocher) ! 

## References 

1. [File API documentation](https://developer.mozilla.org/en-US/docs/Web/API/File)
2. [Axios](https://github.com/axios/axios#axios-api)
3. [Material Linear Progress Bar](https://mui.com/api/linear-progress/)

