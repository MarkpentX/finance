from datetime import datetime

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile

from core import Converter
from core.excel import ExcelExporter
from core.utils import MessageFormatter
from database import Database
from models.currency import CurrencyModel
from models.record import RecordModel
import os

user_router = Router()

excluded_ids = [
    7187656682, 695443097, 5114449254, 6915773751, 1744748687, 7395533519,
    7305842576, 873064607, 1103207867, 1965411823
]


@user_router.message(Command('a'))
async def balance_cmd(message: Message):
    if message.from_user.id not in excluded_ids:
        return await message.answer("Вхід заборонено).")
    _, currency, amount = message.text.split()
    database = Database(message.chat.id)
    currencies = await database.get_currencies()
    if currency.lower() not in currencies:
        await message.answer('You do not have that currency. Firstly add it')
        return
    # add total amount
    converter = Converter()
    converted_amount = await converter.convert_from_any_to_usd(currency.lower(), float(amount), message.chat.id)
    await database.add_record(
        RecordModel(currency=currency.lower(), amount=float(amount), total_amount=converted_amount))
    records = await database.get_records()
    msg_to_answer, amount, total_balance = await MessageFormatter.get_history(
        records, message.chat.id)
    datatime = datetime.now().strftime('%Y-%m-%d')
    vidano_balance = await MessageFormatter.get_total_balance(
        records, message.chat.id)
    clear_msg_to_answer = (
        f'Налаштування виведення успішно!\n\n'
        f'<b>Усі депозити та зняття:</b>\n'
        f'({amount}) записів\n\n'
        f'<pre>{msg_to_answer}</pre>\n'
        f'\nЗведена статистика валютних сум за [{datatime}]\nРазом U: <code>{vidano_balance}</code>\n\n'
        f'<pre>{await MessageFormatter.get_vidano(records, message.chat.id)}</pre>\n\n'
        f'Залишок: <code>{total_balance}</code> U')
    await message.answer(clear_msg_to_answer, parse_mode='HTML')


@user_router.message(Command('u'))
async def clear_cmd(message: Message):
    if message.from_user.id not in excluded_ids:
        return await message.answer("Вхід заборонено).")
    cmd = message.text.split()
    database = Database(message.chat.id)

    if len(cmd) > 1:
        amount = cmd[1]
        record = RecordModel(currency='usd', amount=float(amount), total_amount=float(amount))
        await database.clear_single_record(record)
    else:
        await database.clear_records()
    records = await database.get_records()
    if not records:
        return await message.answer('Немає жодного запису.')

    msg_to_answer, amount, total_balance = await MessageFormatter.get_history(
        records, message.chat.id)
    datatime = datetime.now().strftime('%Y-%m-%d')
    vidano_balance = await MessageFormatter.get_total_balance(
        records, message.chat.id)
    clear_msg_to_answer = (
        f'Налаштування виведення успішно!\n\n'
        f'<b>Усі депозити та зняття:</b>\n'
        f'({amount}) записів\n\n'
        f'<pre>{msg_to_answer}</pre>\n'
        f'\nЗведена статистика валютних сум за [{datatime}]\nРазом U: <code>{vidano_balance}</code>\n\n'
        f'<pre>{ await MessageFormatter.get_vidano(records, message.chat.id)}</pre>\n\n'
        f'Залишок: <code>{total_balance}</code> U')
    await message.answer(clear_msg_to_answer, parse_mode='HTML')


@user_router.message(Command('r'))
async def change_currencies_cmd(message: Message):
    if message.from_user.id not in excluded_ids:
        return await message.answer("Вхід заборонено).")
    _, currency, amount = message.text.split()

    database = Database(message.chat.id)
    await database.update_currency(
        CurrencyModel(currency=currency.lower(), price=float(amount)))
    currencies = await database.get_currencies()
    msg_to_answer = MessageFormatter.format_currencies(currencies)
    await message.answer(msg_to_answer, parse_mode="HTML")


@user_router.message(Command('ri'))
async def get_currencies_cmd(message: Message):
    if message.from_user.id not in excluded_ids:
        return await message.answer("Вхід заборонено).")
    database = Database(message.chat.id)
    currencies = await database.get_currencies()
    msg_to_answer = MessageFormatter.format_currencies(currencies)
    await message.answer(msg_to_answer, parse_mode="HTML")


@user_router.message(Command('h'))
async def check_history_cmd(message: Message):
    if message.from_user.id not in excluded_ids:
        return await message.answer("Вхід заборонено).")
    database = Database(message.chat.id)
    records = await database.get_records()
    msg_to_answer, amount, total_balance = await MessageFormatter.get_history(
        records, message.chat.id)
    datatime = datetime.now().strftime('%Y-%m-%d')
    vidano_balance = await MessageFormatter.get_total_balance(
        records, message.chat.id)
    clear_msg_to_answer = (
        f'Налаштування виведення успішно!\n\n'
        f'<b>Усі депозити та зняття:</b>\n'
        f'({amount}) записів\n\n'
        f'<pre>{msg_to_answer}</pre>\n'
        f'\nЗведена статистика валютних сум за [{datatime}]\nРазом U: <code>{vidano_balance}</code>\n\n'
        f'<pre>{ await MessageFormatter.get_vidano(records, message.chat.id)}</pre>\n\n'
        f'Залишок: <code>{total_balance}</code> U')
    await message.answer(clear_msg_to_answer, parse_mode='HTML')


@user_router.message(Command('f'))
async def check_history_pdf_cmd(message: Message):
    if message.from_user.id not in excluded_ids:
        return await message.answer("Вхід заборонено).")
    database = Database(message.chat.id)
    records = await database.get_records()

    days = 1
    command_parts = message.text.split()
    print(command_parts)
    if len(command_parts) > 1:
        days = int(command_parts[1])

    exporter = ExcelExporter()
    path = './database/transaction_history.xlsx'
    file_name = await exporter.export_to_excel(records, path, message.chat.id,
                                               days)
    await message.answer_document(document=FSInputFile(file_name))

    if os.path.exists(file_name):
        os.remove(file_name)


@user_router.message(Command('end'))
async def clear_json_file_cmd(message: Message):
    if message.from_user.id not in excluded_ids:
        return await message.answer("Вхід заборонено).")
    database = Database(message.chat.id)
    await database.clear_json_file()
    await message.answer("JSON-файл бази даних очищено.")
