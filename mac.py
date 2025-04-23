import tkinter as tk
from tkinter import scrolledtext
import requests
from bs4 import BeautifulSoup
import platform
import subprocess

# Only import wmi if on Windows
if platform.system() == "Windows":
    import wmi


def extractData():
    r = requests.get('https://learn.microsoft.com/en-us/windows-hardware/design/minimum/supported/windows-11-22h2-supported-intel-processors')
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
    if platform.system() == "Windows":
        c = wmi.WMI()
        for cpu in c.Win32_Processor():
            return cpu.Name
    else:
        return subprocess.getoutput("sysctl -n machdep.cpu.brand_string")

def normalizeComputerProccessor(name):
    normalizedName = name.lower().replace('-', ' ')
    splitName = normalizedName.split('@')[0].strip()
    return splitName
      
def isItCompatable(name, supported_list):
    for support in supported_list:
        if name in support or support in name:
            return True
    return False

def checkSecureBoot():
    if platform.system() != "Windows":
        return None
    try:
        output = subprocess.check_output([
            "powershell", "-Command", "Confirm-SecureBootUEFI"
        ]).decode().strip()
        return output == "True" if output in ["True", "False"] else None
    except Exception:
        return None
    
def checkTpm():
    if platform.system() != "Windows":
        return False, "TPM check not supported on macOS/Linux"
    try:
        output = subprocess.check_output([
            "powershell",
            "-Command",
            "Get-WmiObject -Namespace 'Root\\CIMv2\\Security\\MicrosoftTpm' -Class Win32_Tpm"
        ]).decode()

        if 'IsEnabled_InitialValue' in output and 'True' in output:
            version_line = [line for line in output.splitlines() if 'SpecVersion' in line]
            version = version_line[0].split(':')[1].strip() if version_line else 'Unknown'
            return True, version
        else:
            return False, "TPM not enabled or not found"
    except Exception as e:
        return False, f"Error checking TPM: {e}"

def run_checks(output_box):
    output_box.delete('1.0', tk.END)

    supported_cpus = extractData()
    detected_cpu = getProccessor()
    normalized_cpu = normalizeComputerProccessor(detected_cpu)
    
    output_box.insert(tk.END, f"Detected CPU: {detected_cpu}\n")
    output_box.insert(tk.END, f"Normalized CPU: {normalized_cpu}\n")

    if isItCompatable(normalized_cpu, supported_cpus):
        output_box.insert(tk.END, "✅ CPU is compatible with Windows 11.\n")
    else:
        output_box.insert(tk.END, "❌ CPU is NOT compatible with Windows 11.\n")

    secure_boot = checkSecureBoot()
    if secure_boot is True:
        output_box.insert(tk.END, "✅ Secure Boot is ENABLED.\n")
    elif secure_boot is False:
        output_box.insert(tk.END, "❌ Secure Boot is DISABLED.\n")
    else:
        output_box.insert(tk.END, "⚠️ Secure Boot status could not be determined or not supported.\n")

    tpm_status, tpm_info = checkTpm()
    if tpm_status:
        output_box.insert(tk.END, f"✅ TPM is ENABLED. Version: {tpm_info}\n")
    else:
        output_box.insert(tk.END, f"❌ TPM Check Failed. Reason: {tpm_info}\n")

def main():
    root = tk.Tk()
    root.title("Windows 11 Compatibility Checker")
    root.geometry("600x400")

    tk.Label(root, text="Windows 11 Compatibility Checker", font=("Helvetica", 16)).pack(pady=10)

    output_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=70, height=15)
    output_box.pack(padx=10, pady=10)

    tk.Button(root, text="Check Compatibility", command=lambda: run_checks(output_box)).pack(pady=5)

    root.mainloop()

if __name__ == "__main__":
    main()
