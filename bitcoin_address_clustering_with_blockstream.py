
import requests
import os
import csv
import platform
import networkx as nx
import matplotlib.pyplot as plt
from tqdm import tqdm  # Progress bar

# Maximum address limit for clustering
MAX_ADDRESSES = 5000

# Define recursion depth limit to avoid going too deep into clustering
MAX_DEPTH = 3

# Function to fetch transactions using Blockstream API
def get_transactions(address, api_url="https://blockstream.info/api"):
    '''
    Fetches transactions for a Bitcoin address using Blockstream's public API.
    Users can replace the `api_url` with their own API endpoint if desired.
    '''
    url = f"{api_url}/address/{address}/txs"
    response = requests.get(url)

    try:
        if response.status_code == 200:
            transactions = response.json()
            return transactions
        else:
            print(f"Error: Failed to fetch transactions, Status Code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error while fetching or parsing the response: {e}")
        return None

# Function to detect if a transaction is likely a CoinJoin transaction
def is_coinjoin(tx):
    inputs = tx.get('vin', [])
    input_addresses = [vin['prevout']['scriptpubkey_address'] for vin in inputs if 'prevout' in vin]
    
    if len(inputs) > 5 and len(tx.get('vout', [])) > 5:
        return True  # Likely CoinJoin transaction based on number of inputs and outputs

    reused_addresses = set()
    for addr in input_addresses:
        if addr in reused_addresses:
            return False  # Not a CoinJoin, there's address reuse
        reused_addresses.add(addr)

    return True  # CoinJoin detected due to input/output count and no address reuse

# Function to detect likely change addresses
def detect_change_address(tx):
    outputs = tx.get('vout', [])
    inputs = tx.get('vin', [])
    
    input_value = sum(float(vin['prevout'].get('value', 0)) for vin in inputs if 'prevout' in vin)
    likely_change = None

    for vout in outputs:
        output_value = float(vout.get('value', 0))
        output_address = vout.get('scriptpubkey_address')

        if output_value < input_value:
            likely_change = output_address
            break
    
    return likely_change

# Recursive function to cluster addresses based on Common Input Ownership Heuristic (CIOH), CAD, and CoinJoin detection
def cluster_addresses_recursive(addresses, current_depth, address_cluster, processed_addresses, total_addresses, pbar, graph, api_url):
    if current_depth > MAX_DEPTH or total_addresses >= MAX_ADDRESSES:
        return total_addresses

    for address in addresses:
        if total_addresses >= MAX_ADDRESSES:
            break

        if address in processed_addresses:
            continue

        processed_addresses.add(address)
        transactions = get_transactions(address, api_url)
        if transactions is None:
            continue

        for tx in transactions:
            if total_addresses >= MAX_ADDRESSES:
                break

            if is_coinjoin(tx):
                continue

            inputs = tx.get('vin', [])
            input_addresses = [vin['prevout']['scriptpubkey_address'] for vin in inputs if 'prevout' in vin]

            for addr in input_addresses:
                if addr not in address_cluster:
                    address_cluster.add(addr)
                    graph.add_edge(address, addr)
                    total_addresses += 1
                    pbar.update(1)
                if total_addresses >= MAX_ADDRESSES:
                    break

            change_address = detect_change_address(tx)
            if change_address and change_address not in address_cluster:
                address_cluster.add(change_address)
                graph.add_edge(address, change_address)
                total_addresses += 1
                pbar.update(1)

            if total_addresses >= MAX_ADDRESSES:
                break

        new_addresses = address_cluster - processed_addresses
        total_addresses = cluster_addresses_recursive(new_addresses, current_depth + 1, address_cluster, processed_addresses, total_addresses, pbar, graph, api_url)

    return total_addresses

# Wrapper function for clustering starting with the initial target address
def cluster_addresses(target_address, api_url="https://blockstream.info/api"):
    address_cluster = set()
    processed_addresses = set()
    total_addresses = 0

    graph = nx.Graph()

    with tqdm(total=MAX_ADDRESSES, desc="Clustering Addresses") as pbar:
        total_addresses = cluster_addresses_recursive({target_address}, 1, address_cluster, processed_addresses, total_addresses, pbar, graph, api_url)

    return address_cluster, total_addresses, graph

# Function to save clustered address data to CSV
def save_clustered_addresses(address_cluster, output_folder, target_address, entity):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    file_path_cluster = os.path.join(output_folder, f"{target_address}_clustered_addresses.csv")
    with open(file_path_cluster, mode='w', newline='') as file:
        writer = csv.writer(file)

        writer.writerow([f"Bitcoin Address: {target_address}", f"Entity: {entity}"])
        writer.writerow(["Clustered Addresses"])

        for address in address_cluster:
            writer.writerow([address])

    print(f"Clustered addresses saved to: {file_path_cluster}")
    open_csv_file(file_path_cluster)

# Function to visualize the address clustering graph using networkx and matplotlib
def visualize_graph(graph, target_address):
    plt.figure(figsize=(10, 10))
    pos = nx.spring_layout(graph)
    nx.draw(graph, pos, with_labels=True, node_size=50, font_size=8, node_color="lightblue", edge_color="gray")
    plt.title(f"Address Clustering for {target_address}")
    plt.show()

# Function to open the CSV file automatically based on the operating system
def open_csv_file(file_path):
    try:
        if platform.system() == "Darwin":
            os.system(f"open {file_path}")
        elif platform.system() == "Windows":
            os.startfile(file_path)
        elif platform.system() == "Linux":
            os.system(f"xdg-open {file_path}")
        else:
            print(f"Cannot automatically open the file on this platform: {platform.system()}")
    except Exception as e:
        print(f"Error opening file: {e}")

# Main script execution
if __name__ == "__main__":
    target_address = input("Please paste the Bitcoin address to analyze: ")
    entity = input("Please enter the entity related to this Bitcoin address (e.g., exchange, wallet service, etc.): ")

    # Optionally, the user can provide a custom API URL; default is Blockstream's API
    api_url = input("Please enter the API URL for fetching transactions (leave blank to use Blockstream's API): ")
    if not api_url:
        api_url = "https://blockstream.info/api"

    output_folder = input("Please enter the folder where results should be saved (e.g., './output'): ")

    address_cluster, total_addresses, graph = cluster_addresses(target_address, api_url)
    save_clustered_addresses(address_cluster, output_folder, target_address, entity)
    print(f"Total addresses collected: {total_addresses}")
    visualize_graph(graph, target_address)
