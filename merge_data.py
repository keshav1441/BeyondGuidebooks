import os
import pandas as pd
from groq import Groq
from tqdm import tqdm
import dotenv

# Load environment variables
dotenv.load_dotenv()
GROK_API_KEY = os.getenv("GROK_API_KEY")

# Configure Groq
client = Groq(api_key=GROK_API_KEY)  # Replace with your actual key

# Folder with CSVs
data_folder = "data"
output_file = "final_heritage_data.csv"

# Collect unique site names
site_names = set()
csv_files = [os.path.join(data_folder, f) for f in os.listdir(data_folder) if f.endswith(".csv")]

for file in csv_files:
    try:
        df = pd.read_csv(file, header=None, encoding="latin1")
        for row in df.itertuples(index=False):
            for col in row:
                if isinstance(col, str) and len(col.strip().split()) > 1:
                    site_names.add(col.strip())
    except Exception as e:
        print(f"Error reading {file}: {e}")

# Prompt generator
def make_prompt(site_name):
    return f"""
You are a helpful AI assistant. Given the name of a heritage site, return a single CSV row with the format:
Site Name, City, State, Latitude, Longitude

Example:
Taj Mahal, Agra, Uttar Pradesh, 27.1751, 78.0421

Now do the same for: {site_name}
Just return the row, no explanation.
"""

# Query Groq API
def query_groq(site_name):
    prompt = make_prompt(site_name)
    completion = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=150,
        top_p=1.0,
        stream=False,
    )
    return completion.choices[0].message.content.strip()

# Generate structured data
results = []
for site in tqdm(sorted(site_names), desc="Processing sites"):
    try:
        row = query_groq(site)
        if row.count(",") >= 4:  # crude check for 5 columns
            results.append(row)
    except Exception as e:
        print(f"Failed to process '{site}': {e}")

# Write final CSV
with open(output_file, "w", encoding="utf-8") as f:
    f.write("Site Name,City,State,Latitude,Longitude\n")
    for row in results:
        f.write(row + "\n")

print(f"\n✅ Done! Saved to {output_file}")
