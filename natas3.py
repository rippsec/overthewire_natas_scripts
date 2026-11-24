#!/usr/bin/env python3

import requests,re,sys,signal,time,os
import base64 as b64
import html2text as h2t
from tabulate import tabulate
from bs4 import BeautifulSoup

def sig_handler(sig,frame):
  print("\n\n[+] Exiting...\n")
  sys.exit(0)
signal.signal(signal.SIGINT, sig_handler)

def robots(user,password):
  print(f"[+] Querying robots from {user}.py ...\n") 
  url = f"http://{user}.natas.labs.overthewire.org"
  path = "robots.txt"
  r = requests.get( f"{url}/{path}", auth=(user,password) )
  paths = re.findall(r"\/.*\/", r.text)
  return paths

def parse_directory_listing(html_content):
  """Extract file and directory links from Apache directory listing"""
  soup = BeautifulSoup(html_content, 'html.parser')
  links = []
  
  for link in soup.find_all('a', href=True):
    href = link['href']
    if href not in ['/', '../'] and not href.startswith('?'):
      links.append(href)
  
  return links

def crawl_directory(user, password, path, base_url, visited=None, depth=0, max_depth=3):
  if visited is None:
    visited = set()
  
  if depth > max_depth or path in visited:
    return []
  
  visited.add(path)
  findings = []
  
  print(f"{'  ' * depth}[+] Crawling: {path}")
  
  try:
    r = requests.get(f"{base_url}/{path}", auth=(user, password), timeout=10)
    
    if "Index of" in r.text:
      print(f"{'  ' * depth}[>] Directory found, parsing links...")
      links = parse_directory_listing(r.text)
      
      for link in links:
        if path.endswith('/'):
          full_path = f"{path}{link}"
        else:
          full_path = f"{path}/{link}"
        
        if link.endswith('/'):
          findings.extend(crawl_directory(user, password, full_path, base_url, visited, depth+1, max_depth))
        else:
          findings.extend(crawl_directory(user, password, full_path, base_url, visited, depth+1, max_depth))
    
    else:
      print(f"{'  ' * depth}[*] File found: {path}")
      flags = get_flag(r.text)
      findings.append({
        'path': path,
        'status': r.status_code,
        'content': r.text,
        'flags': flags
      })
  
  except Exception as e:
    print(f"{'  ' * depth}[!] Error accessing {path}: {e}")
  
  return findings

def make_request(user,password,path=""):
  print(f"[+] Sending request from {user}.py ...\n[+] user:{user} ; passwd:{password}") 
  url = f"http://{user}.natas.labs.overthewire.org"
  r = requests.get( f"{url}/{path}", auth=(user,password) )
  return r.status_code, r.text, r.cookies.get_dict(), user, password

def get_flag(req):
  flags = re.findall(r"\b[a-zA-Z0-9]{32}\b",req)
  if flags:
    return "\n---\n".join(flags)
  return "x"

def get_password():
  status, text, cookies, user, password = make_request(f"{os.path.basename(__file__)[:-3]}",f"{prev_level.get_password()}")
  return get_flag(text)

def dbg(status,raw_html,cookies,user,password,md5s):
  rendered_html = h2t.html2text(raw_html)
  table_data = [
      [f"[i] Status:{status}", ""],
      [f"[i] User",f"[i] Password"],
      [f"{user}",f"{password}"],
      ["[i] Raw HTML", "[i] Rendered HTML"],
      [raw_html,rendered_html],
      ["[i] Cookies", cookies],
      ["[i] Previous Flag", password],
      ["[+] Flag for Next Level", md5s]
  ]
  print(tabulate(table_data, tablefmt="grid", maxcolwidths=[70,40]))

if __name__ == "__main__":
  user = os.path.basename(__file__)[:-3]
  password = "3gqisGdR0pjm6tpkDKdIWO2hSvchLeYH"
  base_url = f"http://{user}.natas.labs.overthewire.org"
  
  paths = robots(user, password)
  
  all_findings = []
  
  for path in paths:
    print(f"\n{'='*60}")
    print(f"[+] Exploring path from robots.txt: {path}")
    print(f"{'='*60}\n")
    
    findings = crawl_directory(user, password, path.strip('/'), base_url)
    all_findings.extend(findings)
  
  print(f"\n\n{'='*60}")
  print("[+] SUMMARY OF FINDINGS")
  print(f"{'='*60}\n")
  
  for finding in all_findings:
    print(f"\n[>] Path: {finding['path']}")
    print(f"[>] Status: {finding['status']}")
    print(f"[>] Flags/Passwords: {finding['flags']}")
    print(f"[>] Content Preview: {finding['content'][:200]}...")
    print("-" * 60)
  
  if all_findings:
    last = all_findings[-1]
    status, text, cookies, _, _ = make_request(user, password, last['path'])
    dbg(status, text, cookies, user, password, last['flags'])
