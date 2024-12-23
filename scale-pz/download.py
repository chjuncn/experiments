import urllib.request
import xml.etree.ElementTree as ET
import os
import time

def download_paper(search_query, output_dir="electron_papers"):
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Format the API query
    base_url = 'http://export.arxiv.org/api/query?'
    query_params = {
        'search_query': f'all:{search_query}',
        'start': 0,
        'max_results': 1000
    }
    url = base_url + urllib.parse.urlencode(query_params)
    
    # Get and parse the API response
    with urllib.request.urlopen(url) as response:
        xml_data = response.read()
    
    # Parse XML
    root = ET.fromstring(xml_data)
    
    # arXiv XML namespace
    namespace = {'arxiv': 'http://www.w3.org/2005/Atom'}
    
    # Get all entries
    entries = root.findall('arxiv:entry', namespace)
    if not entries:
        print("No papers found")
        return
    
    for entry in entries:
        # Get paper details
        title = entry.find('arxiv:title', namespace).text.strip().replace('\n', ' ')
        paper_id = entry.find('arxiv:id', namespace).text.split('/')[-1]
        
        # Construct PDF URL
        pdf_url = f'https://arxiv.org/pdf/{paper_id}.pdf'
        
        # Download the PDF
        output_file = os.path.join(output_dir, f"{paper_id}.pdf")
        print(f"Downloading: {title}")
        print(f"Saving to: {output_file}")
        
        try:
            urllib.request.urlretrieve(pdf_url, output_file)
            print("Download complete!")
        except Exception as e:
            print(f"Error downloading {title}: {e}")
        
        # Add a small delay to be nice to arXiv servers
        time.sleep(2)

# Example usage
download_paper("electron")