import requests
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time

def extract_fencer_data(url):
    """
    Extracts static fencer details using requests and BeautifulSoup.
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    data = {}
    data['FIE ID'] = url.rstrip('/').split('/')[-1]
    
    # Extract Name
    name_tag = soup.find('h1', class_='AthleteHero-fencerName')
    data['Name'] = name_tag.get_text(strip=True) if name_tag else None
    
    # Extract Image URL from inline style
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

    # Extract Category from dropdown
    category_select = soup.find('select', class_='js-athlete-dropdown-fencer-category')
    if category_select:
        selected_option = category_select.find('option', selected=True)
        data['Category'] = selected_option.get_text(strip=True) if selected_option else None
    else:
        data['Category'] = None

    # Extract Season (static from initial page load)
    season_select = soup.find('select', class_='js-season-dropdown')
    if season_select:
        selected_option = season_select.find('option', selected=True)
        data['Season'] = selected_option.get_text(strip=True) if selected_option else None
    else:
        data['Season'] = None

    data['Wins/losses'] = None  # Placeholder

    # Extract Rank
    rank_tag = soup.find('span', class_='ProfileInfo-rank')
    data['Rank'] = rank_tag.get_text(strip=True) if rank_tag else None

    # Extract Points (using string instead of text to avoid deprecation warnings)
    pts_label = soup.find(lambda tag: tag.name == 'span' and 'Pts' in tag.get_text())
    if pts_label:
        points_value = pts_label.find_next_sibling(string=True)
        data['Points'] = points_value.strip() if points_value else None
    else:
        data['Points'] = None

    # Extract Handedness (Left/Right)
    hand_label = soup.find(lambda tag: tag.name == 'span' and 'Hand' in tag.get_text())
    if hand_label:
        hand_value = hand_label.find_next_sibling(string=True)
        data['Left/Right'] = hand_value.strip() if hand_value else None
    else:
        data['Left/Right'] = None

    return data


if __name__ == "__main__":
    url = 'https://fie.org/athletes/22439'
    
    # Extract static fencer data.
    fencer_data = extract_fencer_data(url)
    print("Fencer Data:")
    print(fencer_data)
