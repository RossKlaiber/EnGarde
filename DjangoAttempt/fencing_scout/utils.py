import requests
import json
from bs4 import BeautifulSoup
import time
import pandas as pd
import PyPDF2
import io
import re
from selenium import webdriver
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

def extract_fencer_data(url):
    """
    Extracts static fencer details using requests and BeautifulSoup.
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    data = {}
    data['FIE Page'] = url
    data['FIE ID'] = url.rstrip('/').split('/')[-1]
    
    name_tag = soup.find('h1', class_='AthleteHero-fencerName')
    data['Name'] = name_tag.get_text(strip=True) if name_tag else None

    nationality_div = soup.find('div', class_='AthleteHero-nationality')
    span = nationality_div.find('span') if nationality_div else None
    span_classes = span.get('class') if span else []
    result = span_classes[2].split('--')[-1] if len(span_classes) >= 3 else None
    data["Flag"] = result
    
    hand_span = soup.find('span', string='Hand')
    next_span = hand_span.find_next('span') if hand_span else None
    data["Handedness"] = next_span.get_text(strip=True) if next_span else None

    age_span = soup.find('span', string='Age')
    next_span = age_span.find_next('span') if age_span else None
    data["Age"] = next_span.get_text(strip=True) if next_span else None
    
    image_div = soup.find('div', class_='AthleteHero-fencerImage')
    if image_div and 'style' in image_div.attrs:
        style = image_div['style']
        start = style.find("url(")
        end = style.find(")", start)
        data['Image'] = style[start+4:end].strip('\'"')
    else:
        data['Image'] = None

    weapon_tag = soup.find('div', class_='ProfileInfo-item')
    data['Weapon'] = weapon_tag.get_text(strip=True) if weapon_tag else None

    rank_tag = soup.find('span', class_='ProfileInfo-rank')
    data['Rank'] = rank_tag.get_text(strip=True) if rank_tag else None

    residence_tag = soup.find('span', class_='AthletBio-stat test')
    data['Residence'] = residence_tag.get_text(strip=True) if residence_tag else None

    pts_label = soup.find(lambda tag: tag.name == 'span' and 'Pts' in tag.get_text())
    if pts_label:
        points_value = pts_label.find_next_sibling(string=True)
        data['Points'] = points_value.strip() if points_value else None
    else:
        data['Points'] = None

    with open("fencer_data.json", "w") as json_file:
        json.dump(data, json_file, indent=4)

    return data

def get_pdf_url(base_url):
    url = base_url.rstrip('/') + "/results/poolsResults/pdf?lang=en"
    if "competitions" in url:
        return url.replace("competitions", "competition")
    return url

def download_and_extract_row(pdf_url, name):
    try:
        response = requests.get(pdf_url)
        if response.status_code != 200:
            alternative_url = pdf_url.replace("competitions", "competition")
            response = requests.get(alternative_url)
            if response.status_code != 200:
                return 0, 0, 0
        with io.BytesIO(response.content) as open_pdf:
            reader = PyPDF2.PdfReader(open_pdf)
            text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
            if name not in text:
                return 0, 0, 0
            lines = text.split("\n")
            for i, line in enumerate(lines):
                if name in line:
                    surrounding_lines = lines[i:i+10]
                    extracted_info = " ".join(surrounding_lines)
                    numbers = re.findall(r'\d+', extracted_info)
                    if len(numbers) >= 3:
                        return int(numbers[3]), int(numbers[4]), int(numbers[3])-int(numbers[4])
    except Exception as e:
        print(f"Error processing PDF {pdf_url}: {e}")
    return 0, 0, 0

def extract_competitions_last_five_seasons(url):
    driver = webdriver.Chrome()  # Make sure the ChromeDriver is installed and in your PATH.
    wait = WebDriverWait(driver, 10)
    driver.get(url)
    
    competitions_list = []
    dropdown_elem = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "select.js-season-dropdown")))
    select = Select(dropdown_elem)
    num_options = min(5, len(select.options))
    
    for i in range(num_options):
        dropdown_elem = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "select.js-season-dropdown")))
        select = Select(dropdown_elem)
        season_text = select.options[i].text.strip()
        select.select_by_index(i)
        time.sleep(3)
        
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        results_container = soup.find('div', class_='js-athlete-results-tab-container')
        if results_container:
            links = results_container.find_all('a', class_='Historial-link')
            for link in links:
                href = link.get('href')
                if href and href.startswith('/'):
                    href = 'https://fie.org' + href
                competition_name_div = link.find("div", class_="Historial-label Historial-label--colorDark")
                competition_name = competition_name_div.get_text(strip=True) if competition_name_div else ""
                competitions_list.append({
                    "Year": season_text,
                    "Competition": competition_name,
                    "Link": href
                })
    driver.quit()
    return competitions_list
