# CogniQ

This project is under active development. I wouldn't recommend using it until release has been cut.

If you're interested in contributing, please do open an issue or a pull request!

# Usage in Slack

## In a thread, mention @CogniQ
In Slack, have a conversation with CogniQ and ask it to do something by mentioning it in a thread or channel. For example:

<img src="https://user-images.githubusercontent.com/176915/235838387-9befa803-1179-42a4-8127-8ee1ad518c73.png" alt="@CogniQ What is the Picard Maneuver?" width="300">

CogniQ will respond with the answer to your question.

## In a direct message, just ask your question.

You can also message CogniQ directly. You do not have to mention it when you message it directly.

<img src="https://user-images.githubusercontent.com/176915/235838098-a281d2ef-5f38-4317-a9c3-d03a15c6b426.png" alt="What's the capital of France?" width="300">

## CogniQ will augment its responses using Bing. 

If you have a preferred search api, I'd be happy for a contribution!

## Thread vs Channel
If you mention it in a thread, CogniQ will have historical context from the thread.
If you mention it in a channel, CogniQ will have historical context from the channel, including from threads preceding it.

# Development in 4 steps.

## 1. Get Bing Search API Keys

To set up Bing Search API keys, follow these steps:

1. Sign in to your Microsoft account or create a new one at https://portal.azure.com/.

2. Click on "Create a resource" in the top-left corner of the Azure portal.

3. In the search box, type "Bing Search v7" and select it from the list of results.

4. Click the "Create" button to begin the process of setting up the Bing Search API.

5. Fill out the required information:

   - Choose a subscription: Select your Azure subscription.
   - Choose a resource group: Create a new resource group or select an existing one.
   - Give your resource a name: Choose a unique name for your Bing Search resource.
   - Choose a pricing tier: Select the appropriate pricing tier based on your needs. Note that there's a free tier available with limited capabilities.

6. Click the "Review + create" button and review your settings. If everything is correct, click "Create" to deploy the Bing Search resource.

7. After the deployment is complete, go to your new Bing Search resource in the Azure portal.

8. Click on "Keys and Endpoint" in the left-hand menu. Here, you'll find your Bing Search API keys.

9. Copy one of the API keys and add it to the `.envrc` file

   ```
   export BING_SUBSCRIPTION_KEY=<your_bing_search_api_key>
   ```


## 2. Get OpenAI API Keys

To set up OpenAI API keys, follow these steps:

1. Go to the OpenAI website at https://beta.openai.com/signup/ and sign up for an account if you don't have one already.

2. Once you have an account, sign in and go to the API Keys section in your OpenAI Dashboard: https://beta.openai.com/dashboard/api-keys

3. Click on the "Create an API key" button.

4. Give your API key a name, and optionally add a description. This can be helpful if you want to track the usage of different keys for various projects or environments.

5. Click on the "Create" button, and the new API key will be generated.

6. Copy the generated API key to your clipboard.

7. Add the OpenAI API key to the `.envrc` file
   ```
   export OPENAI_API_KEY=<your_openai_api_key>
   ```


## 3. Deploy the app

1. Clone the repository: `git clone git@github.com:CogniQ/CogniQ.git`
2. Navigate to the project directory: `cd CogniQ`
3. Initialize the virtualenv: `python3 -m venv .venv`
4. Install poetry: `pip install poetry`
5. Install the dependencies: `poetry install`
6. Use the `.envrc.example` file to create a `.envrc` file with your environment variables.
7. Either source the `.envrc` file manually, or use [direnv](https://direnv.net/) to automatically source it.
8. In a separate terminal window, start [ngrok](https://ngrok.com/): `ngrok http 3000`. Take note of the URL from the ngrok output.
9. Run the app: `python main.py`
10. Restart the app whenever you make changes to the code.

## 4. Deploy to Slack

1. Go to https://api.slack.com/apps and click "Create New App."
2. Choose "From an app manifest" and select your workspace.
3. Modify the app manifest from `deployments/example/slack_manifest.json` to include your ngrok URL for the above app.
4. Paste the app manifest into the text box and click "Next."
5. Click "Create" to finish creating the app.

# Notes

## Why not langchain?

### TL;DR

By foregoing the framework, I do the upfront work of learning the various APIs, but retain the freedom to deviate from the rails. I do want to [enable modularity](https://github.com/CogniQ/CogniQ/issues/7), but I wish to balance the extent to which the project requires learning the language of the project.

### Rant
I started writing this using [langchain](https://docs.langchain.com/docs/). The project is awesome for quickly trying out a concept. For scripting, its an absolute win. I'm just not smart enough to understand how to use it, and in particular, extend it to suit my needs. Instead, what I offer is less of a framework, and more of an attempt at a starter template.

In general, I find that when one uses frameworks (or client libraries for that matter) for stitching together various APIs, one ostensibly substitues learning the intricacies of the API for learning the intricaces of the framework.
These intricacies tend to become more convoluted the more various similar but different services are mashed together.
The convolution happens as a byproduct of [entangling disparate systems](https://www.youtube.com/watch?v=SxdOUGdseq4) not only vertically in the integration, but horizontally across categories of similarity.
The result of this is that the first steps in using the framework are blissfully easy, the stuff of demos.
But as soon as one steps outsides the limits of the framework, the developer finds they must study both the framework and the API.
Protocols like REST and GraphQL already provide a common and robust interface enough, I think.

/rant

## Why Haystack?

### TL;DR

I was wrong. Haystack is a) rapidly being developed, and b) comprehensive in its approach to the problem domain. I'm still not sure I'll use it in production, but I'm happy to use it for development.

### Not really a rant

I know I seem like a hypocrite to write what I wrote about langchain, then turn around and use haystack. Indeed, the same problems of using frameworks continue to exist. I have to study both the framework and the API. And stepping outside the limit of the framework has me maintaining a [fork](https://github.com/CogniQ/haystack).

But, [haystack](https://haystack.deepset.ai/) is a solid framework, and I have a day job.

I still think a serious at scale deployment will likely demand a purpose-built rewrite, but for me and right now there's more reason than not to use this framework.