import argparse
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument("-path", type=str, default='cmd.sh')
args = parser.parse_args()


f = open(args.path, 'r',encoding='utf8')
for cmd in f.readlines():
    if '#' not in cmd and '\n' != cmd:
        print(cmd)
        subprocess.Popen(cmd, shell=True, stdout=None)

# cd valuation
# python run.py

# https://www.comet.com/investment/value-investing/view/PkbFWG2FKrx7U4ITj95YwUFZU/experiments