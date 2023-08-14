import time
import requests
import asyncio
import ntplib
from datetime import datetime
from termcolor import colored
import socket
import netifaces
import aiohttp
import asyncio
import socket
import speedtest
from tqdm import tqdm


 
acUrl = 'https://pastebin.com/raw/RtHkkwmW'
alarmsUrl = 'https://pastebin.com/raw/AJJqZ2LV'
ntpUrl = 'https://pastebin.com/raw/VH65zZFu'
intercomUrl = 'https://pastebin.com/raw/b0gUybbw'
camerasUrl = 'https://pastebin.com/raw/1aSY0jLj'

class colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

print("--------------------------------------------------")
print("Welcome to the Verkada Networking Test Tool")
print("--------------------------------------------------")
print("\nCapabilities:")
print("  - TCP endpoints")
print("  - NTP reachability")
print("  - Download/Uplaod test")
print("\nNote: UDP testing is not currently supported.")
print("\nFor questions or feedback, please contact Casey Keller.\n")



time.sleep(1)
#Convert text response to a list of domains
try:
    print('Gathering FQDN endpoints...')
    allUrls = requests.get(camerasUrl).text.split('\r\n')
    acUrl = requests.get(acUrl).text.split('\r\n')
    allUrls = allUrls + acUrl
    verkada_endpoints = allUrls + requests.get(alarmsUrl).text.split('\r\n')
    sipEndpoints =requests.get(intercomUrl).text.split('\r\n')
    ntpEndpoints =requests.get(ntpUrl).text.split('\r\n')
    
except:
    print('Please verify you have a valid IP4 address and can reach the internet.')
    exit()



ntp_server = "verkada.com"  # Replace with the NTP server you want to test
timeout = 3  # Timeout in seconds
sslPorts = [443]
sipPorts = [5060, 5061]
ntpPorts = [123]
async def test_port(endpoint, port, timeout):
    try:
        reader, writer = await asyncio.wait_for(asyncio.open_connection(endpoint, port), timeout=timeout)
        writer.close()
        return True
    except asyncio.TimeoutError:
        return False
    except Exception as e:
        return False

def speedtest_with_progress():
    st = speedtest.Speedtest()

    # Progress bar for download
    print("Testing Download Speed...")
    for _ in tqdm(range(10), desc="Download", ncols=100):
        if _ == 0:
            st.download()
        time.sleep(0.1)  # tqdm is very fast, so we introduce a slight delay for a better visual effect

    # Progress bar for upload
    print("\nTesting Upload Speed...")
    for _ in tqdm(range(10), desc="Upload", ncols=100):
        if _ == 0:
            st.upload()
        time.sleep(0.1)

    # Getting ping value
    print("\nGetting Best Server based on Ping...")
    st.get_best_server()
    ping_val = st.results.ping

    # Printing results
    print("\nResults:")
    print(f"Download Speed: {st.results.download / 1_000_000:.2f} Mbps")
    print(f"Upload Speed: {st.results.upload / 1_000_000:.2f} Mbps")
    print(f"Ping: {ping_val} ms")

async def test_endpoints(endpoints, ports, timeout):
    results = []

    for endpoint in endpoints:
        for port in ports:
            result = await test_port(endpoint, port, timeout)
            results.append((endpoint, port, result))

    return results
def test_ntp_server(server):
    try:
        client = ntplib.NTPClient()
        response = client.request(server, timeout=timeout)
        return response.tx_time
    except (ntplib.NTPException, socket.timeout):
        return None

async def get_ipv4_address():
    """Get the IPV4 address of the client."""
    return netifaces.ifaddresses(netifaces.gateways()['default'][netifaces.AF_INET][1])[netifaces.AF_INET][0]['addr']

async def test_google_connectivity():
    """Test if we can connect to google.com on port 443 asynchronously."""
    url = "https://www.google.com"
    timeout = aiohttp.ClientTimeout(total=5)
    
    async with aiohttp.ClientSession(timeout=timeout) as session:
        try:
            async with session.get(url) as response:
                return response.status == 200
        except:
            return False

def get_dhcp_info(interface):
    """Get the DHCP information for the given interface."""
    info = netifaces.ifaddresses(interface).get(netifaces.AF_INET, [{}])[0]
    return {
        'address': info.get('addr', 'N/A'),
        'netmask': info.get('netmask', 'N/A'),
        'broadcast': info.get('broadcast', 'N/A')
    }

def get_default_gateway():
    """Get the default gateway."""
    gateway = netifaces.gateways()['default'].get(netifaces.AF_INET, (None, None))
    return gateway[0]

def get_dns_servers():
    """Get the DNS servers."""
    with open("/etc/resolv.conf", "r") as f:
        lines = f.readlines()
        dns_servers = [line.split()[1] for line in lines if line.startswith("nameserver")]
    return dns_servers
async def main():
    sslResults = await test_endpoints(verkada_endpoints, sslPorts, timeout=3)
    sipResults = await test_endpoints(sipEndpoints, sipPorts, timeout=3)
    for endpoint, port, result in sslResults:
        port_status = "open" if result else "closed"
        if port_status == 'open':
            print(f"TCP port {port} for {endpoint} is {colors.OKGREEN}{port_status}{colors.ENDC}")
        else: 
            print(f"TCP port {port} for {endpoint} is {colors.FAIL}{port_status}{colors.ENDC}")
    for endpoint, port, result in sipResults:
        port_status = "open" if result else "closed"
        if port_status == 'open':
            print(f"TCP port {port} for {endpoint} is {colors.OKGREEN}{port_status}{colors.ENDC}")
        else: 
            print(f"TCP port {port} for {endpoint} is {colors.FAIL}{port_status}{colors.ENDC}")

    for server in ntpEndpoints:
        ntp_time = test_ntp_server(server)
        
        if ntp_time is not None:
            ntp_datetime = datetime.fromtimestamp(ntp_time)
            print(colored(f"NTP server {server} time: {ntp_datetime}", "green"))
        else:
            print(colored(f"Unable to query NTP server {server}", "red"))
    print('')
    print('Running a speed test. This will take a bit...')
    speedtest_with_progress()
    iface = netifaces.gateways()['default'][netifaces.AF_INET][1]
    dhcp_info = get_dhcp_info(iface)
    print('')
    print('Netowrking information:')
    print(f"Interface: {iface}")
    print(f"IPV4 Address: {await get_ipv4_address()}")
    print(f"Netmask: {dhcp_info['netmask']}")
    print(f"Broadcast Address: {dhcp_info['broadcast']}")
    print(f"Default Gateway: {get_default_gateway()}")
    print(f"DNS Servers: {', '.join(get_dns_servers())}")

    if await test_google_connectivity():
        print("Successfully connected to google.com over port 443!")
    else:
        print("Failed to connect to google.com over port 443.")
if __name__ == "__main__":
    asyncio.run(main())




