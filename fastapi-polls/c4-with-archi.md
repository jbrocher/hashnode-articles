## Introduction

Recently, I decided the time had come for an overhaul of the way we handle software architecture in my team. As our numbers grow, we had an urgent need for tools and processes that allowed us to keep our agility, while offering strong guarantees on the quality of our codebase.

After some research, I settled on a process based on the [C4 model](https://c4model.com/) and [Archi](https://www.archimatetool.com/). I am quite satisfied with it, so I figured I'd share it! First we'll go over what thoses tools are, and how to use them. Then we'll apply them to a pratical example: Modeling the Poll App from [my on going FastAPI tutorial](https://dev.indooroutdoor.io/the-poll-app-from-django-tutorial-with-fastapi-and-react-1)! 

*The models for the poll app are also available in [this repository](https://github.com/jbrocher/poll-app-archi)*


##  📋 The specificiations

First let's go over our needs. We're looking for a software architecture method with the following characterisitcs : 
 - Flexible enough to be used in an agile environment
 - Easy to adopt for both senior and junior developers
 - Collaborative
 - Reusable and Maintainable

I feel the last point is most difficult to attain. Without the right tools,  it's hard for a team to go beyond the initial drawing created during the conception phase, and actually maintain a model representative of the current codebase.

With that in mind, let's see how the C4 + Archi combination fits the bill ! 


## 🔧 The tools


### The C4 model 

So what is the C4 model ?

The [C4 model](https://c4model.com/) is a set of software architecture viewpoints designed by [Simon Brown](https://twitter.com/simonbrown). The official documentation (which I encourage you to read  👓) describes it as : 
> The C4 model is an "abstraction-first" approach to diagramming software architecture, based upon abstractions that reflect how software architects and developers think about and build software.


A C4 model for a given system is composed of 4 diagrams, representing 4 different levels of abstraction. Each lower level diagram "zoom in" on a concept from the previous higher level one. Here's a brief description of each of them:  

- **Context Diagram**: This is the most abstract level. It shows how a system interacts with its users and other systems

- **Containers Diagram**: Shows the runtimes that power the system. For example a database is a container.

- **Components Diagram**: Displays the logical units that make up a container and their relationships. What a "logical unit" is depends on the use case, and what you're trying to show in this diagram. 

-  **Code Diagram**: This would show the exact implementation of each component. However it would be really tedious to maintain. Instead, this is where the expertise of the engineering team and the best practices in place should kick in. 


<center>

  ![The C4 model](https://cdn.hashnode.com/res/hashnode/image/upload/v1635926716300/tSOz29bCb.png?auto=compress)



  <small>*The 4 levels of the C4 model*</small>


</center>


**A note on UML**

You might notice some similarities with the Unified Modeling Language. While it serves a similar purpose, the C4 model is simpler and way more flexible, which it makes its adoption by a team more likely. 

This is actually my issue with UML. While its extensive specification might sound good in theory, in practice it is quite heavy to use. In my opinion, unless you're working with a waterfall methodology with a long period dedicated to creating the models, and tools that can auto-generate code from UML, the payoff is jut not worth the trouble. 

Of course this doesn't prevent you from using complementary diagrams coming from UML if you'd like to. Personnaly I find the [Sequence Diagram](https://en.wikipedia.org/wiki/Sequence_diagram) often comes in handy !



### Archimate & Archi

Now that we've talked about the model (or rather meta-model, as the C4 is a tool for building models), let's see how we can go about producing the diagrams. Remember that we want actual modeling capablilites here, not a simple drawing tool. [Simon explains it well](https://c4model.com/#Modelling), modeling allows to easily reuse the same concepts across different views, and enable a static analysis of your architecture. 


To generate our models we'll use the following: 

 - [Archimate](https://www.archimatetool.com/#) : It is an open specificiation modeling language. This is the language that our models will be written in. 
 - [Archi](https://www.archimatetool.com/#): an archimate editor. This makes working with archimate models super easy ! 
 ![Achi](https://cdn.hashnode.com/res/hashnode/image/upload/v1635926684052/Rzfd8uLWL.png?auto=compress)


 What I love about Archimate and Archi, is that it maintains a clear separation between model and view, while still offering a great WYSIWG editor. 


## 🎓 The Methodology

Now that we've got the tools, let's see about using them !

### Collaboration and Versionning

First of all, for our models to be maintainable, we need to be able to collaborate on them. The great thing about using a modelling langage like archimate instead of boxes and arrows, is that we can version our architecture.  All we need to do is to store our models in repositories and we can even create pull request to discuss the changes !

The only issue is that the archimate files genreated by Archi aren't very git friendly. Each model is stored in a huge .xml file which can makes conflicts really hard to solve. Luckily, there is a plug-in that can take care of that for us : [CoArchi](https://github.com/archimatetool/archi-modelrepository-plugin/wiki). CoArchi put each archimate concept into its own file, making PR way easier to read !


### Using the C4 meta-model in Archi 

So now we can collaborate, but how do we actually create the C4 diagram in Archi? 

Our method for this is heavily inspired by this [excellent article](https://www.archimatetool.com/blog/2020/04/18/c4-model-architecture-viewpoint-and-archi-4-7/), which explains how to map Archimate concepts to the C4 meta model. We can actually save these Mapping in a dedicated model, and use a view as a toolbox from where we can copy paste the C4 building blocks as needed. Here is the end result :


 <center>

 ![ToolBox](https://cdn.hashnode.com/res/hashnode/image/upload/v1635929287462/tbtGcryaD.png?auto=compress)

 </center>

  - The C4 **persons** are maped to an archimate **business actors**
  - The C4 **software systems** and containers are mapped to archimate **application components**
  - The C4 components are mapped to **application functions**



### Extending the C4 model

I won't go into too much details here, because it really depends on your organisation, but I think it's good to extend the C4 model with your own set of rules to better suit you needs. 

For example in my team we agree on the following : 
 - In containers diagrams relationship must include the protocol (HTPPS, SSH..) used by the containers to communicate
 - In the component diagrams the presence of a relationship between component alwasy imply the existence of a public api/method/attribute

 We even have special rules for describing React apps: 
  - Coumpound components are described using composition relation ship
  - .. on so on. 

## Putting everything in practice

Finally let's have a look at a concrete example. Here's how I would describe the architecture of the Poll app from my [FastAPI tutorial](https://dev.indooroutdoor.io/the-poll-app-from-django-tutorial-with-fastapi-and-react-1), using the methods outlined in this article. 

**The Context**

First let's describe the context for our Poll App. In a real life situation I would discuss this diagram with my Product Manager to be sure we are aligned on the systems affected by the project: 

<center>

 ![System Diagram](https://cdn.hashnode.com/res/hashnode/image/upload/v1635929821232/vVXP1CB1d.png?auto=compress)
  <small>*Context Diagram*</small>

 </center>


 This is pretty self explanatory, here our Poll App is used by both an administrator responsbile for creating the polls, and the end user that answer them. I've also included an imaginary "stats app" to show inter system relationships.


 **The Poll App container**

 Now let's zoom in and explore which containers are necessary for our app. Here we decide what kind of technologies will be necessary for our projects,
 and how everything will interacts. 

 <center>

  ![Container Diagram](https://cdn.hashnode.com/res/hashnode/image/upload/v1635930891270/rkchp5K5E.png?auto=compress)
  <small>*Container Diagram*</small>

</center>

In this case we're using a rather classic paradigm with an API hosting the business logic and an UI handled by SPAs.



 **The Poll Api components**

 Let'ts zoom agin, this time on the API container. In a real life scenario, depending on the complexity of the SPAs, I'd also create a 
 component Diagram for the UI containers. 

 <center>

   ![Component Diagram](https://cdn.hashnode.com/res/hashnode/image/upload/v1635931596637/-PU8eajVf5.png?auto=compress)
   <small>*Component Diagram*</small>

</center>

To be honest,  this one feels a bit overkill for our Poll APP,  as it is a very simple use case. Usually in situation with more complex business logic to implement, I'd probably have a single CRUD component. 

## Conclusion 

Thanks for reading, I hoped you found this article useful ! How do your team handle Software Architecture in an agile environment ? Let me know in the comments or on [Twitter](https://twitter.com/JiBRocher) !


## References 

1. [C4 model website](https://c4model.com/)
2. [Archimate](https://www.opengroup.org/archimate-forum/archimate-overview)
3. [Archi](https://www.archimatetool.com/)
4. [Archi Collaboration Plugin](https://github.com/archimatetool/archi-modelrepository-plugin/wiki)
