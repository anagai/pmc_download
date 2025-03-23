*** E-utilities introduction: https://www.ncbi.nlm.nih.gov/books/NBK25497/#chapter2.Usage_Guidelines_and_Requiremen
*** Documentation on search endpoint: https://www.ncbi.nlm.nih.gov/books/NBK25499/#_chapter4_ESearch_
*** NLM APIs: https://www.ncbi.nlm.nih.gov/home/develop/api/#:~:text=The%20E%2Dutilities%20are%20the,search%2C%20link%20and%20retrieval%20operations.
*** Entrez Direct Unix CLI: https://www.ncbi.nlm.nih.gov/books/NBK179288/

Running download_pmc_pdf.py

1) Install libraries from the project root directory
   pip install -r requirements.txt
2) Run script 
   python .\download_pmc_pdf.pyenv
3) Will prompt you to enter the disease

It is set to download 20 documents. You can change this by changing the 
MAX_ARTICLES constant in the script. The extracted texts will be saved to directory 
of the disease name. Each directory will have manifest file with urls to original pdfs.

