from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import requests
from bs4 import BeautifulSoup
from .models import AthleteProfile
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import requests
import pandas as pd
import PyPDF2
import io
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import json
 

def extract_fencer_data(url):
    """
    Extracts static fencer details from the given FIE URL.
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    data = {}
    data['FIE_page'] = url
    data['FIE_id'] = url.rstrip('/').split('/')[-1]
    
    # Extract Name
    name_tag = soup.find('h1', class_='AthleteHero-fencerName')
    data['name'] = name_tag.get_text(strip=True) if name_tag else None

    # Extract Flag (using country code from a CSS class)
    nationality_div = soup.find('div', class_='AthleteHero-nationality')
    span = nationality_div.find('span') if nationality_div else None
    span_classes = span.get('class') if span else []
    if len(span_classes) >= 3:
        data["flag"] = span_classes[2].split('--')[-1]
    else:
        data["flag"] = None

    # Extract Handedness
    hand_span = soup.find('span', string='Hand')
    next_span = hand_span.find_next('span') if hand_span else None
    data["handedness"] = next_span.get_text(strip=True) if next_span else None

    # Extract Age
    age_span = soup.find('span', string='Age')
    next_span = age_span.find_next('span') if age_span else None
    # Convert age to integer if possible
    try:
        data["age"] = int(next_span.get_text(strip=True)) if next_span else None
    except (ValueError, TypeError):
        data["age"] = None

    # Extract Image URL (if available)
    image_div = soup.find('div', class_='AthleteHero-fencerImage')
    if image_div and 'style' in image_div.attrs:
        style = image_div['style']
        start = style.find("url(")
        end = style.find(")", start)
        data['image'] = style[start+4:end].strip('\'"')
    else:
        data['image'] = None

    # Extract Weapon info
    weapon_tag = soup.find('div', class_='ProfileInfo-item')
    data['weapon'] = weapon_tag.get_text(strip=True) if weapon_tag else None

    # Extract Rank
    rank_tag = soup.find('span', class_='ProfileInfo-rank')
    data['rank'] = rank_tag.get_text(strip=True) if rank_tag else None

    # Extract Residence
    residence_tag = soup.find('span', class_='AthletBio-stat', string=lambda s: s and 'Residence' in s)
    if residence_tag:
        data['residence'] = residence_tag.find_next('span').get_text(strip=True)
    else:
        data['residence'] = None

    # Extract Points
    pts_label = soup.find(lambda tag: tag.name == 'span' and 'Pts' in tag.get_text())
    if pts_label:
        points_value = pts_label.find_next_sibling(string=True)
        try:
            data['points'] = int(points_value.strip()) if points_value else 0
        except (ValueError, TypeError):
            data['points'] = 0
    else:
        data['points'] = 0

    return data

def extract_competitions_last_five_seasons(url):
    driver = webdriver.Chrome()  # Ensure chromedriver is in PATH
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
        time.sleep(2)  # wait a bit for page load
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


@login_required
def create_athlete_profile(request):
    if request.method == 'POST':
        # Get the form inputs
        fie_link = request.POST.get('fie_link')
        form_name = request.POST.get('fencer_name')  # fallback if scraping fails
        bio = request.POST.get('bio')
        # Note: Video upload is accepted by the form, but handling file uploads requires additional code.
        # For this example, we ignore the video upload.

        # Use the scraper to extract data from the provided URL
        scraped_data = extract_fencer_data(fie_link)

        # Create or update the AthleteProfile for the current user
        profile, created = AthleteProfile.objects.get_or_create(user=request.user)
        profile.FIE_page = scraped_data.get('FIE_page')
        profile.FIE_id = scraped_data.get('FIE_id')
        # Use scraped name if available; otherwise, use the form input
        profile.name = scraped_data.get('name') or form_name
        profile.flag = scraped_data.get('flag')
        profile.handedness = scraped_data.get('handedness')
        profile.age = scraped_data.get('age')
        # For the image, you might need to download the image and save it;
        # for now, we simply store the URL if your model is adapted accordingly.
        # profile.image = scraped_data.get('image')
        profile.weapon = scraped_data.get('weapon')
        profile.rank = scraped_data.get('rank')
        profile.residence = scraped_data.get('residence')
        profile.points = scraped_data.get('points')
        profile.bio = bio
        profile.save()

        return redirect('athlete_home')  # Adjust as needed
    return render(request, 'athlete/create_profile.html')

def profile_dashboard(request):
    # For now, simply render the dashboard template.
    # Later you can add logic to load profile data and statistics.
    return render(request, 'profiles/profile_dashboard.html')

from django.shortcuts import render

def add_profile_information(request):
    return render(request, 'athlete/add_profile_information.html')

def view_profile(request):
    return render(request, 'athlete/view_profile.html')

def add_view_recruiters(request):
    return render(request, 'athlete/add_view_recruiters.html')
