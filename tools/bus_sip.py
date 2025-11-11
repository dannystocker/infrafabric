#!/usr/bin/env python3
import json, sys, argparse; from pathlib import Path
P=Path.home()/'.if'/'sip_servers.json'
def L(): return json.loads(P.read_text()) if P.exists() else {}
def S(d): P.parent.mkdir(parents=True, exist_ok=True); P.write_text(json.dumps(d, indent=2))
def add(n,t,a): d=L(); d[n]={'type':t,'auth':dict(x.split('=') for x in a)}; S(d); print(f'Added {n}')
def test(n): d=L(); s=d.get(n); print(f"OK: {s['type']}" if s else 'Not found')
def call(n,**kw): print(f'Calling {n}: {kw}')
def hangup(n,**kw): print(f'Hangup {n}: {kw}')
def lst(): [print(f"{k}: {v['type']}") for k,v in L().items()]
def rm(n): d=L(); d.pop(n,None); S(d); print(f'Removed {n}')
def main():
 p=argparse.ArgumentParser(prog='if bus'); sp=p.add_subparsers(dest='cmd')
 a=sp.add_parser('add'); a.add_argument('proto'); a.add_argument('name'); a.add_argument('type', choices=['asterisk','freeswitch','kamailio','opensips','twilio','vonage','fusionpbx']); a.add_argument('--auth', nargs='+', default=[])
 sp.add_parser('list')
 t=sp.add_parser('test'); t.add_argument('proto'); t.add_argument('name')
 c=sp.add_parser('call'); c.add_argument('proto'); c.add_argument('name'); c.add_argument('params', nargs='*')
 h=sp.add_parser('hangup'); h.add_argument('proto'); h.add_argument('name'); h.add_argument('call_id')
 r=sp.add_parser('remove'); r.add_argument('proto'); r.add_argument('name')
 args=p.parse_args()
 if args.cmd=='add' and args.proto=='sip': add(args.name,args.type,args.auth)
 elif args.cmd=='test' and args.proto=='sip': test(args.name)
 elif args.cmd=='call' and args.proto=='sip': call(args.name,**{x.split('=')[0]:x.split('=')[1] for x in args.params if '='in x})
 elif args.cmd=='hangup' and args.proto=='sip': hangup(args.name,call_id=args.call_id)
 elif args.cmd=='list': lst()
 elif args.cmd=='remove' and args.proto=='sip': rm(args.name)
if __name__=='__main__': main()
