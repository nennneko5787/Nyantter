from .env import getenv
import aiohttp

async def verify_captcha(token: str) -> bool:
    data = {
        "secret": getenv("turnstile_secret"),
        "response": token
    }

    async with aiohttp.ClientSession() as session:
        async with session.post("https://challenges.cloudflare.com/turnstile/v0/siteverify", data=data) as response:
            return (await response.json()).get("success", False)