from typing import Union
import json
from fastapi import FastAPI

from utils import create_bring_session

app = FastAPI()




@app.get("/items")
async def get_items()-> list[str]:
    bring_instance, session = await create_bring_session()
    try:
        # Use the bring_instance
        all_lists = await bring_instance.load_lists()
        all_lists = all_lists["lists"]
        grocery_list = next((item for item in all_lists if item.get("name") == "Einkoofen"), None)
        list_id= grocery_list["listUuid"]
        items = await bring_instance.get_list(list_id)
        return json.dumps(items)


    finally:
        # Close the session when done
        await session.close()


@app.post("/items")
def post_list(item_list:list):
    pass

@app.delete("/items")
def delete_all_items():
    pass
    #
    #
    #
    # # Get information about all available shopping lists
    # lists = (await bring.load_lists())["lists"]
    #
    # # Save an item with specifications to a certain shopping list
    # await bring.save_item(lists[0]['listUuid'], 'Milk', 'low fat')
    #
    # # Save another item
    # await bring.save_item(lists[0]['listUuid'], 'Carrots')
    #
    # # Get all the items of a list
    #
    #
    # # Check off an item
    # await bring.complete_item(lists[0]['listUuid'], 'Carrots')
    #
    # # Remove an item from a list
    # await bring.remove_item(lists[0]['listUuid'], 'Milk')
