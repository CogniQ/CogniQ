# CogniQ

This project is under active development. I wouldn't recommend using it yet, unless you're interested in contributing.

# Usage

In Slack, have a conversation with CogniQ and ask it to do something. CogniQ will augment its responses using Bing.

## Thread vs Channel
If you mention it in a thread, CogniQ will have historical context from the thread.
If you mention it in a channel, CogniQ will have historical context from the channel, including from threads preceding it.

# Development

## Get Bing Search API Keys

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


## Get OpenAI API Keys

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


## Deploy the app

1. Clone the repository: `git clone https://github.com/your-repo/CogniQ.git`
2. Navigate to the project directory: `cd CogniQ`
3. Initialize the virtualenv: `python3 -m venv .venv`
4. Install poetry: `pip install poetry`
5. Install the dependencies: `poetry install`
6. Use the `.envrc.example` file to create a `.envrc` file with your environment variables.
7. Either source the `.envrc` file manually, or use [direnv](https://direnv.net/) to automatically source it.
8. In a separate terminal window, start [ngrok](https://ngrok.com/): `ngrok http 3000`. Take note of the URL from the ngrok output.
9. Run the app: `python main.py`
10. Restart the app whenever you make changes to the code.

## Deploy to Slack

1. Go to https://api.slack.com/apps and click "Create New App."
2. Choose "From an app manifest" and select your workspace.
3. Modify the app manifest from `deployments/example/slack_manifest.json` to include your ngrok URL for the above app.
4. Paste the app manifest into the text box and click "Next."
5. Click "Create" to finish creating the app.
