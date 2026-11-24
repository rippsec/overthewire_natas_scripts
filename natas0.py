
import requests,re,sys,signal,time,os
import base64 as b64
import html2text as h2t
from tabulate import tabulate

def sig_handler(sig,frame):
  print("\n\n[+] Exiting...\n")
  sys.exit(0)

signal.signal(signal.SIGINT, sig_handler)

def make_request(user,password):
  print(f"[+] Sending request from {os.path.basename(__file__)} ...")
  url = f"http://{user}.natas.labs.overthewire.org"
  r = requests.get( url, auth=(user,password) )
  return r.status_code, r.text, r.cookies.get_dict()

def get_flag(req):
  flags = re.findall(r"\b[a-zA-Z0-9]{32}",req)
  if flags:
    return "\n---\n".join(flags)
  return "x"


def dbg(status,raw_html,cookies,md5s):
  
  rendered_html = h2t.html2text(raw_html)
  table_data = [
      [f"status:{status}", ""],
      ["Raw HTML", "Rendered HTML"],
      [raw_html,rendered_html],
      ["Cookies", cookies],
      ["md5s", md5s]
  ]

  print(tabulate(table_data, tablefmt="grid", maxcolwidths=[67,33]))


def get_password():
  status, text, cookies = make_request("natas0","natas0")
  return get_flag(text)

if __name__ == "__main__":
 
  status, text, cookies = make_request("natas0","natas0")
  flags = get_flag(text)
  dbg(status,text,cookies,flags)


