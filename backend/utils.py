import asyncio
import os
from dotenv import load_dotenv
import aiohttp
from bring_api import Bring


async def create_bring_session():
    load_dotenv()
    mail = os.getenv("BRING_MAIL")
    password = os.getenv("BRING_PASSWORD")

    if not mail or not password:
        raise ValueError("Missing BRING_MAIL or BRING_PASSWORD environment variables")

    session = aiohttp.ClientSession()
    bring = Bring(session, mail, password)
    await bring.login()
    return bring, session



