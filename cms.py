import requests
import re

def scan_website(url):
    # Check for common CMS directories and files
    common_directories = ["/administrator", "/wp-admin", "/user", "/admin", "/typo3", "/craft"]
    for directory in common_directories:
        full_url = f"{url}{directory}"
        try:
            response = requests.get(full_url)
            if response.status_code == 200:
                print(f"Found potential CMS directory: {full_url}")
        except requests.exceptions.RequestException:
            pass

    # Check server headers for CMS fingerprinting
def detect_cms(url):
    try:
        # Fetch the webpage HTML content
        response = requests.get(url)
        html_content = response.text

        # Check for common CMS indicators in the HTML content
        cms_indicators = {
            'WordPress': r'<!-- Powered by WordPress|<meta name="generator" content="WordPress|/wp-content/',
            'Joomla': r'Powered by Joomla|/media/system/',
            'Drupal': r'Powered by Drupal|/sites/all/',
            'Magento': r'Powered by Magento',
            'Shopify': r'myshopify.com',
            'Typo3': r'<!-- This website is powered by TYPO3|/typo3/',
            'Craft CMS': r'Powered by Craft CMS|/admin/',
        }

        for cms, indicator in cms_indicators.items():
            if re.search(indicator, html_content, re.IGNORECASE):
                return cms

        # If no CMS detected
        return 'Unknown CMS'

    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

# Example usage:
if __name__ == "__main__":
    url = 'http://dev.devvortex.htb'  # Replace with the URL of the website you want to check
    detected_cms = detect_cms(url)
    if detected_cms:
        print(f"The CMS of {url} is: {detected_cms}")
    else:
        print(f"Failed to detect CMS for {url}")

    scan_website(url)