from database import Database


class Converter:
    async def convert_from_any_to_usd(self, currency: str, amount: float, chat_id: int) -> float:
        """
        The method is used to convert any and any currency amount to a USD
        :return: The amount in USD
        """

        currencies = await Database(chat_id).get_currencies()
        rate = currencies.get(currency)
        # TODO check calculation
        return round(amount / rate, 2)
