# https://www.cars.com/shopping/results/?dealer_id=&include_shippable=true&keyword=&list_price_max=&list_price_min=&makes[]=porsche&maximum_distance=all&mileage_max=&models[]=porsche-911&monthly_payment=&page_size=20&sort=best_match_desc&stock_type=cpo&year_max=2019&year_min=2009&zip=94070

import requests, bs4

def get_cars_com_results():
	res = requests.get("https://www.cars.com/shopping/results/?dealer_id=&include_shippable=true&keyword=&list_price_max=&list_price_min=&makes[]=porsche&maximum_distance=all&mileage_max=&models[]=porsche-911&monthly_payment=&page_size=20&sort=best_match_desc&stock_type=cpo&year_max=2019&year_min=2009&zip=94070")

	



if __name__ == __main__:
	get_cars_com_results()