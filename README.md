# CogniQ

This project is under active development. Your experience will be buggy until a release has been cut.
Naturally at this stage, there are no guarantees about stability.

In short, the current feature set is that you can have conversations that will be composed of responses from Bing Search, Chat GPT, and Anthropic Claude.

If you don't have access to one of the API keys required for the personality, then modify `multiple_personalities.py` to remove the personality or personalities.

The idea is that one could add an arbitrary number of personalities to CogniQ.

In that sense, `multiple_personalities.py` and `main.py` are really just example files for how to use the library. You can use them as a starting point for your own bot.

# Demo

Join the [community slack channel](www.cogniq.info/join-slack) to interact with @CogniQMain, the demo bot deployed from the `main` branch of this repository. 

# Usage

The primary interface by which to use CogniQ is as a slack bot. You may direct message @CogniQ directly, or you may invoke it in a thread.

@CogniQ wil always start a new thread if not in a thread already. This is so that the memory of the conversation is segmented correctly.

## In a channel or thread, mention @CogniQ
In Slack, have a conversation with CogniQ and ask it to do something by mentioning it in a thread or channel. For example:

<img src="https://user-images.githubusercontent.com/176915/235838387-9befa803-1179-42a4-8127-8ee1ad518c73.png" alt="@CogniQ What is the Picard Maneuver?" width="300">

When starting a new conversation outside of a thread, @CogniQ will be initialized with the last 10 or so messages from the channel. This history may include messages in recent threads.

When starting a new conversation inside of a thread, @CogniQ will be initialized with the last 10 or so messages from the thread.

CogniQ will respond with the answer to your question.

## In a direct message, just ask your question.

You can also message CogniQ directly. You do not have to mention it when you message it directly.

<img src="https://user-images.githubusercontent.com/176915/243065469-d6cc3f54-198f-411e-b280-e6aab922a4ef.png" alt="What is the Riker Maneuver?" width="450">


# CogniQ has multiple personalities

## CogniQ will ask Chat GPT for an answer, and also search the web using Bing.

CogniQ will incorporate the top three search results into its answer and will provide links to any relevant sources.

It gets its answer by performing a straight query to ChatGPT and then using an agent to draw context from Bing Search. 
The set of responses are then combined to produce a search augmented response.


# Deployment

## Running locally

- [ ] Install the prerequisites (see details in the [development](#development) section)

```bash

# If you haven't already, initialize a virtualenv: 
python -m venv .venv

# Install the dependencies:  
make deps
source .venv/bin/activate

# Copy the example .env file to .env
cp .env.example .env

# Edit the .env file to add your API keys
echo "edit .env to add your API keys"


# Run the app
python main.py
```

## Running in a Docker container

```
docker run --env_file .env ghcr.io/cogniq/cogniq:main
```

## Deploying to Azure Container Instances

See the workflow in `.github/workflows/_deploy.yml`. 

> The workflow is used to deploy the bot to the CogniQ Community Slack ([please join!](https://www.cogniq.info/join-slack)).

# Development

## 1. Prerequisites

Before you begin, make sure to have the following prerequisites in place:

### Install CUDA if on Linux

To set up the development environment on Linux, follow these steps:

1. Install the CUDA Toolkit 11. You can find the [installation instructions](https://docs.nvidia.com/cuda/cuda-installation-guide-linux/index.html) on the NVIDIA website.
   1. The files should be installed to /usr/local/cuda-11.8/
   2. `export LD_LIBRARY_PATH=/usr/local/cuda-11.8/lib64:/usr/local/cuda-11.8/extras/CUPTI/lib64`
2. Install cuDNN
   1. Install the [cuDNN for CUDA 11 repo](https://developer.nvidia.com/rdp/cudnn-download)
   ```
   sudo dpkg -i /mnt/c/Users/myusername/Downloads/cudnn-local-repo-ubuntu2004-8.9.1.23_1.0-1_amd64.deb
   ```
   1. After the repo is installed, then install the package
   ```
   apt install libcudnn8
   ```

3. Manually uncomment the pytorch source, and uncomment the torch dependency line for 2.0.1+cu118

4. Install the dependencies and run the app:
   ```
   python -m venv .venv
   source .venv/bin/activate
   make deps
   python main.py
   ```

## No need for CUDA on OSX environments

```
python -m venv .venv
source .venv/bin/activate
make deps
python main.py
```

### Visual Studio Code Dev Containers (Optional)
#### Docker Desktop 

1. **Install Docker Desktop**: Docker is used for creating isolated environments called containers. To install Docker Desktop, follow the instructions given in the official Docker documentation.

   - For Windows: [Install Docker Desktop on Windows](https://docs.docker.com/docker-for-windows/install/)
   - For Mac: [Install Docker Desktop on Mac](https://docs.docker.com/docker-for-mac/install/)
   - For Linux: Docker Desktop is not available, use Docker engine instead. [Install Docker Engine on Ubuntu](https://docs.docker.com/engine/install/ubuntu/)

2. **Verify Docker Desktop Installation**: After installing Docker Desktop, you can verify that it's installed correctly by opening a new terminal window and typing `docker --version`. You should see a message with your installed Docker version.

#### Install Visual Studio Code
1. **Install Visual Studio Code**: VS Code is a code editor with support for development containers. To install VS Code, follow the instructions in the [VS Code Documentation](https://code.visualstudio.com/docs/setup/setup-overview).

2. **Install Remote - Containers Extension**: This extension lets you use a Docker container as a full-featured development environment. To install the extension, follow the instructions in the [VS Code Documentation](https://code.visualstudio.com/docs/remote/containers#_installation).


## 2. Setup API Keys

### Get Bing Search API Keys

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

9. Copy one of the API keys and add it to the `.env` file

   ```
   BING_SUBSCRIPTION_KEY=<your_bing_search_api_key>
   ```


### Get OpenAI API Keys

To set up OpenAI API keys, follow these steps:

1. Go to the OpenAI website at <https://platform.openai.com/signup/> and sign up for an account if you don't have one already.

2. Once you have an account, sign in and go to the API Keys section in your OpenAI Dashboard: <https://platform.openai.com/account/api-keys>

3. Click on the "Create an API key" button.

4. Give your API key a name, and optionally add a description. This can be helpful if you want to track the usage of different keys for various projects or environments.

5. Click on the "Create" button, and the new API key will be generated.

6. Copy the generated API key to your clipboard.

7. Add the OpenAI API key to the `.env` file
   ```
   OPENAI_API_KEY=<your_openai_api_key>
   ```


### Get Anthropic Claude API Keys
To set up Anthropic Claude API keys, follow these steps:
1. Go to the Anthropic website at https://www.anthropic.com/product and request access to Claude.
2. Once you have an account, sign in and go to the API Keys section: https://console.anthropic.com/account/keys
3. Click on the "Create Key" button.
4. Copy the generated API key to your clipboard.
5. Add the Anthropic Claude API key to the `.env` file

   ```
   ANTHROPIC_API_KEY=<your_anthropic_api_key>
   ```

### Deploy to Slack

1. Go to https://api.slack.com/apps and click "Create New App."
2. Choose "From an app manifest" and select your workspace.
3. Copy the app manifest from `deployments/example/slack_manifest.json`. Later, you will modify it with your public URL. But for dev, the example is fine.
4. Modify to taste, and paste the app manifest into the text box and click "Next."
5. Click "Create" to finish creating the app.
6. After your app has been created, navigate to the "Basic Information" page from the side menu.
7. Under the "App Credentials" section, find the "App Token" field. This is your `SLACK_APP_TOKEN`. Copy it.
8. Add the `SLACK_APP_TOKEN` to the `.env` file.
9. Still on the "Basic Information" page, locate the "Signing Secret" under the "App Credentials" section. This is your `SLACK_SIGNING_SECRET`.
10. Add the `SLACK_SIGNING_SECRET` to the `.env` file.
11. Now, navigate to the "OAuth & Permissions" page in the side menu.
12. At the top of the "OAuth & Permissions" page, click "Install App to Workspace." This will generate your `SLACK_BOT_TOKEN`.
13. After the installation process, you will be redirected to the "OAuth & Permissions" page again. Here, under the "Tokens for Your Workspace" section, you will find the "Bot User OAuth Token". This is your `SLACK_BOT_TOKEN`.
16. Add the `SLACK_BOT_TOKEN` to the `.env` file.

> ⚠️ **Remember to never commit your `.env` file to the repository as it contains sensitive information.** ⚠️


## 3a. Run the app locally

1. Once you have all of the API keys in the .env file, you can run the app locally.
7. Run the app: `python main.py`
8. Restart the app whenever you make changes to the code.

## 3b. Run the app in Dev Container (Optional)

1. With the repository open in VS Code, press F1 and select the "Remote-Containers: Reopen in Container" command. VS Code will start building the Docker container based on the specifications in the `.devcontainer/devcontainer.json` file in the repository. This may take some time when run for the first time.
2. Assuming that the .env file is setup correctly, you can run the app in the dev container.
3. Run the app: `python main.py`
4. Restart the app whenever you make changes to the code.

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
