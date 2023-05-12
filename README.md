# CogniQ

This project is under active development. Your experience will be buggy until a release has been cut.
Naturally at this stage, there are no guarantees about stability.

In short, the current feature set is that you can have conversations about web search results in the slack bot.
In the coming future, I will be incorporating additional data sources to enquire about.

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

<img src="https://github.com/CogniQ/CogniQ/assets/176915/c55a19c1-3558-4b4b-b605-db42821c8e38" alt="What is the plot to Back to the Future 3?" width="450">

## CogniQ will augment its responses using Bing. 

CogniQ will incorporate the top three search results into its answer and will provide links to its sources.

# Development in 5 steps.

## 0. Prerequisites

Before you begin, make sure to have the following prerequisites in place:

### YOU NEED TO DOWNLOAD NCCL

I don't include this in the repo because you need to agree to a license.

NCCL is required for the PyTorch Docker image.

Open [https://developer.nvidia.com/nccl/nccl-download](https://developer.nvidia.com/nccl/nccl-download)

Click "Download NCCL 2.18.1, for CUDA 11.0, May 4th, 2023"
Click "O/S agnostic local installer"
You should get `nccl_2.18.1-1+cuda11.0_x86_64.txz`

After checkout, place the downloaded file in the `vendor` directory.

### Docker Desktop

1. **Install Docker Desktop**: Docker is used for creating isolated environments called containers. To install Docker Desktop, follow the instructions given in the official Docker documentation.

   - For Windows: [Install Docker Desktop on Windows](https://docs.docker.com/docker-for-windows/install/)
   - For Mac: [Install Docker Desktop on Mac](https://docs.docker.com/docker-for-mac/install/)
   - For Linux: Docker Desktop is not available, use Docker engine instead. [Install Docker Engine on Ubuntu](https://docs.docker.com/engine/install/ubuntu/)

2. **Verify Docker Desktop Installation**: After installing Docker Desktop, you can verify that it's installed correctly by opening a new terminal window and typing `docker --version`. You should see a message with your installed Docker version.

### VS Code Dev Containers

1. **Install Visual Studio Code**: VS Code is a code editor with support for development containers. To install VS Code, follow the instructions in the [VS Code Documentation](https://code.visualstudio.com/docs/setup/setup-overview).

2. **Install Remote - Containers Extension**: This extension lets you use a Docker container as a full-featured development environment. To install the extension, follow the instructions in the [VS Code Documentation](https://code.visualstudio.com/docs/remote/containers#_installation).


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


## 3. Deploy to Slack

1. Go to https://api.slack.com/apps and click "Create New App."
2. Choose "From an app manifest" and select your workspace.
3. Copy the app manifest from `deployments/example/slack_manifest.json`. Later, you will modify it with your public URL. But for dev, the example is fine.
4. Modify to taste, and paste the app manifest into the text box and click "Next."
5. Click "Create" to finish creating the app.
6. After your app has been created, navigate to the "Basic Information" page from the side menu.
7. Under the "App Credentials" section, find the "App Token" field. This is your `SLACK_APP_TOKEN`. Copy it.
8. Add the `SLACK_APP_TOKEN` to the `.envrc` file


## 4. Deploy the app

1. Clone the repository: `git clone git@github.com:CogniQ/CogniQ.git`
2. Navigate to the project directory: `cd CogniQ`
3. Download NCCL nccl_2.18.1-1+cuda11.0_x86_64. This is required for the PyTorch Docker image. You can download it from https://developer.nvidia.com/nccl/nccl-download. Place the downloaded file in the `vendor` directory.
4. **Open the Repository in a Dev Container**: With the repository open in VS Code, press F1 and select the "Remote-Containers: Reopen in Container" command. VS Code will start building the Docker container based on the specifications in the `.devcontainer/devcontainer.json` file in the repository. This may take some time when run for the first time.
5. Use the `.envrc.example` file to create a `.envrc` file with your environment variables.
6. Either source the `.envrc` file manually, or use [direnv](https://direnv.net/) to automatically source it.
7. Run the app: `python main.py`
8. Restart the app whenever you make changes to the code.

# Notes

## Setup for WSL-Ubuntu

To set up the development environment on WSL-Ubuntu, follow these steps:

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

3. Install the dependencies
   ```
   make deps
   ```

## Setup for Mac OSX M1 Silicon

1. Manually comment out the pytorch source, and swap the "torch" dependency lines.
2. Install the dependencies
   ```
   make deps
   ```


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
