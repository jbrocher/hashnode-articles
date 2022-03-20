# Authenticating and SPA with a REST API

## Introduction

 Authentication is something most web applications need, and that can be difficult to get right. Recently I had to implement it for a React app I was developing, and wanted to list the options available to me. So I did a bit of research and, to my surprise, I found it's really hard to get a straightforward answer on the proper way
 to implement authentication between an SPA and an API backend. 

 Since I had to do quite a bit of work to identify the distinct patterns I could choose from, I decided to compile them into an article so others could benefit from them! My goal 
 here is to provide you with a good starting point should you ever want your user to be able to authenticate with your SPA.


## Setting the context

Before diving deeper into the subject, it's important to have an idea of what we're trying to achieve and what we'd like to avoid. So let's review
what we mean by "Authentication", and the main kind of security issues we need to look out for. However, if you'd like to skip all that and go 
straight to the authentication patterns, [feel free to do so](#authenticating-with-an-spa) !

### The three aspects of "Authentication"

Usually when we talk about implementing some kind of Authentication system on an application, we're actually talking about
3 different concepts. In a monolithic app, these are rarely explicitly stated, because they're usually tackled at the same time. However,
as we'll see a bit later, some of the Authentication patterns available to SPA don't cover all of them, which means it's important 
to define them. These concepts are **Authorization**, **Authentication** and **Session**:

 - Authorization: Determining if an entity is allowed to perform a specific action. This doesn't necessarily mean we need to know **who** is performing the action. 
 - *Actual* Authentication: Knowing the identity of the user. For example their email address, username or any property that can be used to uniquely identify a user in 
 your domain of work. 
 - Session: Maintaining state for one or both of the above concepts


Keep that in mind, we'll refer to these definitions often throughout the article!

### 2 types of attack to avoid 

Now that we know what we want, let's review what we **don't** want. That is, security flaws that could allow an attacker to by 
pass our authentication system. There are an infinite possibilities when it comes to attacking an application, and no system can
claim to be completely secure. However, when building an authentication system, here are the ones we mainly need to worry about: 
 - Cross Site Request Forgery (CSRF);
 - and, Cross Site Scripting (XSS, I guess CSS was already taken) 

I'll quickly go over them, just so we can understand the mechanism we need to have in place to cover for these!

#### CSRF Attacks

These kind of attacks target authentication schemes that relies on cookies for storing credentials or session ID. They work by exploiting
the fact that cookies related to a domain are automatically sent by the browser for every request made to the domain. This allows malicious
website to set up forms designed to hit your application, and perform unwanted side-effects if your user is currently logged in. 

There is also another kind of "reverse" CSRF attack which specifically targets login form. In these kind of attacks, the malicious website logs in the browser 
with the *attacker account*. Then when the user goes back to your app, thinking they're logged in with their own account, the attacker can 
gain access to any sensitive data they enter.

It's important to note that CORS settings alone **do not** prevent CSRF attacks. Indeed, with the exception of pre-flighted requests, CORS doesn't
prevent the browser from making the request, it just prevents the response to be read by javascript.<sup id="1">[\[1\]](#ft1)</sup>

#### XSS Attacks

A Cross-Site Scripting Attack is a really wide category of attacks, where a malicious person manage to inject some foreign javascript
into your application. For example if you render some text coming from user input, without escaping potential HTML code, someone
could pretty much do whatever they want with your SPA. Specifically regarding authentication, they could read any sensitive information
stored in LocalStorage or SessionStorage, which is why you'll often read that you MUST not store session data into LocalStorage.<sup id="2">[\[2\]](#ft2)</sup> 

*As a side note, some argue that this is a non subject as if you're vulnerable to XSS attacks, you have bigger issues to deal with anyway. For example 
an attacker could simply modify a login form to send credentials directly to their own server. Personally I disagree entirely as I think security
measures should be self-contained and make no assumptions on the scale of the attack.*

---

### Authenticating with a monolith

One more thing : Before diving into the SPA world, I'd like to quickly review how it's done with a monolith. 
This way we'll have a reference point when talking about the specificities of SPA authentication. 

With a monolith, usually it works like this: 

<center>

![Monolith](https://media.giphy.com/media/cjyVveMCMgunS/giphy.gif)

<small> Wait, not that kind of monolith </small>

</center>


I mean like this:


 <center>

 ![Monolith Sequence Diagram](https://cdn.hashnode.com/res/hashnode/image/upload/v1649321115381/80w6rzhy0.png?auto=compress)

 <small>Monolothic auth sequence diagram</small>

 </center>

It's simple really: once the user submits their credentials, the server creates a stateful session. Then it mints an httpOnly cookie containing a session id, 
which will be sent with each subsequent request. Authentication is performed by storing an identifier in the session, and Authorization is checked 
by looking up the rigths/roles/permissions/whatever associated with the identity. The session is maintained natively by the browser and the cookie.


#### A word on CSRF

As outlined in the previous section, using a cookie makes the app vulnerable to CSRF attacks. Most frameworks have a built in  way to deal with it using 
a CSRF token mechanism similar to the one I've included into the sequence diagram. This is good, because building a CSRF token system is *hard* to do and *easy* to get wrong. 


## Authenticating with an SPA

All right, now that's out of the way, let's start with today's main subject.
I'm sure you're glad you've just read 800 hundred words not related in any way to SPAs, in an article about SPAs. 
But this was necessary, and now we'got all the context we need to review the available SPA authentication patterns in a constructive way! 


### Option 1: Stateful session with cookie

This is the simplest approach, and closely resembles the monolithical one. Here's how it looks : 

![SPA Stateful cookie](https://cdn.hashnode.com/res/hashnode/image/upload/v1649321222030/03F_wPU3C.png?auto=compress)

As with the monolithic architecture, the API creates a stateful session, and a Session Cookie 🍪, with the session ID. The only difference is that the UI is now provided 
by the SPA. It is a big difference though because: 
 - The SPA is *Authorized* to perform some actions on behalf of the user, but the user is only *Authenticated* with the API. Meaning the SPA doesn't know 
 the identity of the user. If you choose this pattern you'll have to create a dedicated route (something like `/me` or `/profile`) to fetch the identity of the 
 user. 
 - As we're now dealing with two different apps, for this approach to work you need to be able to share the cookie between them. This means they have to be hosted
 on the same domain
 - Since we're using a cookie, we're vulnerable to CSRF attack. However *contrary* to the monolothic approach where it's often handled by the framework, you 
 have to deal with it yourself. 

 #### Dealing with CSRF attacks

In this case there are two main ways to prevent CSRF attacks: 
  - Setting SameSite on the cookie: This prevents the browser from automatically sending it along with requests made from another domain. This is the recommended approach by the OAuth2 specs on browser-based application<sup id="3">[\[3\]](#ft3)</sup>. The only caveats is that this setting is only supported by recent browser versions, so users using outdated ones will be vulnerable!<sup id="4">[\[4\]](#ft4)</sup>
  - Manually setting up a CSRF mitigation method like a CSRF token. This can definetly work as outlined [in this article](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Set-Cookie/SameSite#browser_compatibility) but it's really easy to get wrong, so I'd use this option as a last resort.


#### Pros & Cons

**Pros**
 - Low cost of implementation 

**Cons**
 - Older browser are not protected by SameSite cookie, you need to manually implement CSRF
 - You must be able to share a domain with the server
 - Doesn't provide direct authentication for the SPA, you need to make another call to a dedicated API route.


### Option 2: Stateless JWT authentication

This pattern uses JWT to exchange authentication data. JWT is a standard for exchanging signed JSON data (signed, not secret !). If you want more details
about how JWT work, Auth0 has [a dedicated website with all the information you'll need](https://jwt.io/introduction). Here it's used to provide a stateless way to manage 
authentication in the SPA and authorization in the API: 

![JWT Sequence Diagram](https://cdn.hashnode.com/res/hashnode/image/upload/v1649321585788/0p6NIe-aM.jpg?auto=compress)

Pretty straightforward, the credentials are exchanged against a JWT that contains : 
 - An Access Token used as a bearer token for authorization
 - A Refresh Token for when the Access Token expires
 - The identity of the user (often under the "sub" key of the json data)

This kind of authentication isn't as exposed to CSRF attacks if you don't store the JWT inside a cookie. 


#### What about session

Maintaining session is problematic in this case. As explained earlier, we can't just store the Refresh Token inside the local storage, as it's vulnerable to XSS attacks. You
could store it inside an HttpOnly cookie, but you lose the ability to *authenticate* the user with the JWT in the SPA. In that case I'd recommend using option 1 instead if possible, as it is more battle tested and easier to implement.

There is a way to give the illusion of maintaining an active session, but it requires a more complex approach, that is outlined in the next section.

#### Pros & Cons


**Pros**
 - Provide both Authorization and Authentication of the SPA
 - Stateless which *may* improve performance depending on your architecture. For example by saving a database lookup. 

**Cons**
 - Can't really maintain session in a secure way


### Option 3: OpenID connect


OpenId Connect is an extension of the OAuth2 authorization framework that adds authentication capabilities to it. 

OAuth2 was originally meant to allow a third-party app
to perform actions in a main application on behalf of the user. Like posting comments on Facebook, or publishing a tweet. This means that "third-party" here is defined from the point of view of the end user. As in "I don't want to give my Facebook password to this random application, but I'd like to allow it to publish status on my behalf". The goal is 
to give the third-party app an Access Token signed by the authentication server (Facebook in our example). This doesn't take care of *authenticating* the user. 

<center>

![who are you](https://media.giphy.com/media/ScFZKpCFoTIblL4Epu/giphy.gif)

<small>Can't answer that with authorization alone !</small>

</center>

Authentication is enabled by the OpenId Connect protocol that adds a standard for returning an identifier for the user along the access token, that can be decoded and used
by the third party app. 

In our case, it can be used by our SPA to Authenticate the user against our API and get an access token to perform some actions. Our SPA *is not* a third-party as defined by OAuth2 since our user doesn't even need to know that the SPA and the API are two different things. However it allows us to treat our API as an authentication service for our
spa which has several benefits:
 - It scales better in case you DO want to authenticate from other third-party services. 
 - It allows you to isolate your login form making it more secure
 - It allows the implementation of a Silent Authentication for maintaining sessions 

 Here's how it looks:

![OpenId connect](https://cdn.hashnode.com/res/hashnode/image/upload/v1649336853356/1-hPW3ycj.jpg?auto=compress)


It's important to note that there are several possible authentication flows when using OpenId Connect. Currently the flow that must be used by SPAs is the Authorization Clode Flow with Proof Key for Code Exchange. I won't describe it here, instead I'll do you one better and link to the awsome Auth0 article that goes into . I *strongly* recommend you do not try to implement this yourself as it's time consuming, and easy to get wrong. Instead use the recommended lib
from you framework. For example if you're using the great Django Rest Framework, you can easily add OAuth2/OpenID Connect capabilities with [Django Oauth Toolkit for DRF](https://www.django-rest-framework.org/api-guide/authentication/#django-oauth-toolkit)


#### Maintaining Session

As explained, it is not safe to store the tokens returned by the OpenID Connect flow in the browser. Instead, since you can make use of a [Silent Authentication Flow](https://auth0.com/docs/authenticate/login/configure-silent-authentication). It works by setting a cookie on the Authentication Server and not prompting the user for their credentials
if they are already logged in. CSRF is still an issue here, but since it only concerns the login form, you can use your API framework CSRF token system to mitigate, which is 
quite easy in most cases.

#### Pros & Cons

Pros: 
 - The most flexible set up as you can use it to authenticate third-party App
 - Allows the use of federated identiy provider By proxying other Open id provider like Facebook or Google
Cons: 
 - More costly to implement and hard to get right without using a trusted Framework / Library
 - I you use a dedictated authentication provider, you might need to subscribe to a paying plan


### Backend For Frontend

There is one alternative I haven't listed yet, that opens up new possibilities and new authentication flows. It is the "Backend For Frontend" architecture pattern, which 
means serving your SPA from a server that can also run code. For example a Meta-Framework like NextJS, or just a regular server that happens to also statically serve your app. 
Using this solution changes a lot of things. For example, it might be easier to manually mitigate CSRF threats in option 1, or use a cookie to store the tokens created in Option 2. 

However I won't go into the details here, beyond the scope of just choosing and Authentication Solution. Instead I might write 
a dedicated article listing the patterns associated with this architecture

In the meantime, the OAuth2 spec has a [great section](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-browser-based-apps#section-6.2) on the subject if you'd like to know more. 

### Auth provider

Finally, As we've seen with the previous patterns, Authenticating an SPA is not as straightforward as it should be. If you don't want to invest too much time
looking for the perfect solution, you can always use an Authentication and Authorization SaaS. Most of them come with out-of-the-box integrations 
with both you SPA and your framework of choice, which can save you a lot of time. Of course, even though most of them offer a free plan, you might need to purchase
a paying subscription as your user base grows.

Most of them rely on OpenID Connect behind the scenes, meaning the integration with your SPA and your API usually look like this:

 ![Auth Provider Sequence Diagram](https://cdn.hashnode.com/res/hashnode/image/upload/v1649323779155/8pK63Whlg.jpg?auto=compress)


- Here are a few examples that provide a great DX: 
 - [Auth0](https://auth0.com/docs/get-started/auth0-overview): Awesome service, and great documentation. However it quickly gets expensive;
 - [Firebase auth]: GCP authentication solution. Interesitingly they seems to store some token in IndexDB which is not XSS safe; 
 - [AWS cognito]: AWS identiy management solution. Might be a good solution if you're already using AWS;
 - [Keycloack](https://www.keycloak.org/): Open source, yay! 



## Conclusion

As often when it comes to programming, there is no silver bullet for handling Authentication with SPAs. With this article I hope to give you 
some insight into what's possible so you can find a solution that best suit your needs. And to make this easier, 
I've compiled what we covered into this handy chart, I hope it helps you in your conception work, it certainly helped me!

![Auth patterns comparison chart](https://cdn.hashnode.com/res/hashnode/image/upload/v1649429989568/eFVYYwWVg.png?auto=compress)

I might write some dedicated tutorials on one or more of this pattern so stay tuned !


--- 
### References

1. <span id="ft1">[MDN CORS documentation](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)</span>
2. <span id="ft2">[The issues with using jwt for maintaining sessions](http://cryto.net/~joepie91/blog/2016/06/13/stop-using-jwt-for-sessions/)</span>
3. <span id="ft3">[OAuth2 for browser-based apps](https://tools.ietf.org/html/draft-ietf-oauth-browser-based-apps)</span>
4. <span id="ft4">[SameSite cookies](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Set-Cookie/SameSite#browser_compatibility)
5. [Auth0 which auth flow](https://auth0.com/docs/get-started/authentication-and-authorization-flow/which-oauth-2-0-flow-should-i-use)
6. [Mitigating CSRF in spas](https://medium.com/tresorit-engineering/modern-csrf-mitigation-in-single-page-applications-695bcb538eec)
