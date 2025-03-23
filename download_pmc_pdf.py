import requests
import os
import fitz  # PyMuPDF for PDF to text conversion
import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import quote

# Need these libraries also: frontend, tools, PyMuPDF
# Need to create /static folder
inp = input("Enter search term: ")
SEARCH_TERM = quote(inp)

# 🔍 Search term (change for a different rare disease)
MAX_ARTICLES = 20  # Limit the number of downloaded articles

# 📂 Folder to store text files
SAVE_DIR = SEARCH_TERM.replace(" ", "_")
os.makedirs(SAVE_DIR, exist_ok=True)

# 🔗 Base URL for PubMed Central
PMC_BASE_URL = "https://www.ncbi.nlm.nih.gov/pmc/articles/"
# Base URL for PMC articles
PDF_BASE_URL = "https://pmc.ncbi.nlm.nih.gov/articles/"

def search_pubmed_open_access(search_term, max_results=20):
    """
    Search PubMed Central (PMC) for open-access articles and return their PMC IDs.
    """
    search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = {
        "db": "pmc",  # Search only in PubMed Central
        "term": f'"{search_term}"[Title]',  # Searching for term in title only
        "retmax": max_results,
        "retmode": "xml"
    }
    response = requests.get(search_url, params=params)
    response.raise_for_status()

    root = BeautifulSoup(response.text, "xml")
    #print(root.prettify())
    pmc_ids = [id_elem.text for id_elem in root.find_all("Id")]

    print(f"✅ Found {len(pmc_ids)} free articles.")
    return pmc_ids[:max_results]  # Limit the number of articles

def get_pdf_link(pmc_id):
    """
    Scrape the PMC article page to find the correct PDF link.
    """
    article_url = f"{PMC_BASE_URL}PMC{pmc_id}/"
    print(f"🔎 Checking article: {article_url}")
    
    try:
        response = requests.get(article_url, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        #print(soup.prettify())
        # Find the correct PDF link
        pdf_link = None
        for link in soup.find_all("a", href=True):
            if "pdf" in link["href"]:
                pdf_link = f"{PDF_BASE_URL}PMC{pmc_id}/{link["href"]}"
                break
        
        if pdf_link:
            print(f"📄 Found PDF: {pdf_link}")
            return pdf_link
        else:
            print("❌ No PDF link found.")
            return None
    except Exception as e:
        print(f"⚠️ Error fetching PDF link: {e}")
        return None

def download_and_convert_pdf(pdf_url, text_filename):
    """
    Download a PDF, extract text, and save it as a .txt file.
    """
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(pdf_url, headers=headers, stream=True)
        response.raise_for_status()

        # Use PyMuPDF to extract text
        doc = fitz.open(stream=response.content, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()

        with open(text_filename, "w", encoding="utf-8") as txt_file:
            txt_file.write(text)

        print(f"📄 Saved text file: {text_filename}")
        return True
    except Exception as e:
        print(f"⚠️ Error downloading or converting PDF: {e}")
        return False

def main():
    print(f"🔎 Searching for open-access articles on '{SEARCH_TERM}'...")

    # Step 1: Get free full-text articles
    pmc_ids = search_pubmed_open_access(SEARCH_TERM, max_results=MAX_ARTICLES)
    if not pmc_ids:
        print("❌ No free articles found!")
        return
    
    # Step 2: Process each article
    downloaded_texts = []
    for i, pmc_id in enumerate(pmc_ids):
        print(f"\n📥 Processing article {i + 1}/{len(pmc_ids)} - PMC{pmc_id}")

        # Step 3: Get the correct PDF link
        pdf_url = get_pdf_link(pmc_id)
        if not pdf_url:
            continue
        
        # Step 4: Download and convert PDF to text
        text_filename = os.path.join(SAVE_DIR, f"PMC_{pmc_id}.txt")
        if download_and_convert_pdf(pdf_url, text_filename):
            downloaded_texts.append({"PMC_ID": pmc_id, "PDF_URL": pdf_url, "Text_File": text_filename})

    # Step 5: Save metadata
    if downloaded_texts:
        df = pd.DataFrame(downloaded_texts)
        csv_filename = os.path.join(SAVE_DIR, "downloaded_articles.csv")
        df.to_csv(csv_filename, index=False)
        print(f"\n📂 Saved metadata to {csv_filename}")

if __name__ == "__main__":
    main()