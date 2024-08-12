import pandas as pd
from tqdm import tqdm

from scraper import Scraper

if __name__ == "__main__":
    df = pd.read_excel("invoice_position.xlsx")
    if "images" not in df.columns:
        df["images"] = "[]"
    items_name_without_images = df.loc[df["images"] == "[]", "item_name"].unique()
    count = 0
    total_images = 10
    scraper = Scraper(total_images)

    for item_name in tqdm(items_name_without_images):
        scraped_links = scraper.scrape_images(query=item_name, count_run=count)
        count += 1
        df.loc[df["item_name"] == item_name, "images"] = str(scraped_links) if scraped_links != [] else ""
        if count % 5 == 0:
            df.to_excel("invoice_position.xlsx", index=False)
            count = 0
