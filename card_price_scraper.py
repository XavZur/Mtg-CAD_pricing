import re
import requests
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
import tkinter as tk
from tkinter import filedialog
import asyncio

def fetchfrom401(card_name):
    base_url = "https://store.401games.ca/search?q="
    search_url = f"{base_url}{card_name.replace(' ', '+')}"

    r = requests.get(search_url)
    
    soup = BeautifulSoup(r.content, "html5lib")
    # Seperate products on the webpage
    products_table = soup.select_one("div.products.products-list.search-list")
    if products_table:
        #Find each product to look through
        products = products_table.find_all("div", class_="box product")
        price_array = {}

        for item in products:
            # Extract the product name 
            title_tag = item.select_one("div.product-title a.title")
            if title_tag:  
                name = title_tag.get_text(strip=True)
                if card_name.lower() not in name.lower():
                    continue
            
            # Extract the product price
            price_tag = item.select_one("span.price")
            if price_tag:
                price = price_tag.get_text(strip=True).replace("From", "").strip()
                if "Sold Out" in price:
                    continue
                else:
                    price_match = re.search(r"\d+\.\d+", price)
                    if price_match:
                        price = float(price_match.group())

                    # Check if this is the cheapest in-stock option
                        if price not in price_array:
                            price_array[price] = []
                        price_array[price].append(name)
        
        if price_array:
            cheapest_price = min(price_array.keys())
            cheapest_cards = price_array[cheapest_price]

            return f"Cheapest cards: {', '  .join(cheapest_cards)}, Price: ${cheapest_price:.2f}"
        else:
            return "No in-stock cards found."
   

from playwright.async_api import async_playwright

async def fetchfromf2f(card_name):
    base_url = "https://www.facetofacegames.com/search/?keyword="
    search_url = f"{base_url}{card_name.replace(' ', '+')}"

    try:
        async with async_playwright() as p:
            # Launch the browser
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(search_url, timeout=100000)

            # Wait for the content to load
            try:
                await page.wait_for_selector(".hawk-results__item", timeout=60000)
            except Exception as e:
                print(f"Selector not found or timeout: {e}")
                return "No results found or page took too long to load."

            # Extract data from all cards
            card_data = []
            cards = await page.query_selector_all(".hawk-results__item")
            for card in cards:
                # Extract card names
                subtitle_element = await card.query_selector(".hawk-results__hawk-contentSubtitle")
                subtitle = await subtitle_element.text_content() if subtitle_element else "No subtitle"

                # Skip products that aren't accurately matched
                if "art series" in subtitle.lower():
                    continue
                # if card_name.lower() not in subtitle.lower():
                #     continue

                # Extract stock status
                stock_element = await card.query_selector(".hawkStock")
                stock_status = await stock_element.text_content() if stock_element else "Stock status unknown"

                # Skip out-of-stock cards
                if stock_status.lower() == "out of stock":
                    continue

                # Extract price
                price_element = await card.query_selector(".retailPrice.hawkPrice")
                price_text = await price_element.text_content() if price_element else None

                # Convert the extracted price to a float
                try:
                    price = float(price_text.replace("CAD $", "").replace(",", "").strip()) if price_text else None
                except ValueError:
                    price = None

                # Add card data 
                if price is not None:
                    card_data.append({
                        "subtitle": subtitle,
                        "price": price,
                    })

            await browser.close()

            # If no valid cards are found, exit
            if not card_data:
                return "No cards are in stock."

            # Find the minimum price and filter cheapest cards
            min_price = min(card["price"] for card in card_data)
            cheapest_cards = [card for card in card_data if card["price"] == min_price]

            # Group and sort unique card subtitles for the lowest price
            unique_names = ", ".join(sorted(set(card["subtitle"] for card in cheapest_cards)))

            return f"Cheapest cards: {unique_names}, Price: ${min_price:.2f}"

    except Exception as e:
        return f"An error occurred: {e}"


def fetchfromvortex(card_name):
    base_url = "https://vortexgames.ca/search?type=product&q="
    search_url = f"{base_url}{card_name.replace(' ', '+')}"
    
    r = requests.get(search_url)
    
    soup = BeautifulSoup(r.content, "html5lib")
    products_table = soup.select_one(".grid.grid--uniform")
    if products_table:
        products = products_table.find_all("div", class_="grid-product__content")
        price_array = {}

        for item in products:
            # Extract status tag and skip items marked as "Sold Out"
            sold_out_tag = item.select_one(".grid-product__tag.grid-product__tag--sold-out")
            if sold_out_tag:
                continue
            
            # Extract proce
            title_tag = item.select_one(".grid-product__title.grid-product__title--body")
            name = title_tag.get_text(strip=True) if title_tag else "Unknown Product"
            
            # Skip items that dont have the correct name
            if card_name.lower() not in name.lower():
                continue

            # Extract the product price
            price_tag = item.select_one(".grid-product__price")
            if price_tag:
                price_text = price_tag.get_text(strip=True).replace("From", "").strip()
                price_match = re.search(r"\d+\.\d+", price_text)
                if price_match:
                    price = float(price_match.group())
                    
                    # Store the price and corresponding product name
                    if price not in price_array:
                        price_array[price] = []
                    price_array[price].append(name)

        # Find the cheapest price and format the output
        if price_array:
            cheapest_price = min(price_array.keys())
            cheapest_cards = price_array[cheapest_price]
            return f"Cheapest cards: {', '.join(cheapest_cards)}, Price: ${cheapest_price:.2f}"
        else:
            return "No in-stock cards found."
    else:
        return "No products found on the page."


async def fetch_all_stores(card_name):
    loop = asyncio.get_event_loop()
    result_401 = await loop.run_in_executor(None, fetchfrom401, card_name)
    result_vortex = await loop.run_in_executor(None, fetchfromvortex, card_name)
    result_f2f = await fetchfromf2f(card_name)

    return {
        "401 Games": result_401,
        "Face to Face Games": result_f2f,
        "Vortex Games": result_vortex,
    }

async def process_card_file_async(input_file, output_file):
    # Read input file synchronously
    with open(input_file, 'r') as infile:
        card_names = [line.strip() for line in infile if line.strip()]
        card_names = [re.sub(r"^\d+\s*", "", name) for name in card_names]

    # Process cards asynchronously
    tasks = [fetch_all_stores(card_name) for card_name in card_names]
    results = await asyncio.gather(*tasks)

    # Variables to track total cost and out-of-stock cards
    total_cost = 0.0
    out_of_stock_cards = []

    # Write output file synchronously
    with open(output_file, 'w') as outfile:
        for card_name, result in zip(card_names, results):
            outfile.write(f"Card: {card_name}\n")
            
            # Track the lowest price for this card
            cheapest_price = float('inf')
            card_out_of_stock = True

            for store, data in result.items():
                outfile.write(f"{store}: {data}\n")
                
                # Extract price if available
                if "Price: $" in data:
                    try:
                        price = float(re.search(r"Price: \$([0-9]+\.[0-9]+)", data).group(1))
                        cheapest_price = min(cheapest_price, price)
                        card_out_of_stock = False
                    except AttributeError:
                        pass

            if card_out_of_stock:
                out_of_stock_cards.append(card_name)
            else:
                total_cost += cheapest_price
            
            outfile.write("\n")

        with open(output_file, 'r') as infile:
            original_content = infile.read()

        # Write total cost and out-of-stock cards at the top
        header_content = "Deck Analysis\n"
        header_content += "=====================\n"
        header_content += f"Total Deck Cost: ${total_cost:.2f}\n"
        if out_of_stock_cards:
            header_content += "Out of Stock Cards:\n"
            header_content += "\n".join(out_of_stock_cards) + "\n"
        else:
            header_content += "All cards are in stock.\n"
        header_content += "=====================\n\n"

# Write the new content followed by the original content
        with open(output_file, 'w') as outfile:
            outfile.write(header_content + original_content)


def main():
    # Initialize root window
    root = tk.Tk()
    root.withdraw()

    # Prompt to select the input file
    input_path = filedialog.askopenfilename(
        title="Select a file with card names",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
    )

    if not input_path:
        print("No input file selected. Exiting.")
        return

    # Prompt to select or name the output file
    output_path = filedialog.asksaveasfilename(
        title="Save the output file",
        defaultextension=".txt",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
    )

    if not output_path:
        print("No output file selected. Exiting.")
        return

    async def async_main():
        print(f"Processing file: {input_path}")
        print(f"Output will be saved to: {output_path}")
        await process_card_file_async(input_path, output_path)
        print("Processing complete!")

    asyncio.run(async_main())

if __name__ == "__main__":
    main()