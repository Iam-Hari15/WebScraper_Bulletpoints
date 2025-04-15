import requests
import re

#Firecrawl API Key
FIRECRAWL_API_KEY = "Your api key here" #put you firecrawl apikey here (log into firecrawl and get free api keys)

# Clean and extract important bullet points
def clean_and_format(text):
    # Remove markdown links and URLs
    text = re.sub(r'\[.*?\]\(.*?\)', '', text)
    text = re.sub(r'https?://\S+', '', text)

    # Remove HTML tags and unnecessary characters
    text = re.sub(r'<.*?>', '', text)
    text = re.sub(r'\\+', '', text)
    text = re.sub(r'[^a-zA-Z0-9\s.,?!\'"-]', '', text)
    text = re.sub(r'\s{2,}', ' ', text)
    text = re.sub(r'\n+', '\n', text)

    # Break into sentence-like chunks
    lines = re.split(r'\. |\n|- ', text)

    # Filter and keep only meaningful lines
    clean_lines = [
        line.strip().capitalize()
        for line in lines
        if 40 < len(line.strip()) < 200 and not line.strip().lower().startswith((
            'copyright', 'privacy', 'click', 'read more', 'sign in', 'menu'
        ))
    ]

    # Deduplicate and limit to 10 bullet points
    seen = set()
    bullets = []
    for line in clean_lines:
        if line not in seen:
            bullets.append(f"- {line}.")
            seen.add(line)
        if len(bullets) == 10:
            break

    return bullets

#Scrape webpage content using Firecrawl
def scrape_webpage(url):
    print(f"🔍 Scraping: {url}")
    headers = {
        "Authorization": f"Bearer {FIRECRAWL_API_KEY}",
        "Content-Type": "application/json"
    }
    response = requests.post(
        "https://api.firecrawl.dev/v1/scrape",
        headers=headers,
        json={"url": url}
    )
    if response.status_code != 200:
        print(f"❌ Firecrawl Error: {response.status_code} - {response.text}")
        return None

    return response.json()["data"].get("markdown", "")

#Save the clean bullets to a text file
def save_to_txt(bullets, url):
    with open("scraped_notes.txt", "w", encoding="utf-8") as f:
        f.write(f"📝 Notes from: {url}\n\n")
        for bullet in bullets:
            f.write(f"{bullet}\n")
    print("✅ Notes saved to 'scraped_notes.txt'")

#Main
def main():
    print("🔗 Enter the URL:")
    url = input("→ ").strip()

    content = scrape_webpage(url)
    if not content:
        print("❌ Could not extract valid content.")
        return

    bullets = clean_and_format(content)
    if not bullets:
        print("❌ No meaningful info found.")
        return

    save_to_txt(bullets, url)

if __name__ == "__main__":
    main()
