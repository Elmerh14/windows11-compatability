import requests
from bs4 import BeautifulSoup
import wmi


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
            manufacturer = cols[0].text.strip()
            brand = cols[1].text.strip()
            model = cols[2].text.strip()
            cpu_full = f"{manufacturer} {brand} {model.replace('processor', '').replace('  ', ' ')}"
            supported_cpus.append(cpu_full)

    return supported_cpus

def getProccessor():
    c = wmi.WMI()

    for cpu in c.Win32_Processor():
        name = cpu.Name

    return name
      
# def isItCompatable(name): 

    

def main():
    cpus = extractData()
    for cpu in cpus:
        print(cpu)

    print(getProccessor())


if __name__ == "__main__":
    main()