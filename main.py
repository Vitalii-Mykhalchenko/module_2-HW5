import aiohttp
import asyncio
import json
import datetime


async def get_exchange_rates(session, date):
    url = 'https://api.privatbank.ua/p24api/exchange_rates'
    params = {'json': '', 'date': date}
    async with session.get(url, params=params) as response:
        if response.status == 200:
            data = await response.json()
            exchange_rates = data.get('exchangeRate', [])
            rates_for_date = {}
            for rate in exchange_rates:
                if 'currency' in rate and 'saleRateNB' in rate and 'purchaseRateNB' in rate:
                    currency = rate['currency']
                    sale_rate = rate['saleRateNB']
                    purchase_rate = rate['purchaseRateNB']
                    rates_for_date[currency] = {
                        'sale': sale_rate, 'purchase': purchase_rate}
            return rates_for_date


async def get_date_range_from_user():
    while True:
        try:
            dates_str = input(
                "Enter a date range in the format 'dd.mm.yyyy' or 'dd.mm.yyyy dd.mm.yyyy': ")
            date_tokens = dates_str.split()
            if len(date_tokens) == 1:
                date = datetime.datetime.strptime(date_tokens[0], '%d.%m.%Y')
                return [date.strftime('%d.%m.%Y')]
            elif len(date_tokens) > 1:
                start_date = datetime.datetime.strptime(
                    date_tokens[0], '%d.%m.%Y')
                end_date = datetime.datetime.strptime(
                    date_tokens[1], '%d.%m.%Y')
                if start_date > end_date:
                    print("Error: The start date must be less than the end date.")
                    continue
                dates = [(start_date + datetime.timedelta(days=i)).strftime('%d.%m.%Y')
                         for i in range((end_date - start_date).days + 1)]
                return dates
            else:
                print("Error: At least one date must be entered.")
        except ValueError:
            print(
                "Error: Invalid date format. Please enter the date in the format 'dd.mm.yyyy'.")
        except Exception as e:
            print("An error has occurred:", e)


async def get_currencies_from_user():
    choice = input(
        "Want to select specific currencies? (y/n): ").strip().lower()
    if choice == 'y':
        currencies = input(
            "Enter the currencies separated by commas AUD, AZN, BYN, CAD, CNY, EUR, GBP, JPY, USD...: ").strip().upper().split(',')
        return [currency.strip() for currency in currencies]
    else:
        return None


async def write_to_file(data_dict, filename):
    with open(filename, "w") as json_file:
        json.dump(data_dict, json_file, indent=4)
    print("The data was successfully written to the JSON file.")


async def print_from_file(filename, currencies_to_display=None):
    with open(filename, 'r') as file:
        data = json.load(file)
        for date, currencies in data.items():
            print(f"date: {date}")
            for currency, rates in currencies.items():
                if currencies_to_display is None or currency in currencies_to_display:
                    print(
                        f"{currency}: sale - {rates['sale']}, purchase - {rates['purchase']}")
            print()  # Додаємо порожній рядок для кращого читання між датами


async def main():
    async with aiohttp.ClientSession() as session:
        dates = await get_date_range_from_user()
        exchange_data = {}  # Створюємо пустий словник для зберігання даних про курси валют
        for date in dates:
            rates_for_date = await get_exchange_rates(session, date)
            exchange_data[date] = rates_for_date

        await write_to_file(exchange_data, 'data.json')

        currencies_to_display = await get_currencies_from_user()

        await print_from_file("data.json", currencies_to_display)

if __name__ == "__main__":
    asyncio.run(main())
