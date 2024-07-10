import time
import json
from notion_client import Client
import logging

logging.basicConfig(level=logging.INFO, filename='log.log', filemode='w',
                     format= "%(asctime)s - %(levelname)s - %(message)s")

keys = None
with open('api_keys.json', 'r') as file:
            keys = json.load(file)

ALL_TASKS_ID = keys['alltasks_id']
DESAR_TASKS_ID = keys['desar_tasks_id']

class SyncDatabases:
    def __init__(self, db_id_from, db_id_to) -> None:
        self.id_from = db_id_from
        self.id_to = db_id_to
        self.from_db_path = None
        api_key = None
        with open('api_keys.json', 'r') as file:
            api_key = json.load(file)['notion_token']
        self.client = Client(auth= api_key)

    def pull_db(self):
        my_page = self.client.databases.query(
        database_id = self.id_from
        )
        with open(f'{self.id_from}.json', 'w') as file:
            json.dump(my_page, file)
    
    def check_in(self, db, page):
        for item in db['results']:
            if item['id'] == page['id']:
                return True
        
        return False

    # TODO: подумать как апдейтить в вторую базу данных. Можно сразу сохранять пары айдишек первая_бд - вторая_бд и по этим парам находить айдишку во второй бд
    # но тогда что делать с удаленными страницами? 
    def check_updates(self, db, page):
        for item in db['results']:
              if item['id'] == page['id']:
                   if item["properties"]["Name"]["title"][0]["text"]["content"] != item["properties"]["Name"]["title"][0]["text"]["content"]:
                        # TODO: update name of the page
                        updates = {"Name": {"title": [{"text": {"content": item["properties"]["Name"]["title"][0]["text"]["content"]}}]}}
                        self.client.pages.update(page_id=item['id'], properties = updates)
                        return True
        return False

        
    def sync(self):
        updated_db = self.client.databases.query(
        database_id = self.id_from
        )
        with open(f'{self.id_from}.json', 'r') as file:
            curr_db = json.load(file)
        
        new_pages = [x for x in updated_db['results'] if not(self.check_in(curr_db, x))]
        log_s = ''
        for x in new_pages:
            log_s += f'Name: {x["properties"]["Name"]["title"][0]["text"]["content"]}, id: {x["id"]}\n'
        print(log_s)
        logging.info(log_s[:-1])

        #TODO: подумать как нормально апдейдить названия задач

        # pages_with_changed_names = [x for x in updated_db['results'] if self.check_updates(curr_db, x)]
        
        # log_s = ''
        # for x in pages_with_changed_names:
        #     log_s += f'Name: {x["properties"]["Name"]["title"][0]["text"]["content"]}, id: {x["id"]}\n'
        # print(log_s)
        # logging.info(log_s[:-1])

        for page in new_pages:
            upload_json = {
                     "Name": {"title": [{"text": {"content": page["properties"]["Name"]["title"][0]["text"]["content"]}}]},
                     "Class": {"select":  {"name": "Преподавание"}},
                     "Subclass": {"select":  {"name": "DEŠAR"}}
            }
            self.client.pages.create(parent={"database_id": keys['alltasks_id']}, properties=upload_json)




desar_to_all_tasks = SyncDatabases(db_id_from=DESAR_TASKS_ID, db_id_to=ALL_TASKS_ID)

while True:
    desar_to_all_tasks.pull_db()
    logging.info('updated from_db')
    time.sleep(60)
    desar_to_all_tasks.sync()
    logging.info('syncing with to_db is done.')