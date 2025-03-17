import requests
from bs4 import BeautifulSoup

def get_twitter_trends_24(country="united-states"):
    # Construct the URL for the specific country or region on Trends24
    url = f"https://trends24.in/{country}/"

    # Make a GET request.
    # Including a User-Agent helps avoid being blocked by some servers.
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to retrieve page. Status code: {response.status_code}")
        return None

    # Parse the HTML
    soup = BeautifulSoup(response.text, "html.parser")
    print(soup.prettify())

    # Find the table (adjust the selector to match what you see in DevTools)
    # For example, if the table has class="trend-table"
    table = soup.find("table", class_="the-table")
    if not table:
        print("Could not find the trend table on the page.")
        return None

    # Grab all table rows in <tbody> (if there's a <thead>, skip it)
    tbody = table.find("tbody", class_="list")
    if not tbody:
        print("No table body found.")
        return None

    rows = tbody.find_all("tr")
    if not rows:
        print("No rows found in the trend table.")
        return None

    # Extract data from each row
    trend_data = []
    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 5:
            # Skip if the row doesn't have the expected 5 columns
            continue

        rank = cols[0].get_text(strip=True)
        trending_topic = cols[1].get_text(strip=True)
        top_position = cols[2].get_text(strip=True)
        tweet_count = cols[3].get_text(strip=True)
        duration = cols[4].get_text(strip=True)

        trend_data.append({
            "Rank": rank,
            "Trending Topic": trending_topic,
            "Top Position": top_position,
            "Tweet Count": tweet_count,
            "Duration": duration,
        })

    return trend_data

if __name__ == "__main__":
    trends = get_twitter_trends_24("united-states")
    if trends:
        for t in trends:
            print(t)
