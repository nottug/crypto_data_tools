import datetime
import time
from selenium.webdriver.common.action_chains import ActionChains
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from calendar import monthrange

months = {'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
		'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12}


def fetch(driver, coin, start, end):

	batches = []
	data = []
	last = start

	while True:
		temp = last + datetime.timedelta(days=monthrange(last.year, last.month)[1])
		batches.append((last,temp))
		if temp == end:
			break
		last = temp


	for first, last in batches:

		driver.get('https://www.coinwarz.com/network-hashrate-charts/{}-network-hashrate-chart'.format(coin))
		time.sleep(5)

		input_boxes = driver.find_elements_by_class_name('highcharts-range-input')
		
		input_boxes[0].click()
		time.sleep(0.2)
		inputs = driver.find_elements_by_class_name('highcharts-range-selector')[0]
		inputs.clear()
		inputs.send_keys('{}-{}-{}'.format(first.year, first.month, first.day))
		inputs.send_keys(Keys.RETURN)

		input_boxes[1].click()
		time.sleep(0.2)
		inputs = driver.find_elements_by_class_name('highcharts-range-selector')[1]
		inputs.clear()
		inputs.send_keys('{}-{}-{}'.format(last.year, last.month, last.day))
		inputs.send_keys(Keys.RETURN)

		time.sleep(1)

		edge = driver.find_element_by_class_name('highcharts-scrollbar-button')
		ActionChains(driver).move_to_element(edge).move_by_offset(0, -300).perform()
		ActionChains(driver).move_by_offset(-6, 0).perform()


		def find_data():
			text = driver.find_element_by_class_name('highcharts-tooltip-box').text

			text = text.split('GM')
			date = text[0].split(', ')[1]
			date = date.split(' ')
			mins = date[3].split(':')

			date = datetime.datetime(int(date[2]), months[date[1]], int(date[0]), int(mins[0]), int(mins[1]), int(mins[2]))
			
			hash_ = text[1]
			hash_ = float(hash_.split(':')[1].replace(' ', '').split('P')[0])

			return [date, hash_]


		while True:
			fetched = find_data()

			if fetched[0].year == last.year and fetched[0].month == last.month and fetched[0].day == last.day:
				break

			if fetched not in data:
				data.append(fetched)

			ActionChains(driver).move_by_offset(1, 0).perform()


	return data
