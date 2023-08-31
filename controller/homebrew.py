from provider import itemsprovider


def save_new_item(item_data):
    raise Exception("Adding items has been temporarily disabled.")
    itemsprovider.update_in_items(item_data)
