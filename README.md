# Nightly Marvel Movie Message
## Using AWS Lambda and Amazon Pinpoint
<br />

This tutorial will step you through how to set up a service that sends a text
message on a schedule using AWS.

# Table of Contents

1. [The Plot](#the-plot)
2. [Disclaimers](#disclaimers)
3. [Service Overview](#service-overview)
* [AWS Lambda](#aws-lambda)
* [Amazon Pinpoint](#amazon-pinpoint)
* [Amazon CloudWatch](#amazon-cloudwatch)
* [Amazon IAM](#amazon-iam)
4. [Setup](#setup)
5. [The Tutorial](#the-tutorial)
* [Setting up a Pinpoint Long Code](#setting-up-a-pinpoint-long-code)
* [Creating the Lambda Function](#creating-the-lambda-function)
* [Adding Code and Testing the Lambda Function](#adding-code-and-testing-the-lambda-function)
* [Modifying the Lambda IAM Role](#modifying-the-lambda-iam-role)

6. [Adding a CloudWatch Event](adding-a-cloudwatch-event-to-automatically-trigger-the-lambda-function)
7. [Cleaning Up](cleaning-up)
8. [The End](#the-end)


<br />

# The Plot

You were asked by a friend to watch a different Marvel movie every night this
week. You aren't sure which order to watch them in, and don't really want to
ask.

So, you decide to set up a text message service to text you the name of
a random Marvel movie to watch each night at 7pm.

<br /><br />

The services we will use are as follows:
<br />

* AWS Lambda, to execute code without needing to rent out a server
* Amazon Pinpoint, to allow us to send texts from a consistent phone number
* AWS CloudWatch, to set a scheduled alarm to trigger our Lambda code
* AWS IAM, which allows the Lambda function permission to send messages via Pinpoint

<br /><br />

# Disclaimers
This tutorial is NOT free!! It is **very inexpensive** (~$1).

An Amazon Pinpoint long code costs $1 a month for
a dedicated long code, and SMS messages sent in the USA are $0.00645 each as of
this writing.

These costs are relatively low, but I want to make it clear that this tutorial
is not completely free.

There are opportunities for students to get [AWS credits](https://aws.amazon.com/blogs/aws/aws-educate-credits-training-content-and-collaboration-for-students-educators/)
through [AWS Educate](https://aws.amazon.com/education/awseducate/).

There are compute charges for AWS Lambda, but this tutorial uses very little, so
it is all within the [free tier](https://aws.amazon.com/free/).

AWS IAM is a service that is provided at [no cost](https://aws.amazon.com/iam/faqs/#Pricing).

AWS CloudWatch Event Rules are also [free](https://forums.aws.amazon.com/message.jspa?messageID=699878).

I will describe how to turn off resources at the end of this lab. Note that
Pinpoint is the only service that will incur recurring costs, as IAM and
CloudWatch Event Rules are free and with Lambda, you only pay when you execute
code. You never have to pay for IAM users, roles, CloudWatch Rules, or Lambda
functions that are sitting around doing nothing.

If you are interested in a free tutorial, I may build out a similar tutorial
using [AWS SNS](https://docs.aws.amazon.com/sns/latest/dg/sns-lambda-as-subscriber.html)
in the future, which has a more inclusive free tier than Pinpoint

There are also some free services which can do similar things to this, like [IFTTT](https://ifttt.com/)


<br /><br />
# Service Overview
## AWS Lambda
AWS Lambda is a serverless compute service offered by AWS. By serverless, it
doesn't mean the code is executed on elephants, but rather that you don't have
to worry about spinning up a whole computer, installing the operating system,
installing libraries, and then executing a few dozen lines of code, then
turning it back off after all that. AWS takes care of all of that for you!

AWS lets you use Lambda for free for 400,000 GB-seconds and 1,000,000 invokes.
This means that it is incredibly easy to experiment with it for absolutely no
cost!

See more information [here](https://aws.amazon.com/lambda/faqs/).
<br /><br />

## Amazon Pinpoint
Amazon Pinpoint is a service that is aimed primarily at marketing, and allows
users to use AWS to send out text messages, emails, or push notifications to
their customers to communicate with their end users and measure user engagement.

We'll be using it to configure a long code, which is just a dedicated phone
number that we can text people from using AWS Lambda.

See more information [here](https://aws.amazon.com/pinpoint/faqs/).
<br /><br />

## Amazon CloudWatch
Amazon CloudWatch Events is able to generate events on a schedule you set by
using the popular Unix cron syntax. By monitoring for these events, you can
implement a scheduled application.

See more information [here](https://aws.amazon.com/cloudwatch/faqs/).

## Amazon IAM
You can use AWS IAM to securely control individual and group access to your AWS
resources. You can create and manage user identities ("IAM users") and grant
permissions for those IAM users to access your resources.

See more information [here](https://aws.amazon.com/iam/faqs/).

# Setup

The first thing you'll need to do is create an AWS account
https://portal.aws.amazon.com/billing/signup#/

Once you have that set up, you can optionally create an admin user for best
practice in IAM. This isn't a necessary step, but it is considered bad practice
to use the root account (the one that's made when you created your AWS account)
to provision resources.
https://docs.aws.amazon.com/IAM/latest/UserGuide/getting-started_create-admin-group.html
https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html


## Selecting a Region

The next thing we need to do after creating our AWS Account, is select the
region in which our services will live. This isn't a permanent change!  It's
really easy to change your region in the AWS Console, but it's sometimes easy to
forget which region you are in. Be sure to choose your region at the start, and
if you can't find a resource, make sure you are in the right region!

For this project, we will be using Amazon Pinpoint, which is available in the US
only in N. Virginia and Oregon regions as of this writing (2020/06/06). So,
click on the region select in the upper right corner and ensure you are in one
of those two regions.

<br />
<img src="/Screenshots/PinpointSupportedRegion.png" alt="Pinpoint Supported Regions" width="400"/>
<br /><br />

**TODO:** Which new one is better? This one?
<br />
<img src="/Screenshots/AWSRegionSelectRedBox.png" alt="Region Select Red Box" width="900"/>
<br /><br />

Or this one?

<br />
<img src="/Screenshots/AWSRegionSelectRedBoxPlusArrow.png" alt="Region Select Red Box Plus Arrow" width="900"/>
<br /><br />


# The Tutorial

We'll start by creating an Amazon Pinpoint project and making a Lambda function.
Then, we'll make a quick modification to the Lambda's IAM Role and set up
CloudWatch. It's as simple as that!


## Setting up a Pinpoint Long Code

First, we are going to set up a long code in Amazon Pinpoint to eventually be
able to text from with our Lambda function.
<br />

To make a new Amazon Pinpoint project, first ensure you are at the AWS Management
Console. If you don't see this page, click on the AWS logo in the upper left corner.

<br />
<img src="/Screenshots/AWSManagementConsoleHome.png" alt="AWS Management Console" width="900"/>
<br /><br />

Type in "Pinpoint" in the search bar and click on the first result to navigate
to Amazon Pinpoint.

<br />
<img src="/Screenshots/PinpointSearchManagementConsole.png" alt="Pinpoint Search" width="900"/>
<br /><br />

Now, we're going to create a project in Amazon Pinpoint and provision a long
code. When you first open the Pinpoint dashboard, it will look like the following.

<br />
<img src="/Screenshots/EmptyPinpointProjects.png" alt="Pinpoint Empty Dashboard" width="900"/>
<br />

To create a new project, simply type in a name and click "Create a project".  
I've chosen to name mine MarvelTextPinpoint.

<br />
<img src="/Screenshots/NamedNewPinpointProject.png" alt="Pinpoint New Project" width="900"/>
<br />

Next, click on the button to configure SMS and Voice for your project.

<br />
<img src="/Screenshots/PinpointConfigureSMS.png" alt="Pinpoint SMS No Long Code" width="900"/>
<br />

Check the box next to "Enable the SMS channel for this project" and click "Save changes"

<br />
<img src="/Screenshots/PinpointEnableSMS.png" alt="Pinpoint Enable SMS" width="900"/>
<br />

Then click settings, and then SMS and Voice to manage your long codes.

<br />
<img src="/Screenshots/PinpointSMSNoLongCode.png" alt="Pinpoint SMS No Long Code" width="900"/>
<br />

Click "Request a Long Code", and it'll take you to a page that looks like this.

<br />
<img src="/Screenshots/ProvisionLongCodeNoCountry.png" alt="Pinpoint Long Code No Country" width="900"/>
<br />

Type in "United" and click United States. The page will update as follows.

<br />
<img src="/Screenshots/TransactionalRadioButton.png" alt="Pinpoint Long Code Country Transactional" width="900"/>
<br />

Click the radio button that says "Promotional". This tells our Pinpoint project
that our messages are non-critical to our business function.

<br />
<img src="/Screenshots/RequestLongCodesWithButton.png" alt="Request Long Codes Button" width="900"/>
<br />

Then, hit "Request long codes", and it should take you back to the SMS and Voice page.

<br />
<img src="/Screenshots/PinpointSMSandVoiceWithLongCode.png" alt="Pinpoint with Long Code" width="900"/>
<br />

This is just about the end of what we need from Amazon Pinpoint. Click on "All
Projects" to view all of the projects.

<br />
<img src="/Screenshots/PinpointSMSandVoiceWithLongCodeRedBox.png" alt="Pinpoint All Projects Red Box" width="900"/>
<br />

Now, **copy the Project ID to a text editor** to be able to reference in our Lambda
function later.

<br />
<img src="/Screenshots/PinpointAllProjectIDs.png" alt="Pinpoint Project IDs" width="900"/>
<br />
<br />


## Creating the Lambda Function
<br />

Click on the "Services" tab in the upper left and type in "Lambda" to get to
AWS Lambda.

<br />
<img src="/Screenshots/PinpointAllProjectIDsCroppedServices.png" alt="Service Button in upper left" width="600"/>
<br />


<br />
<img src="/Screenshots/SearchServicesLambda.png" alt="Searching for AWS Lambda" width="900"/>
<br /><br />

When you arrive at the Lambda service page, you should see a page that looks
empty. Click "Create Function".

<br />
<img src="/Screenshots/LambdaEmptyFunctionFolder.png" alt="Empty Lambda Folder" width="900"/>
<br /><br />

You should see this screen. We'll be authoring our function from scratch - don't
worry, I've provided some code below so it's not really from scratch.

<br />
<img src="/Screenshots/LamdbdaFirstScreenPic.png" alt="Create a Lambda Function" width="900"/>
<br /><br />

You can name your Lambda function almost anything you want. I've chosen to name
mine MarvelMovieProject.

<br />
<img src="/Screenshots/LambdaNameProjectPic.png" alt="Naming the Lambda Project" width="900"/>
<br /><br />

Next, click the "Runtime" dropdown to change the language specified to Python 3.8

<br />
<img src="/Screenshots/LambdaSelectPythonPic.png" alt="Select Python as the Language" width="900"/>
<br /><br />

Finally, if you want, you can check the dropdown "Choose or create an execution
role" to ensure that "Create a new role with basic Lambda permissions".

Then, click "Create function" in the lower right corner.


<br />
<img src="/Screenshots/LambdaRoleCreatePic.png" alt="Lambda Role Creation" width="900"/>




You may have to wait a few seconds after hitting "Create function" before the
Lambda editor is available. Here is what you should see.

<br />
<img src="/Screenshots/LambdaEmptyEditor.png" alt="Empty Lambda Editor" width="900"/>
<br />

## Adding Code and Testing the Lambda Function


When it is available, scroll down to the Function
Code section. This is where you can insert the Python code that will make this
function work.

<br />
<img src="/Screenshots/LambdaFunctionCodeEmpty.png" alt="Empty Lambda Editor" width="900"/>
<br />

The code for this function is included here as well as in "TextCode.py"

### See Code Below!
<details>
  <summary>Click to see/hide code!</summary>
  <p>

  ```
  import json
  import boto3
  import random

  # boto3 is a Python client  used by AWS https://aws.amazon.com/sdk-for-python/
  pinpoint = boto3.client('pinpoint')

  def lambda_handler(event, context):
      messages = ["Captain America: The First Avenger",
                  "Iron Man",
                  "Thor Ragnarok",
                  "Avengers: Infinity War",
                  "Avengers: Endgame",
                  "Black Panther",
                  "Guardians of the Galaxy"
                  ]

      Message = random.choice(messages) # Pick a random movie to watch

      pinpoint.send_messages(
          ApplicationId='COPY_APPLICATION_ID_FROM_AWS_PINPOINT',
          MessageRequest={
              'Addresses': {
                  '+1XXXXXXXXXX': {'ChannelType': 'SMS'}
              },
              'MessageConfiguration': {
                  'SMSMessage': {
                      'Body': Message,
                      'MessageType': 'PROMOTIONAL'
                  }
              }
          }
      )
  ```
  </p>
</details>

<br />

Copy and paste this code into the Lambda function Editor. The code provided has
a lambda_handler function which will execute when the Lambda function is invoked.

It then invokes Pinpoint to send a **message** to a given **phone number**

Replace the Pinpoint ApplicationID with the ID you copied earlier. Then, replace
the phone number with your phone number. Then, click the Save button in the
upper right corner.

<br />
<img src="/Screenshots/LambdaEditorWithCode.png" alt="Lambda Editor With Code" width="900"/>
<br />

Next, we are going to test the Lambda function to see if we can send a text!

<br />
<img src="/Screenshots/LambdaConfigureTestEvent.png" alt="Lambda Configure Test" width="900"/>
<br />

No need to change anything about the test, just name it something - I chose
"MarvelTest". Then, hit "Create"!

<br />
<img src="/Screenshots/LambdaConfigureTestEventNamed.png" alt="Lambda Configure Test Named" width="900"/>
<br />

It should bring you back to this screen - hit Save in the upper right again.

<br />
<img src="/Screenshots/LambdaTestCreated.png" alt="Lambda Test Created" width="900"/>
<br />

Now, we are ready to test our Lambda function and send our first text message!
Hit the "Test" button that's right next to "Save".

<br />
<img src="/Screenshots/TestPermissionsError.png" alt="Test Permissions Error" width="900"/>
<br />

Oh no! You hit the test button too hard! Just kidding, this was supposed to happen.
Let's take a closer look at why our test failed. I hope it wasn't my code...

<br />
<img src="/Screenshots/TestPermissionsErrorExplained.png" alt="Test Permissions Error Explained" width="900"/>
<br />

I highlighted the most important information in some boxes. Specifically,
it looks like there was an AccessDeniedException. That means that an IAM user or
role was denied permissions to do something by IAM.

The IAM role in question is the default one that was created when we first
created our Lambda function. It is being denied the action mobiletargeting:SendMessages
on a specific resource, mobiletargeting, which is our Pinpoint Project.

Let's fix that now.

<br /><br />


## Modifying the Lambda IAM Role

We need to navigate to the IAM Console. Click on the "Services" tab in the upper
left, type in "IAM", and press Enter.

<br />
<img src="/Screenshots/TestPermissionsErrorServices.png" alt="Test Permissions Service Tab" width="900"/>
<br />

<br />
<img src="/Screenshots/ServiceSearchIAM.png" alt="IAM Service Search" width="900"/>
<br />


You'll come to a screen that looks like the following. Click on "Roles" to get
a list of all the roles in your IAM console.

<br />
<img src="/Screenshots/IAMConsole.png" alt="IAM Console" width="900"/>
<br />

<br />
<img src="/Screenshots/IAMRoles.png" alt="IAM Roles" width="900"/>
<br />

Type "Marvel" into the search bar to find the role that your Lambda function
created. Click on the Role name.

<br />
<img src="/Screenshots/IAMRoleSearch.png" alt="IAM Role Search" width="900"/>
<br />

This role has a single policy applied at the moment - an AWS Lambda Basic
Execution Role. This role only gives permissions for CloudWatch logging capabilities.
However, we want the Lambda function to be able to call Pinpoint as well. To do that,
we need to add another policy. Click on "Add Inline Policy"

<br />
<img src="/Screenshots/AWSLambdaRole.png" alt="IAM Lambda Role" width="900"/>
<br />


Here is the screen you will see to create a new policy and attach it to this role.
Policies **allow** roles to perform **Actions** on **Resources**. If the action is
not explicitly allowed in any policies attached to the role, the action is denied.3

<br />
<img src="/Screenshots/IAMCreatePolicy.png" alt="IAM Create Role" width="900"/>
<br />


Now, AWS Pinpoint is the service which we need permissions for. Search for that
in the "Service" area and select Pinpoint.
<br /><br />

Next, for "Actions", it's okay to select "All Pinpoint Actions" for this tutorial.
However, it is best practice to allow the smallest number of actions possible
for a role to be able to do its job. This approach is known as "Least Privilege"
and is a good way to keep your users and applications from doing things they
aren't supposed to. To demonstrate this, I will only allow the function the
permissions that it needs, namely, the "mobiletargeting:SendMessages" command.
<br /><br />

Next, for "Resources" again it's okay to select "All Resources" for this tutorial,
or you can choose the specific Pinpoint project that you want to use to send messages.
Here is a screenshot of how to configure it. Note that you need to append "/messages"
at the end of the resource ID, so if your Pinpoint project has the Project ID "123456",
you should put "123456/messages" in the "App id" box.

<br />
<img src="/Screenshots/PolicyAddARN.png" alt="Policy Add ARN" width="900"/>
<br />

There's no need to configure any Request Conditions, so hit "Review Policy" and
give the policy a name. I chose a more descriptive one, but you can name it
anything you want.

<br />
<img src="/Screenshots/CreatePolicyName.png" alt="Name Policy" width="900"/>
<br />

Ok! Hit "Create Policy" to complete this process.

<br />

This will allow your Lambda function to call the Pinpoint project to send messages.
Head back to your Lambda function via the Services tab. Then select your Lambda project.

<br />
<img src="/Screenshots/LambdaProjectsScreen.png" alt="Lambda Projects" width="900"/>
<br />

Now, we're going to test our Lambda project again. Click on test in the upper
right corner.



<br />
<img src="/Screenshots/LambdaTestSuccess.png" alt="Lambda Test Success" width="900"/>
<br />

You should see a success banner! If you do not see this banner, wait a minute or
two and refresh the page to ensure the IAM role has had time to update.

You should receive a text message from the long code that was configured in your
Pinpoint. You can also view the details of the execution.

<br />
<img src="/Screenshots/LambdaTestSuccessFull.png" alt="Lambda Test Success Details" width="900"/>
<br />


## Adding a CloudWatch Event to automatically trigger the Lambda function
**TODO**: Add CloudWatch Event Rule to schedule text every day.

Now, we are going to add a scheduled event to trigger our Lambda function every
day at 7pm. Close the success report by clicking the X in the upper right corner.

<br />
Adding a trigger is easy - just click "Add Trigger" near the center left of the screen.




<br />
<img src="/Screenshots/AddTrigger.png" alt="Add Trigger" width="900"/>
<br />

Click on the "Select a trigger" dropdown, and scroll (or search) to find the
EventBridge trigger.

<br />
<img src="/Screenshots/TriggerEventBridge.png" alt="Trigger EventBridge" width="900"/>
<br />

Next, we will select "Create a new rule" in the next dropdown.

<br />
<img src="/Screenshots/TriggerEmptyRule.png" alt="Trigger Empty Rule" width="900"/>
<br />

Idk I might remove one of these screenshots, there's a lot of them.

<br />
<img src="/Screenshots/TriggerCreateNewRule.png" alt="Trigger Create New Rule" width="900"/>
<br />

We'll create a Schedule expression using cron to schedule when we want our text to be sent.

<br />
<img src="/Screenshots/TriggerCRONExpression.png" alt="Trigger CRON Expression" width="900"/>
<br />

This is the cron expression to trigger the Lambda function at 7pm UTC.
`cron(0 19 ? * * *)`
If you are in the EDT time zone, this is the function that results in 7pm EDT.
`cron(0 23 ? * * *)`
If you are in the PDT time zone, this is the function that results in 7pm PDT.
`cron(0 2 ? * * *)`
<br />
If you want to send the message at a different time or frequency, you can make
your own CRON expression [here](http://www.cronmaker.com/).
<br />
AWS has a [slightly different](https://docs.aws.amazon.com/AmazonCloudWatch/latest/events/ScheduledEvents.html#CronExpressions)
 CRON expression layout








<br /><br /><br /><br /><br /><br />

## Cleaning Up
**TODO**: Add cleanup instructions for Pinpoint, Lambda, CloudWatch, and IAM

<br /><br />


## The End
Thanks for reading through this tutorial! Feel free to give feedback about any issues
or via a pull request. I hope your AWS journey goes well!


<br /><br /><br /><br />

## Planned Fixes/Changes
**TODO**: Add GIFs to cut down on scrolling through pictures
<br />
**TODO**: Add credits/shoutouts
<br />
**TODO**:
<br />

## Old Stuff
MarvelMovieProject-role-j5bre0sa

Original blog post this was based off of:
https://mkdev.me/en/posts/how-to-send-sms-messages-with-aws-lambda-sns-and-python-3
