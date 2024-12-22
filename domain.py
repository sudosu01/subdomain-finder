#!/usr/bin/env python3  # Shebang for Linux users to run the script directly

import subprocess
import dns.resolver  # For subdomain discovery
import pyfiglet
import requests
import re
import time

# Subdomain enumeration techniques: known subdomains and crt.sh API.
known_subdomains = ['www', 'ftp', 'mail', 'blog', 'dev', 'api', 'shop', 'm', 'web', 'app', 'news', 'test']

def print_sudo_su_logo():
    """Generate and display the 'sudo su' logo using pyfiglet"""
    ascii_art = pyfiglet.figlet_format("sudo su", font="slant")  # 'sudo su' ASCII art
    print(ascii_art)

def get_subdomains(domain):
    """Get subdomains of the domain using DNS resolver"""
    subdomains = set()  # Using a set to avoid duplicate entries
    resolver = dns.resolver.Resolver()
    resolver.nameservers = ['8.8.8.8', '8.8.4.4']  # Use Google's public DNS
    resolver.timeout = 10  # Timeout after 10 seconds
    resolver.lifetime = 10  # Set lifetime to 10 seconds
    
    try:
        # Query DNS for subdomains of the main domain
        answers = resolver.resolve(domain, 'A')
        for answer in answers:
            subdomains.add(domain)
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
        print(f"No subdomains found for {domain}")
    except dns.resolver.LifetimeTimeout:
        print(f"DNS resolution timed out while resolving {domain}")
    
    return subdomains

def brute_force_subdomains(domain):
    """Brute-force known subdomains for a domain"""
    subdomains = set()
    for sub in known_subdomains:
        full_domain = f"{sub}.{domain}"
        try:
            # Attempt DNS resolution for each known subdomain
            dns.resolver.resolve(full_domain, 'A')
            subdomains.add(full_domain)
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
            pass  # Skip if subdomain doesn't exist
        except dns.resolver.LifetimeTimeout:
            print(f"DNS timeout while checking {full_domain}.")
            continue
    return subdomains

def get_crt_sh_subdomains(domain):
    """Use crt.sh API to find subdomains by checking certificates"""
    url = f"https://crt.sh/?q=%25.{domain}&output=json"
    subdomains = set()
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            for cert in data:
                subdomain = cert['name_value']
                # Extract subdomains by splitting at commas
                subdomains.update([s.strip() for s in subdomain.split(',') if domain in s])
        else:
            print(f"Error fetching crt.sh data for {domain}")
    except requests.exceptions.RequestException as e:
        print(f"Error querying crt.sh for {domain}: {e}")
    
    return subdomains

def run_sublist3r(domain):
    """Run Sublist3r tool to discover subdomains"""
    print("Running Sublist3r for subdomain enumeration...")
    try:
        result = subprocess.run(["python3", "Sublist3r/sublist3r.py", "-d", domain], capture_output=True, text=True)
        subdomains = set(result.stdout.splitlines())
        return subdomains
    except Exception as e:
        print(f"Error running Sublist3r: {e}")
        return set()

def run_amass(domain):
    """Run Amass tool to discover subdomains"""
    print("Running Amass for subdomain enumeration...")
    try:
        result = subprocess.run(["amass", "enum", "-d", domain], capture_output=True, text=True)
        subdomains = set(result.stdout.splitlines())
        return subdomains
    except Exception as e:
        print(f"Error running Amass: {e}")
        return set()

def run_assetfinder(domain):
    """Run Assetfinder tool to discover subdomains"""
    print("Running Assetfinder for subdomain enumeration...")
    try:
        result = subprocess.run(["./assetfinder", "--subs", domain], capture_output=True, text=True)
        subdomains = set(result.stdout.splitlines())
        return subdomains
    except Exception as e:
        print(f"Error running Assetfinder: {e}")
        return set()

def analyze_domain_and_subdomains(domain):
    """Analyze the given domain and its subdomains"""
    print(f"\nAnalyzing domain and subdomains for {domain}...")

    # Get subdomains from DNS resolution of main domain
    subdomains = get_subdomains(domain)

    # Brute-force common subdomains
    subdomains.update(brute_force_subdomains(domain))

    # Get subdomains from crt.sh
    subdomains.update(get_crt_sh_subdomains(domain))

    # Run Sublist3r for deeper enumeration
    subdomains.update(run_sublist3r(domain))

    # Run Amass for deeper enumeration
    subdomains.update(run_amass(domain))

    # Run Assetfinder for deeper enumeration
    subdomains.update(run_assetfinder(domain))

    # Output the main domain
    print(f"Main domain: {domain}")

    # Output the subdomains
    if subdomains:
        print("\nSubdomains found:")
        for sub in sorted(subdomains):
            print(f"- {sub}")
    else:
        print("No subdomains found.")

# Main script execution
if __name__ == "__main__":
    print_sudo_su_logo()  # Display the custom "sudo su" ASCII art

    # Ask for domain input from the user
    domain_input = input("Enter a domain to check for subdomains (e.g., example.com): ")

    # Call the function to find subdomains of the domain
    analyze_domain_and_subdomains(domain_input)