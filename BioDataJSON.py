import requests
import json
from bs4 import BeautifulSoup

def extract_fencer_data(url):
    """
    Extracts static fencer details using requests and BeautifulSoup.
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    data = {}
    data['FIE Page'] = url

    data['FIE ID'] = url.rstrip('/').split('/')[-1]
    
    # Extract Name
    name_tag = soup.find('h1', class_='AthleteHero-fencerName')
    data['Name'] = name_tag.get_text(strip=True) if name_tag else None
    
    # Extract Image URL
    image_div = soup.find('div', class_='AthleteHero-fencerImage')
    if image_div and 'style' in image_div.attrs:
        style = image_div['style']
        start = style.find("url(")
        end = style.find(")", start)
        data['Image'] = style[start+4:end].strip('\'"')
    else:
        data['Image'] = None

    # Extract Weapon info
    weapon_tag = soup.find('div', class_='ProfileInfo-item')
    data['Weapon'] = weapon_tag.get_text(strip=True) if weapon_tag else None

    # Extract Rank
    rank_tag = soup.find('span', class_='ProfileInfo-rank')
    data['Rank'] = rank_tag.get_text(strip=True) if rank_tag else None

    rank_tag = soup.find('span', class_='AthletBio-stat test')
    data['Residence'] = rank_tag.get_text(strip=True) if rank_tag else None

    # Extract Points
    pts_label = soup.find(lambda tag: tag.name == 'span' and 'Pts' in tag.get_text())
    if pts_label:
        points_value = pts_label.find_next_sibling(string=True)
        data['Points'] = points_value.strip() if points_value else None
    else:
        data['Points'] = None

    # Save data as JSON
    with open("fencer_data.json", "w") as json_file:
        json.dump(data, json_file, indent=4)

    return data

if __name__ == "__main__":
    url = 'https://fie.org/athletes/22439'
    fencer_data = extract_fencer_data(url)
    print("Fencer data saved to fencer_data.json")
