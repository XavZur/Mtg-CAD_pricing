README for Card Price Fetcher

Overview

This project is a card price-fetching tool designed to retrieve the cheapest available prices for Magic the Gathering (MTG) cards from three popular canadian online stores: 401 Games, Face to Face Games, and Vortex Games. The application processes card names from a text file and generates a summary with pricing details and availability for each card.

Features:

	Fetches card prices from the following stores:

		401 Games

		Face to Face Games

		Vortex Games

	Retrieves the cheapest in-stock card prices and card names.

	Processes a list of card names from a user-selected text file.

	Outputs a summary including total deck cost and out-of-stock cards.

Requirements:

	Python 3.7+
	
	Dependencies:

	requests

	beautifulsoup4

	html5lib

	playwright

	tkinter

	asyncio

Installation:

	Clone or download this repository.

	Install dependencies:

	pip install requests beautifulsoup4 html5lib playwright
	playwright install

How to Use:

	Run the Script:
		Execute the script using Python:

		python <script_name>.py

		Input File Selection:

		Upon execution, a file dialog will appear.

		Select a text file containing card names (one name per line). If card quantities are prefixed, they will be ignored.

	Output File Selection:

		Specify a file to save the output summary.

	Processing:

		The program fetches prices from the three stores asynchronously.

		A summary of the deck’s total cost and out-of-stock cards is saved in the output file.

Output File Structure:

	The output file includes:

	Deck Analysis Header:

		Total deck cost.

		List of out-of-stock cards.

	Card-Specific Details:

		For each card, the cheapest price and availability at each store.

	Example:

		Deck Analysis
		=====================
		Total Deck Cost: $45.67
		Out of Stock Cards:
		- Black Lotus
		=====================

		Card: Sol Ring
		401 Games: Cheapest cards: Sol Ring, Price: $5.00
		Face to Face Games: Cheapest cards: Sol Ring, Price: $4.50
		Vortex Games: Cheapest cards: Sol Ring, Price: $4.75

		Card: Black Lotus
		401 Games: No in-stock cards found.
		Face to Face Games: No in-stock cards found.
		Vortex Games: No in-stock cards found.

Functions Overview:

	fetchfrom401(card_name)

		Fetches card prices from 401 Games.

		Scrapes the card name and price, skipping sold-out cards.

		Returns the cheapest card names and prices.

	fetchfromf2f(card_name)

		Fetches card prices from Face to Face Games.

		Uses Playwright for rendering JavaScript-driven content.

		Skips out-of-stock items and art series.

		Returns the cheapest card names and prices.

	fetchfromvortex(card_name)

		Fetches card prices from Vortex Games.

		Scrapes the card name and price, skipping sold-out items.

		Returns the cheapest card names and prices.

	fetch_all_stores(card_name)

		Runs the fetching functions for all three stores asynchronously.

		Returns a dictionary containing results from each store.

	process_card_file_async(input_file, output_file)

		Reads card names from the input file.

		Fetches price data for each card asynchronously.

		Writes a detailed output summary to the specified file.

	main()

		Handles user interaction via file dialogs.

		Triggers asynchronous processing of card files.


Future Improvements

	Add support for more online stores.

	Include currency conversion for international users.

	Optimize scraping and error handling for robustness.

	

Author

XavZur


