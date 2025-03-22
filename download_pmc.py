import requests
import xml.etree.ElementTree as ET
import subprocess
import urllib.parse

if __name__ == "__main__": 

    inp = input("Enter search term: ")
    search_term = urllib.parse.quote(inp)

    print(f"Searching for: {inp}")

    # Step 1: Fetch XML data from the URL
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pmc&term={search_term}&field=title&usehistory=y"
    response = requests.get(url)

    if response.status_code != 200:
        print("Error fetching data from PMC")
        exit()

    # Step 2: Parse XML and extract IDs
    root = ET.fromstring(response.content)
    ids = [id_elem.text for id_elem in root.findall(".//Id")]

    if not ids:
        print("No IDs found in response.")
        exit()

    print(f"Retrieved {len(ids)} IDs.")
    print("IDs:", ids) 

    # Step 3: Execute AWS CLI command for each ID
    s3_bucket = "pmc-oa-opendata/oa_noncomm/txt/all" 
    s3_prefix = "PMC"

    for pmc_id in ids:
        s3_key = f"{s3_prefix}{pmc_id}.txt"
        aws_command = ["aws", "s3", "cp", f"s3://{s3_bucket}/{s3_key}", ".", "--no-sign-request", "--quiet"]

        try:
            subprocess.run(aws_command, check=True)
            print(f"Downloaded {s3_key} from S3 successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to download {s3_key}: {e}")

    print("Script execution completed.")
