Bitcoin Address Clustering Script
This script clusters Bitcoin addresses using the Common Input Ownership Heuristic (CIOH) and CoinJoin detection. It analyzes Bitcoin transactions and generates clusters of addresses that are likely associated with the same entity.
Requirements
Before using the script, ensure you have the following Python libraries installed:
```
pip install requests tqdm networkx matplotlib
```

How the Script Works
1. **Address Clustering:** The script clusters Bitcoin addresses by analyzing transactions for a given Bitcoin address. It uses heuristics such as the Common Input Ownership Heuristic (CIOH) and CoinJoin detection to group addresses.
2. **API Requirement:** The script requires an API to fetch Bitcoin transaction data. Users need to provide their own API URL to fetch the transaction history for a Bitcoin address.
3. **File Output:** The script saves the clustered addresses to a CSV file in the folder specified by the user.
4. **Graph Visualization:** After clustering, the script visualizes the address connections in a graph using NetworkX and Matplotlib.
How to Use the Script
1. Clone or Download the Script
First, download or copy the script to your local environment.
2. Run the Script
Run the script in your Python environment. You will be prompted to provide the following inputs:
- **Bitcoin Address:** The address you want to analyze.
- **Entity:** The entity associated with the Bitcoin address (optional, for reference).
- **API URL:** The URL for the API that will be used to fetch Bitcoin transactions. You must replace this with your own API endpoint.
- **Output Folder:** The folder where the clustered addresses will be saved as a CSV file.
3. Example Workflow
```bash
python bitcoin_address_clustering.py
```
The script will prompt you for the following:
- **Bitcoin Address:** For example, `1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa`
- **Entity:** For example, `Satoshi Nakamoto`
- **API URL:** For example, `https://example.com/api` (you need to replace this with your own working API)
- **Output Folder:** For example, `./output`

4. Output
- **CSV File:** The script saves a CSV file in the specified output folder, containing the clustered Bitcoin addresses.
- **Graph Visualization:** The script generates a graph that visually represents the relationships between clustered addresses.

5. File Auto-Opening
After the CSV file is saved, the script attempts to open the file automatically depending on your operating system. If this fails, you can manually navigate to the output folder and open the CSV file.
Example Input and Output
- **Bitcoin Address:** `1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa`
- **Entity:** `Satoshi Nakamoto`
- **API URL:** `https://example.com/api`
- **Output Folder:** `./output`

### Example Output CSV:
```
Bitcoin Address: 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa, Entity: Satoshi Nakamoto
Clustered Addresses
1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa
1Ez69SnzzmePmZX3WpEzMKTrcBF2gpNQ55
...
```

API Integration
You need to provide your own API to fetch transaction data. The API should return transactions for a given Bitcoin address in JSON format. The placeholder API endpoint used in the script is:

```
https://example.com/api/address/{address}/txs
```

Replace `https://example.com/api` with the actual base URL of the API you are using.
Script Details
- **Clustering Depth Limit:** The script uses a depth limit (`MAX_DEPTH`) to avoid deep recursion while clustering addresses. By default, this is set to 3.
- **Address Limit:** The total number of addresses processed is capped by `MAX_ADDRESSES`, which is set to 5000. You can change this limit in the script if needed.
Notes
- The script skips transactions that are detected as CoinJoin, where multiple participants combine their inputs into a single transaction.
- Change addresses are detected and added to the cluster when possible.
- You must have a working API to fetch Bitcoin transaction data, as the script does not provide its own API service.
