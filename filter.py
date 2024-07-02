def shellPort_filter(results):
    shell_ports = []
    for sublist in results:
        for item in sublist:
            if ("Service: shell" in item) or ("Service: bindshell" in item):
                shell_ports.append(sublist)
                break
    return shell_ports

def SMB_filter(results):
    smb_ports = []
    for sublist in results:
        for item in sublist:
            if "Service: microsoft-ds" in item or "Service: netbios-ssn" in item :
                smb_ports.append(sublist)
                break
    return smb_ports

def FTP_filter(results):
    ftp_ports = []
    for sublist in results:
        ftp_found = False
        for item in sublist:
            if "Service: ftp" in item:
                ftp_found = True
                ftp_ports.append(sublist)
    return ftp_ports

def get_product(port_info):
    product = None
    version = None
    for inner_list in port_info:
        for item in inner_list:
            key, value = item.split(': ', 1)
            if key == 'Product':
                product = value
            elif key == 'Version':
                version = value
    if product or version:
        return product.strip(), version.strip()
    else:
        return None