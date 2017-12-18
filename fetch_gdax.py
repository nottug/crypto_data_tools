'''

Most of this code was taken from Aleksandar Gyorev at

https://hackercrypt.com/code/fetch-historic-price-data


'''

import pandas as pd
import requests
import datetime
from time import sleep


class GDAX(object):

	def __init__(self, pair='BTC-USD'):
		self.pair = pair
		self.uri = 'https://api.gdax.com/products/{pair}/candles'.format(pair=self.pair)


	def fetch(self, start, end, granularity):
		data = []
		# We will fetch the candle data in windows of maximum 100 items.
		delta = datetime.timedelta(minutes=granularity * 100)

		total = (start-end).days

		count = 0

		last = 0

		slice_start = start
		while slice_start != end:
			slice_end = min(slice_start + delta, end)
			data += self.request_slice(slice_start, slice_end, granularity)
			slice_start = slice_end

			prog = round(abs((slice_end-start).days/total)*100, 2)
			count += 1


			if prog != last:
				print('Percentage: {}%'.format(prog))

			last = prog

		# I prefer working with some sort of a structured data, instead of
		# plain arrays.
		data_frame = pd.DataFrame(data=data, columns=['time', 'low', 'high', 'open', 'close', 'volume'])
		data_frame.set_index('time', inplace=True)
		return data_frame

	def request_slice(self, start, end, granularity):
		# Allow 3 retries (we might get rate limited).
		retries = 5
		for retry_count in range(0, retries):
			# From https://docs.gdax.com/#get-historic-rates the response is in the format:
			# [[time, low, high, open, close, volume], ...]
			response = requests.get(self.uri, {
			'start': GDAX.__date_to_iso8601(start),
			'end': GDAX.__date_to_iso8601(end),
			'granularity': granularity * 60  # GDAX API granularity is in seconds.
			})

			if response.status_code != 200 or not len(response.json()):
				if retry_count + 1 == retries:
					raise Exception('Failed to get exchange data for ({}, {})!'.format(start, end))
				else:
					# Exponential back-off.
					sleep(1.5 ** retry_count)
			else:
				# Sort the historic rates (in ascending order) based on the timestamp.
				result = sorted(response.json(), key=lambda x: x[0])
				return result

	@staticmethod
	def __date_to_iso8601(date):
		return '{year}-{month:02d}-{day:02d}T{hour:02d}:{minute:02d}:{second:02d}'.format(
			year=date.year,
			month=date.month,
			day=date.day,
			hour=date.hour,
			minute=date.minute,
			second=date.second)

