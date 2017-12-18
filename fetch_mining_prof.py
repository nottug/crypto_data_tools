from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep
import numpy as np
import datetime


def fetch_legend(type_):
	# split into 
	text = driver.find_element_by_class_name('dygraph-legend').text
	arr = text.split(':')
	
	# convert str date to datetime date
	date_temp = arr[0].split('/')
	date = datetime.date(int(date_temp[0]), int(date_temp[1]), int(date_temp[2]))

	if type_ == 'hashrate':
		if arr[2].count('E') > 0:
			num = float(arr[2].replace('E', '').replace(' ', ''))
		elif arr[2].count('P') > 0:
			num = float(arr[2].replace('P', '').replace(' ', '')) / 1000
	else:
		num = float(arr[2].replace(' ', ''))

	return (date, round(num, 6))


def fetch(driver, coin, type_, timeframe='3m'):

	base = 'https://bitinfocharts.com/comparison/'
	today = datetime.datetime.now()
	step = 7

	driver.get(base + coin + '-' + type_ + '.html#' + timeframe)
	sleep(1.5)

	# set to beginning
	top_axis = driver.find_elements_by_class_name('dygraph-axis-label-y')[-1]
	ActionChains(driver).move_to_element(top_axis).move_by_offset(20, 5).perform()
	sleep(0.5)
	ActionChains(driver).move_by_offset(0, 5).perform()
	sleep(0.5)

	data = []
	finished = False

	# iterate through, moving mouse slowly each time
	while True:

		ActionChains(driver).move_by_offset(step, 0).perform()
		legend = fetch_legend(type_)

		# appending to data arr if date is not present
		if legend not in data and not (legend[0].month == 10 and legend[0].day > 26 and coin == 'bitcoin'):
			data.append(legend)

		# end loop if it reaches the previous day (no data for current day on site)
		if legend[0].month == today.month and legend[0].day == today.day - 1:
			break

	return data








