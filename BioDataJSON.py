import requests
import json
from bs4 import BeautifulSoup
import time

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

    #Extract country id
    nationality_div = soup.find('div', class_='AthleteHero-nationality')
    span = nationality_div.find('span') if nationality_div else None
    span_classes = span.get('class') if span else []
    #the 3rd element contains the country code, after the "--"
    result = span_classes[2].split('--')[-1]
    data["Flag"] = result
    
    # Extract left / right handness
    hand_span = soup.find('span', string='Hand')
    next_span = hand_span.find_next('span') if hand_span else None
    data["Handedness"] = next_span.get_text(strip=True) if next_span else None

    # Extract age
    age_span = soup.find('span', string='Age')
    next_span = age_span.find_next('span') if age_span else None
    data["Age"] = next_span.get_text(strip=True) if next_span else None
    
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

    residence_tag = soup.find('span', class_='AthletBio-stat test')
    data['Residence'] = residence_tag.get_text(strip=True) if residence_tag else None

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
