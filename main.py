import requests
from bs4 import BeautifulSoup
# import wmi


def extractData():

    # Making a GET request
    r = requests.get('https://learn.microsoft.com/en-us/windows-hardware/design/minimum/supported/windows-11-22h2-supported-intel-processors')

    # parse the HTML
    soup = BeautifulSoup(r.content, 'html.parser')

    table = soup.find('table')
    rows = table.find_all('tr')[1:]

    supported_cpus = []

    for row in rows:
        cols = row.find_all('td')
        if len(cols) >= 3:
            manufacturer = cols[0].text.strip().replace('®', '(R)')
            brand = cols[1].text.strip().replace('®', '(R)').replace('™', '(TM)')
            model = cols[2].text.strip()
            cpu_full = f"{manufacturer} {brand} {model.replace('processor', '').replace('  ', ' ').replace('-', ' ')}"
            supported_cpus.append(cpu_full.lower())

    return supported_cpus

def getProccessor():
    # c = wmi.WMI()

    # for cpu in c.Win32_Processor():
    #     name = cpu.Name

    # return name
    return "11th Gen Intel(R) Core(TM) i5-1145G7 @ 2.60GHz   1.50 GHz"

def normalizeComputerProccessor(name):
    normalizedName = name.lower().replace('-', ' ')
    splitName = normalizedName.split('@')[0].strip()
    return splitName
      
def isItCompatable(name, supported_list):
    for support in supported_list:
        if name in support or support in name:
            return True
    return False


def main():
    # cpus = extractData()
    # for cpu in cpus:
    #     print(cpu)

    supported_cpus = extractData()
    detected_cpu = getProccessor()
    normalized_cpu = normalizeComputerProccessor(detected_cpu)

    print(f"Detected CPU: {detected_cpu}")
    print(f"Normalized CPU: {normalized_cpu}")

    if isItCompatable(normalized_cpu, supported_cpus):
        print("✅ Your CPU is compatible with Windows 11!")
    else:
        print("❌ Your CPU is NOT on the supported list for Windows 11.")


if __name__ == "__main__":
    main()