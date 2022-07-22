"""Generate structures for calculating the PES.

The program will read the surface structure from an XYZ file and place the
given atom at different distances from the surface.
A separate XYZ file will be created for each distance.

Notes
-----
The following assumptions are made:

- The surface is aligned with the xy plane and, hence, the distance
corresponds to the z coordinate of the atom.

- The z coordinate origin (z=0) is the mean of the z coordinates of the atoms
in the surface model.
"""

import argparse
import os
import sys

import numpy as np

class ArgumentParser(argparse.ArgumentParser):
    """Added comment line support for arguments passed via input file."""

    def convert_arg_line_to_args(self, line):
        if len(line.strip()) == 0 or line.strip()[0] == '#':
            pass
        else:
            yield line


def get_cmdline_args():
    """Read input data from passed via command line."""

    description = [
            'Create structures for calculating the PES.',
            '\n',
            ('Given an input surface model, generate xyz files with an atom'
             ' placed at different distances from the surface.'),
            ('It is assumed that the surface structure is aligned with the xy'
             ' plane.'),
            ('Additionaly, the distance is calculated with respect to the'
             ' mean of the z coordinates of the surface atoms.'),
            ]

    parser = ArgumentParser(
            description='\n'.join(description),
            formatter_class=argparse.RawDescriptionHelpFormatter,
            fromfile_prefix_chars='@',
            )

    parser.add_argument('-i', '--inpxyz', dest='inpxyz',
                        metavar='<filename>', type=str, nargs='?',
                        required=True,
                        help=('xyz file containing the surface structure.'
                              ' It is assumed that the surface is aligned'
                              ' with the xy plane.'))

    parser.add_argument('-o', '--outname', dest='outname',
                        metavar='<basename>', type=str, nargs='?',
                        required=True,
                        help=('basename for output xyz files.'
                              ' For each distance, a numerical suffix will'
                              ' be appended, followed by the `xyz` extension'
                              ' (e.g.: `<basename>_001.xyz`).'))
    
    parser.add_argument('-dmin', dest='d_min', metavar='<distance>',
                        type=float, nargs='?', required=True,
                        help=('Minimum distance between the surface and the atom.'))
    
    parser.add_argument('-dmax', dest='d_max', metavar='<distance>',
                        type=float, nargs='?', required=True,
                        help=('Maximum distance between the surface and the atom.'))
    
    parser.add_argument('-dstep', dest='d_step', metavar='<distance>',
                        type=float, nargs='?', required=True,
                        help=('Step between consecutive distances.'))

    parser.add_argument('-atom', dest='atom_symb', metavar='<symbol>',
                        type=str, nargs='?', required=False, default='H',
                        help=('Atom to be placed (default="H").'))

    parser.add_argument('-x', dest='xcoord', metavar='<coord>', type=float,
                        nargs='?', required=False, default=0,
                        help=('Set x coordinate for the atom (default=0)'))

    parser.add_argument('-y', dest='ycoord', metavar='<coord>', type=float,
                        nargs='?', required=False, default=0,
                        help=('Set y coordinate for the atom (default=0)'))

    return parser.parse_args()

def main():
    """Main execution routine."""

    cmd_line_args = get_cmdline_args()

    # Get list of distances (z coords.)
    zvalues = np.arange(cmd_line_args.d_min,
                        cmd_line_args.d_max + cmd_line_args.d_step,
                        cmd_line_args.d_step)

    #################
    # Prepare surface
    #################

    with open(cmd_line_args.inpxyz, 'r') as fp:
        inpxyz_lines = [s.strip() for s in fp.readlines()]

    # Read atomic coordinates
    natoms = int(inpxyz_lines.pop(0).split('#')[0].strip())
    inpxyz_lines.pop(0)  # remove comment line
    atoms = []
    atomcoords = []
    for i, line in enumerate(inpxyz_lines):
        if i+1 > natoms:
            break
        tokens = line.split()
        atoms.append(tokens.pop(0))
        atomcoords.append([float(s) for s in tokens[:3]])

    # Shift structure to z origin
    shift = np.array(atomcoords)[:, -1].mean()
    shftcoords = [(x, y, z-shift) for x, y, z in atomcoords]

    ###################
    # Create structures
    ###################

    xnew = cmd_line_args.xcoord
    ynew = cmd_line_args.ycoord
    newatom = cmd_line_args.atom_symb

    for i, znew in enumerate(zvalues):
        newfile = '{:}_{:04d}.xyz'.format(cmd_line_args.outname, i)

        try:
            os.rename(newfile, newfile+'.BAK')
        except FileNotFoundError:
            pass
        else:
            print('WARNING: File "{f:}" moved to "{f:}.BAK"'.format(f=newfile))

        print('Writing new file for d={:.8f}'.format(znew), end=' ... ')
        with open(newfile, 'w') as fp:
            fp.write('{:>4d}\n'.format(natoms+1))
            fp.write('Atom-surface distance: {:.8f}\n'.format(znew))
            fp.write('{:3s} {:13.8f} {:13.8f} {:13.8f}\n'.format(newatom, xnew, ynew, znew))

            for atom, (x, y, z) in zip(atoms, shftcoords):
                fp.write('{:3s} {:13.8f} {:13.8f} {:13.8f}\n'.format(atom, x, y, z))

        print('done! (New file: {:})'.format(newfile), flush=True)

if __name__ == '__main__':
        main()
