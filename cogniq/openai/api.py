import aiohttp

from .config import Config

async def async_chat_completion_create(*, messages, **kwargs):
    url = f"https://api.openai.com/v1/chat/completions"
    payload = {"model": Config["OPENAI_CHAT_MODEL"], "messages": messages, **kwargs}

    return await async_openai(url=url, payload=payload, **kwargs)

async def async_completion_create(*, prompt, **kwargs):
    url = f"https://api.openai.com/v1/completions"
    payload = {"prompt": prompt, **kwargs}

    return await async_openai(url=url, payload=payload, **kwargs)


async def async_openai(*, url, payload, **kwargs):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f'Bearer {Config["OPENAI_API_KEY"]}',
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as response:
            if response.status == 200:
                return await response.json()
            else:
                raise Exception(f"Error {response.status}: {await response.text()}")
