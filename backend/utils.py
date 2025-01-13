import asyncio
import os
from dotenv import load_dotenv
import aiohttp
from bring_api import Bring
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


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


async def get_list_id(bring_instance, list_name):
    all_lists = await bring_instance.load_lists()
    all_lists = all_lists["lists"]
    grocery_list = next((item for item in all_lists if item.get("name") == list_name), None)
    list_id = grocery_list["listUuid"]
    return list_id

def get_db_session():
    load_dotenv()
    user = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")
    host = os.getenv("POSTGRES_HOST")
    port = os.getenv("POSTGRES_PORT")
    database = os.getenv("POSTGRES_DB")

    engine = create_engine(
        url="postgresql://{0}:{1}@{2}:{3}/{4}".format(
            user, password, host, port, database
        ), echo=True
    )

    Session=sessionmaker(bind=engine)
    session = Session()

    return session