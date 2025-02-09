from core import Converter


class MessageFormatter:
    @staticmethod
    def format_currencies(currencies) -> str:
        message_to_answer = ''
        for item in currencies:
            message_to_answer += f'{item} - {currencies.get(item)}\n'
        return f"Курсы валют:\n<pre>{message_to_answer}</pre>"

    @staticmethod
    async def get_history(history: list, chat_id: int) -> str and int:
        vidano_balance = 0.00
        count = 0
        message_to_answer = ''
        for item in history:
            total_amount = item.get('total_amount')
            if not item.get('is_vidano'):
                vidano_balance += total_amount
            if item.get('is_needed'):
                vidano_balance += total_amount
                continue
            if not item.get('is_visible'):
                continue
            if total_amount > 0:
                message_to_answer += f'+ {item.get("currency").upper()}: {item.get("amount")} U: {total_amount} Joker Trade‎ ‎ ‎ ‎ ‎ ‎ ‎\n'
            else:
                message_to_answer += f'- {item.get("currency").upper()}: {item.get("amount") * -1} U: {total_amount * -1} Joker Trade‎ ‎ ‎ ‎ ‎ ‎ ‎\n'
            count += 1

        # if vidano_balance < 0:
        #     vidano_balance = 0.00
        return message_to_answer, count, round(vidano_balance, 2)

    @staticmethod
    async def get_vidano(records: list, chat_id: int) -> str:
        grouped_records = {}

        for item in records:
            if item.get('is_vidano'):
                vidano_time = item.get('vidano_time')
                if not vidano_time:
                    continue
                if vidano_time not in grouped_records:
                    grouped_records[vidano_time] = []
                grouped_records[vidano_time].append(item)

        message_to_answer = ""
        for vidano_time, items in sorted(grouped_records.items()):
            total_sum = 0
            for record in items:

                total_sum += record.get('total_amount')

            # Extract only the time (HH:MM) from the `vidano_time` string
            time_only = vidano_time.split("T")[1][:5]
            message_to_answer += f"{time_only} Видано: {total_sum}U Joker Trade ‎ ‎ ‎ ‎ ‎ ‎ ‎\n"

        return message_to_answer.strip()

    @staticmethod
    async def get_total_balance(records: list, chat_id: int) -> float:
        total_balance = 0
        for item in records:
            total_amount = item.get('total_amount')
            if total_amount > 0:
                total_balance += total_amount
        return round(total_balance, 2)
