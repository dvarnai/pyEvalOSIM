# Evaluate the quality of a simulation

import argparse
import numpy as np
import pandas as pd
import csv

parser = argparse.ArgumentParser(description='Extract marker locations from C3D files and save in TRC format.')
parser.add_argument('prefix', metavar='P', type=str,
                    help='Prefix of the run to evaluate trailed by the path to the output files')

def loadSto(path, delimiter = '\t'):
    with open(path, 'r') as f:
        line = f.readline()
        while line:
            if line.find('endheader') == 0:
                header = f.readline().strip().split(delimiter)
                break
            line = f.readline()
        data = pd.read_csv(f, delimiter=delimiter, names=header, usecols=np.arange(len(header)))
    return data

def getForceKeys(states,forces):

    reserves = [col for col in forces.columns if '_reserve' in col]
    muscles = []
    residuals = []

    headers = map(lambda x: x.split('/'), states.columns.values)
    for column in headers:
        if len(column) == 1:
            continue
        elif column[1] == 'jointset' and column[-2] in forces.columns and column[-2] + " _reserve" not in reserves:
            residuals.append(column[-2])
        elif column[1] == 'forceset':
            muscles.append(column[-2])
    return np.unique(muscles),\
           np.unique(reserves),\
           np.unique(residuals)


if __name__ == '__main__':
    # Parse command line arguments
    args = parser.parse_args()

    # Load forces
    states = loadSto('%s_states.sto' % args.prefix)
    forces = loadSto("%s_Actuation_force.sto" % args.prefix)
    muscles, reserves, residuals = (getForceKeys(states, forces))

    # Get reserve actuator columns
    print("MAX Residual Force (N)")
    print('\t'.join(residuals))
    for idx, reserve in enumerate(reserves):
        print((forces[residuals]**2).mean()**0.5, end='\t' if idx + 1 < len(reserves) else '\n')

    print("RMS Residual Force (N)")
    print('\t'.join(residuals))
    for idx, residual in enumerate(residuals):
        print((forces[residual] ** 2).mean() ** 0.5, end='\t' if idx + 1 < len(residuals) else '\n')

    print("MAX Reserve (Nm)")
    print('\t'.join(reserves))
    for idx, reserve in enumerate(reserves):
        print(forces[reserve].max(), end='\t' if idx+1 < len(reserves) else '\n')

    print("RMS Reserve (Nm)")
    print('\t'.join(reserves))
    for idx, reserve in enumerate(reserves):
        print((forces[reserve]**2).mean()**0.5, end='\t' if idx + 1 < len(reserves) else '\n')
