import requests
import re
from bs4 import BeautifulSoup

pwsc_details = []

def scrape_officer_details(base_url, company_number):
    # Ensure the company number is always eight characters long with leading zeroes if numeric
    if company_number.isnumeric():
        company_number = company_number.zfill(8)
    else:
        company_number = company_number.upper()    
    url = base_url + f"/company/{company_number.upper()}/officers"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to retrieve the base officers page: {url} : {response.status_code}")
        return []
    soup = BeautifulSoup(response.content, 'html.parser')
    company_header = soup.find('div', class_='company-header')
    company_name_tag = company_header.find('h1', class_='heading-xlarge') if company_header else None
    company_name = company_name_tag.text.strip().upper() if company_name_tag else "N/A"
    company_number_tag = company_header.find('p', id='company-number').find('strong') if company_header else None
    extracted_company_number = company_number_tag.text.strip() if company_number_tag else "N/A"

    # with open("soup_output.txt", "w", encoding="utf-8") as file:
    #     file.write(soup.prettify())
    officers = []
    # Find all officer appointments
    appointments = soup.find_all('div', class_=re.compile(r'appointment-\d+'))
    for appointment in appointments:
        # Extract officer details
        name_tag = appointment.find('span', id=re.compile(r'officer-name-\d+'))
        name = name_tag.text.strip() if name_tag else "N/A"
        role_tag = appointment.find('dd', id=re.compile(r'officer-role-\d+'))
        role = role_tag.text.strip() if role_tag else "N/A"
        status_tag = appointment.find('span', id=re.compile(r'officer-status-tag-\d+'))
        status = status_tag.text.strip() if status_tag else "N/A"
        if status == "Active":
            officers.append({
                "Entity1": name,
                "Role": role,
                "Entity2": company_name,
                "Entity2Number": extracted_company_number
            })
    return officers  

def scrape_pwsc(base_url,company_number):
    # Ensure the company number is always eight characters long with leading zeroes if numeric
    if company_number.isnumeric():
        company_number = company_number.zfill(8)
    else:
        company_number = company_number.upper()
    url = base_url + f"/company/{company_number.upper()}/persons-with-significant-control"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to retrieve the base pwsc page: {url}: {response.status_code}")
        return
    soup = BeautifulSoup(response.content, 'html.parser')
    # with open("soup_output.txt", "w", encoding="utf-8") as file:
    #     file.write(soup.prettify())
    company_header = soup.find('div', class_='company-header')
    element1 = company_header.find('h1', class_='heading-xlarge') if company_header else None
    extracted_name = element1.text.strip() if element1 else "N/A"
    element2 = soup.find('div', class_='appointments-list').find('div', class_='appointment-1').find('b')
    pwsc_name = element2.text.strip().upper() if element2 else "N/A"
    reg_number_element = soup.find('dd', id='psc-registration-number-1')
    registration_number = reg_number_element.text.strip() if reg_number_element else "N/A"
    return {"Entity1": pwsc_name, "Role": "pwsc", "Entity2": extracted_name, "Entity2Number": registration_number}

def scrape_master(base_url, company_number, iterations):
    global pwsc_details  # Use global lists to store results
    visited_companies = set()  # To avoid re-scraping the same company
    queue = [company_number]  # Start with the initial company number
    for _ in range(iterations):
        if not queue:
            break  # Stop if there are no more companies to process
        current_company = queue.pop(0)
        if current_company in visited_companies:
            continue  # Skip if already visited
        visited_companies.add(current_company)
        pwsc = scrape_pwsc(base_url, current_company)
        if pwsc:
            pwsc_details.append(pwsc)
            # Add the registration number to the queue for further scraping
            if pwsc["Entity2Number"] != "N/A":
                queue.append(pwsc["Entity2Number"])
    return pwsc_details

def spider_scrape(base_url, company_number, iterations):
    combined_results = []  # Unified list to store all collected data
    visited_companies = set()  # To avoid revisiting companies
    queue = [company_number]  # Start with the initial company number
    # Scrape officers for the top-level company first
    top_level_officers = scrape_officer_details(base_url, company_number)
    combined_results.extend(top_level_officers)
    for _ in range(iterations):
        if not queue:
            break  # Stop if there are no more companies to process
        current_company = queue.pop(0)
        if current_company in visited_companies:
            continue  # Skip if already visited
        visited_companies.add(current_company)
        # Collect PWSC details
        pwsc = scrape_pwsc(base_url, current_company)
        if pwsc:
            if pwsc["Entity1"] != "N/A":
                combined_results.append(pwsc)  # Add PWSC details to the combined results
            # Add the registration number to the queue for further scraping
            if pwsc["Entity2Number"] != "N/A" and pwsc["Entity2Number"] not in visited_companies:
                queue.append(pwsc["Entity2Number"])
            # Collect officer details for the PWSC entity
            officers = scrape_officer_details(base_url, pwsc["Entity2Number"])
            combined_results.extend(officers)
    return combined_results
