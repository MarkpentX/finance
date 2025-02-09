import datetime
import json
import os
import logging
import aiofiles

from models.currency import CurrencyModel
from models.record import RecordModel

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


class Database:
    def __init__(self, chat_id: int):
        self.file_path = f'./database/database_{chat_id}.json'
        self.file_path_currencies = f'./database/currencies_{chat_id}.json'
        logging.info(f"Database initialized for chat_id={chat_id}")

    async def _load_currencies(self):
        try:
            async with aiofiles.open(self.file_path_currencies, 'r') as file:
                content = await file.read()
                logging.debug(f"Loaded currencies from {self.file_path_currencies}")
                return json.loads(content)
        except FileNotFoundError:
            logging.warning(f"File {self.file_path_currencies} not found. Creating a new one.")
            os.makedirs(os.path.dirname(self.file_path_currencies), exist_ok=True)
            initial_data = {}
            async with aiofiles.open(self.file_path_currencies, 'w') as file:
                await file.write(json.dumps(initial_data, ensure_ascii=False, indent=4))
                logging.info(f"Created empty currencies file at {self.file_path_currencies}")
            return initial_data
        except Exception as e:
            logging.error(f"Error loading currencies: {e}")
            return {}

    async def _save_history(self, history: dict) -> None:
        try:
            async with aiofiles.open(self.file_path, 'w') as file:
                await file.write(json.dumps(history, ensure_ascii=False, indent=4))
                logging.debug(f"History saved to {self.file_path}")
        except Exception as e:
            logging.error(f"Error saving history: {e}")

    async def _load_history(self) -> dict:
        try:
            async with aiofiles.open(self.file_path, 'r') as file:
                content = await file.read()
                logging.debug(f"Loaded history from {self.file_path}")
                return json.loads(content)
        except FileNotFoundError:
            logging.warning(f"File {self.file_path} not found. Creating a new one.")
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            initial_data = {}
            async with aiofiles.open(self.file_path, 'w') as file:
                await file.write(json.dumps(initial_data, ensure_ascii=False, indent=4))
                logging.info(f"Created empty history file at {self.file_path}")
            return initial_data
        except Exception as e:
            logging.error(f"Error loading history: {e}")
            return {}

    async def _save_currencies(self, currencies: dict) -> None:
        try:
            async with aiofiles.open(self.file_path_currencies, 'w') as file:
                await file.write(json.dumps(currencies, ensure_ascii=False, indent=4))
                logging.debug(f"Currencies saved to {self.file_path_currencies}")
        except Exception as e:
            logging.error(f"Error saving currencies: {e}")

    async def add_record(self, record: RecordModel) -> None:
        try:
            prev_data = await self._load_history()
            records = prev_data.get('records', [])
            records.append(record.model_dump())
            prev_data['records'] = records
            await self._save_history(prev_data)
            logging.info(f"Added record: {record.model_dump()}")
        except Exception as e:
            logging.error(f"Error adding record: {e}")

    async def get_records(self) -> list:
        try:
            data = await self._load_history()
            logging.info("Fetched records")
            return data.get('records', [])
        except Exception as e:
            logging.error(f"Error getting records: {e}")
            return []

    async def get_currencies(self) -> dict:
        try:
            currencies = await self._load_currencies()
            logging.info("Fetched currencies")
            return currencies
        except Exception as e:
            logging.error(f"Error getting currencies: {e}")
            return {}

    async def update_currency(self, model: CurrencyModel) -> None:
        try:
            currencies = await self._load_currencies()
            currencies[model.currency] = model.price
            await self._save_currencies(currencies)
            logging.info(f"Updated currency: {model.currency} = {model.price}")
        except Exception as e:
            logging.error(f"Error updating currency: {e}")

    async def clear_records(self) -> None:
        try:
            history = await self._load_history()
            records = history.get('records', [])
            clonned = []
            current_time = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
            for record in records:
                if not record.get("is_vidano"):
                    record["is_vidano"] = True
                    record['vidano_time'] = current_time
                if record.get('is_needed'):
                    record['is_needed'] = False
                    record_clonned = record.copy()
                    record['vidano_time'] = current_time
                    clonned.append(record_clonned)
                clonned.append(record)
            history['records'] = clonned
            await self._save_history(history)
            logging.info("Cleared records and updated history")
        except Exception as e:
            logging.error(f"Error clearing records: {e}")

    async def clear_single_record(self, record: RecordModel) -> None:
        try:
            current_time = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
            record.vidano_time = current_time
            record.is_vidano = True
            record.is_needed = True
            record.is_visible = False
            await self.add_record(record)
            logging.info(f"Cleared single record: {record.model_dump()}")
        except Exception as e:
            logging.error(f"Error clearing single record: {e}")

    async def clear_json_file(self):
        try:
            async with aiofiles.open(self.file_path, 'w') as file:
                await file.write(json.dumps({}, ensure_ascii=False, indent=4))
                logging.info(f"Cleared JSON file at {self.file_path}")
        except Exception as e:
            logging.error(f"Error clearing JSON file: {e}")
