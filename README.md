# Bring your own training-completed model with SageMaker by building a custom container


[Amazon SageMaker](https://aws.amazon.com/sagemaker/) provides every developer and data scientist with the ability to build, train, and deploy machine learning models quickly. Amazon SageMaker is a fully-managed service that covers the entire machine learning workflow to label and prepare your data, choose an algorithm, train the model, tune and optimize it for deployment, make predictions, and take action. Your models get to production faster with much less effort and lower cost.

In this session, you will build a custom container which contains a train-completed Pytorch model, and deploy it as a SageMaker endpoint. Your model is trained elsewhere like on premise perhaps, and you only want to use SageMaker to host the model. The session teaches how to do that. Pyorch/fast-ai model is provided for learning purposes. Once you know how to deploy a custom container with SageMaker, you can use the same approach to deploy the model trained with other machine learning framework.


## When should I build my own algorithm container?

You may not need to create a container to bring your own code to Amazon SageMaker. When you are using a framework (such as Apache MXNet or TensorFlow) that has direct support in SageMaker, you can simply supply the Python code that implements your algorithm using the SDK entry points for that framework. This set of frameworks is continually expanding, so we recommend that you check the current list if your algorithm is written in a common machine learning environment.

Even if there is direct SDK support for your environment or framework, you may find it more effective to build your own container. If the code that implements your algorithm is quite complex on its own or you need special additions to the framework, building your own container may be the right choice.

If there isn't direct SDK support for your environment, don't worry. You'll see in this walk-through that building your own container is quite straightforward.


## Example

We will show how to package a simple Pytorch image classification model which classifies types of recycle item. For simplification, there are 3 categories of recycle item, paper, glass bottle, and plastic bottle. The model predicts the image passed on is any of the 3 categories.   

The example is purposefully fairly trivial since the point is to show the surrounding structure that you'll want to add to your own code to host it in Amazon SageMaker.

The ideas shown here will work in any language or environment. You'll need to choose the right tools for your environment to serve HTTP requests for inference, but good HTTP environments are available in every language these days.

## Contents of the solution


- **build_and_push.sh** is a script that uses the Dockerfile to build your container images and then pushes it to ECR. The argument you pass here will be used as your ECR repository name. 
- **Dockerfile** describes how to build your Docker container image, and specifies which libraries and frameworks to be installed to host your model. If your model is trained with frameworks other than Pytorch and fastai, you will update this file.  
- **lambda_function.py** contains the code that downloads a test image from a S3 bucket, and then invokes the SageMaker endpoint sending the image for an inference. You will paste this code to your Lambda function after the endpoint creation is done. 
- **data folder** contains test images. You will upload those images to your S3 bucket.
- **model folder** contains the compressed Pytorch/fastai image classification model. You will upload the tar.gz file to your S3 bucket.
- **image_classification** folder contains the following files that are going to be copied into the Docker image that hosts your model.
    - **nginx.conf** is the configuration file for the nginx front-end. No need to modify this file and use it as-is.
    - **serve** is the program that starts when the container is started for hosting. It simply launches the gunicorn server which runs multiple instances of the Flask app defined in predictor.py. No need to modify this file and use it as-is.
    - **wsgi.py** is a small wrapper used to invoke the Flask app. No need to modify this file and use it as-is.
    - **predictor.py** is the program that actually implements the Flask web server and the image classification predictions. Amazon SageMaker uses two URLs in the container:
        - **/ping** will receive GET requests from the infrastructure. The program returns 200 if the container is up and accepting requests.
        - **/invocations** is the endpoint that receives client’s inference POST requests. The format of the request and the response depends on the algorithm. For this blog post, we will be receiving a JPEG image and the model will classify which type of recycling item it is. It returns the results text in a JSON format.



    ![archDiagram](./images/archDiagram.jpg)

## Prerequisites for the Workshop

- Sign up for an AWS account


## Workshop Roadmap

- Launch EC2 instance.
- Create a model object on SageMaker.
- Create an endpoint configuration on SageMaker.
- Create an endpoint.
- Create a Lambda function to test your endpoint.


## Launch Jupyter Notebook Environment on Amazon SageMaker

1. Click on **Amazon SageMaker** from the list of all services by entering Sagemaker into the **Find services** box. This will bring you to the Amazon SageMaker console homepage. 

1. To create a new Jupyter notebook instance, go to **Notebook instances** in the Amazon SageMaker console, and click the **Create notebook instance** button at the top of the browser window.

    ![sagemakerCreateNotebook](./images/sagemakerCreateNotebook.png)

1. Type *Custom-Container-Workshop* into the **Notebook instance name** text box, and then *ml.m5.2xlarge* into the **Notebook instance type**. Note, there is not need to launch a large, compute-optimized C5 or GPU-based instance type.

    ![sagemakerCreateNotebook2](./images/sagemakerCreateNotebook2.png)

    On the **Permission and encryption** section of the same page, choose **Create a new role** from the dropdown list. It will bring up the following popup window. Here, you can specify your S3 bucket or choose *Any S3 bucket* if you don't have S3 bucket created yet. For security purposes, we always recommend to choose *Specific S3 bucket* option but for the purpose of the lab, you could choose *Any S3 bucket*.  

    ![sagemakerCreateNotebook3](./images/sagemakerCreateNotebook3.png)

    Lastly on this wizard, scroll down to the **Git repositories** section and choose *Clone a public Git repository to this notebook instance only* option. Then enter the URL of this workshop as shown below. Click on **Create notebook instance** button. 

    https://github.com/rumiio/SageMaker_Custom_Container.git   

    ![sagemakerCreateNotebook4](./images/sagemakerCreateNotebook4.png)

＃TODO: add these permissions is simply to add the managed policy AmazonEC2ContainerRegistryFullAccess to the role that you used to start your notebook instance.


1. Wait until the notebook instance status is **InService**. This will take a few minutes once the creation process has started. Then click on **Open Jupyter**.

    ![sagemakerCreateNotebook5](./images/sagemakerCreateNotebook5.png)