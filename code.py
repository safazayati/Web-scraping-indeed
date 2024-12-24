from bs4 import BeautifulSoup
import os
import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

# --- Configuration du WebDriver ---
CHROMEDRIVER_PATH = "C:/Program Files/Google/Chrome/chromedriver-win64/chromedriver.exe"
service = Service(CHROMEDRIVER_PATH)
driver = webdriver.Chrome(service=service)

# --- URL de recherche Indeed ---
BASE_URL = "https://fr.indeed.com/jobs?q=software+engineer&l=Paris+%2875%29&from=searchOnDesktopSerp&vjk=25c7d4554d0cf477"

# --- Fonction de scraping ---
def scrape_indeed_with_selenium(url, max_pages=6):
    jobs = []
    driver.get(url)

    for page in range(max_pages):
        print(f"Scraping page {page + 1}...")

        # Attendre que les annonces se chargent
        time.sleep(5)

        # Extraire le HTML de la page
        soup = BeautifulSoup(driver.page_source, "html.parser")
        job_cards = soup.find_all("div", class_="job_seen_beacon")

        # Debugging : Vérifiez si des cartes ont été trouvées
        print(f"Nombre de cartes trouvées : {len(job_cards)}")

        if not job_cards:
            print("Aucune offre d'emploi trouvée sur cette page.")
            break

        for card in job_cards:
            try:
                title = card.find("h2", class_="jobTitle")
                company = card.find("span", class_="companyName")
                location = card.find("div", class_="companyLocation")
                summary = card.find("div", class_="job-snippet")

                # Debugging : Affichez les données extraites
                print({
                    "title": title.get_text(strip=True) if title else "N/A",
                    "company": company.get_text(strip=True) if company else "N/A",
                    "location": location.get_text(strip=True) if location else "N/A",
                    "summary": summary.get_text(strip=True) if summary else "N/A"
                })

                jobs.append({
                    "title": title.get_text(strip=True) if title else "N/A",
                    "company": company.get_text(strip=True) if company else "N/A",
                    "location": location.get_text(strip=True) if location else "N/A",
                    "summary": summary.get_text(strip=True) if summary else "N/A"
                })
            except Exception as e:
                print(f"Erreur lors de l'extraction : {e}")

        # Passer à la page suivante
        try:
            next_button = driver.find_element(By.XPATH, '//a[contains(@aria-label, "Next")]')
            next_button.click()
        except Exception:
            print("Aucune page suivante trouvée.")
            break

    driver.quit()
    return jobs

# --- Exporter les résultats en CSV ---
def export_to_csv(jobs, filename="indeed_jobs.csv"):
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["title", "company", "location", "summary"])
        writer.writeheader()
        writer.writerows(jobs)
    print(f"Résultats enregistrés dans {filename}")

# --- Lancer le scraping ---
if __name__ == "__main__":
    scraped_jobs = scrape_indeed_with_selenium(BASE_URL, max_pages=3)
    if scraped_jobs:
        export_to_csv(scraped_jobs, filename="C:/Users/R I B/OneDrive/Bureau/indeed_jobs.csv")
    else:
        print("Aucun emploi trouvé.")
