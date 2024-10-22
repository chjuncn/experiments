from bs4 import BeautifulSoup
import requests
import os


def download_html(url):
    saved_dir = "experiments/benchmark_data/htmls/" + url.split("/")[-1].split("?")[0]
    response = requests.get(url)

    if response.status_code == 200:
        html_content = response.text
    else:
        print(f"Failed to retrieve the webpage: {response.status_code}")
        exit

    # Parse the HTML
    soup = BeautifulSoup(html_content, "html.parser")

    img_tags = soup.find_all('img')
    img_urls = [img['src'] for img in img_tags if 'src' in img.attrs]
    os.makedirs(saved_dir, exist_ok=True)

    for img_url in img_urls:
        # Handle relative URLs
        if not img_url.startswith('http'):
            img_url = requests.compat.urljoin(url, img_url)
        
        try:
            img_response = requests.get(img_url)
            if img_response.status_code == 200:
                # Get the image name from the URL
                img_name = os.path.join(saved_dir, os.path.basename(img_url))
                with open(img_name, 'wb') as img_file:
                    img_file.write(img_response.content)
                print(f"Downloaded: {img_name}")
            else:
                print(f"Failed to download image: {img_url}")
        except Exception as e:
            print(f"Error downloading {img_url}: {e}")

    # Extract text or specific elements
    text = soup.get_text()  # Get all text
    with open(saved_dir + ".txt", "w") as f:
        f.write(text)


download_html("https://ourworldindata.org/economic-growth-since-1950")



# # Example: Extract all <h1> tags
# h1_tags = soup.find_all('h1')
# for tag in h1_tags:
#     print(tag.text)

