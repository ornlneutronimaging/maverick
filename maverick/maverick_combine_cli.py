import argparse

parser = argparse.ArgumentParser(description="Combine a set of TOF folders")
parser.add_argument('--algorithm', choices=["mean", "median"])
args = parser.parse_args()

print(args.algorithm)
