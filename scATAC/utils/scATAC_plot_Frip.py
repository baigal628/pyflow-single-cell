#!/usr/bin/env python


"""scATAC_plot_Frip.py: get quality control metric Frip score (Fraction of reads in promoter) from fragment.tsv file 
and plot a scatter plot with x-axis is log10 total reads and y-axis is the Frip and highlight the cells pass
the total reads cutoff and Frip cutoff.
"""

# template from Michale Hoffman https://gist.github.com/crazyhottommy/7c5da0050e5786cb0d4e0b21c00accdb

__version__ = "0.1"

from argparse import Namespace
from os import EX_OK
import os
import sys
from typing import List, Optional
from MAESTRO.scATAC_utility import RSCRIPT_PATH

def parse_args(args: List[str]) -> Namespace:
    from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser

    description = __doc__.splitlines()[0].partition(": ")[2]
    parser = ArgumentParser(description=description,
                            formatter_class=ArgumentDefaultsHelpFormatter)

    version = f"%(prog)s {__version__}"
    parser.add_argument("--version", action="version", version=version)
    parser.add_argument("-F","--frag", dest = "fragfile", default = "",help = "The fragment file generated by 10X CellRanger ATAC, "
        "with barcodes and counts.")
    parser.add_argument("-P","--promoter", dest = "promoterBed", default = "",help = "The 3 column or 6 column Bed file for the promoters")
    parser.add_argument("-CC","--countcutoff", default = 1000, help = "Cutoff for the number of count in each cell")
    parser.add_argument("-FC","--fripcutoff", default = 0.2, help = "Cutoff for fraction of reads in promoter in each cell")
    parser.add_argument("-PF", "--prefix", dest = "prefix", default = "", help = "prefix of the output files.")
    parser.add_argument("-O", "--outdir", dest = "outdir", default = ".", help = "The output directory.")
    if len(args)==0:
        parser.print_help(sys.stderr)
        sys.exit(1)
    else:
        return parser.parse_args(args)


def main(argv: List[str] = sys.argv[1:]):
    args = parse_args(argv)

    # how many reads are mapped in each cell
    cmd1 = "sort -k4,4 -V {fragfile} | \
    bedtools groupby -i - -g 4 -c 5 -o sum > singlecell_mapped.txt".format(fragfile = args.fragfile)

    # how many reads are mapped to promoters in each cell
    cmd2 = "bedtools intersect -wa -a {fragfile} -b {promoter} -u | sort -k4,4 -V | \
    bedtools groupby -i - -g 4 -c 5 -o sum > singlecell_promoter.txt".format(fragfile = args.fragfile, promoter = args.promoterBed)

    # join the two files 
    cmd3 = "sort -k1,1 singlecell_mapped.txt > singlecell_mapped_sorted.txt; \
    sort -k1,1 singlecell_promoter.txt > singlecell_promoter.sorted.txt; \
    join --nocheck-order -t $'\t' -a1 -e'0' -o'1.1 1.2 2.2' -1 1 -2 1 \
    singlecell_mapped_sorted.txt singlecell_promoter.sorted.txt > singlecell.txt"

    # make figures
    cmd4 = "Rscript scATACseq_qc.R --singlestat singlecell.txt \
        --countcutoff {countcutoff} --fripcutoff {fripcutoff} --prefix {prefix} --outdir {outdir}". \
        format(countcutoff = args.countcutoff, fripcutoff = args.fripcutoff, prefix = args.prefix, outdir = args.outdir)
    os.system(cmd1)
    os.system(cmd2)
    os.system(cmd3)
    os.system(cmd4)
    return None

if __name__ == "__main__":
    sys.exit(main())



