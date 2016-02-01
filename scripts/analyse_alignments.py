
import os
from os.path import basename
import readline
import rpy2
import rpy2.robjects
from collections import OrderedDict, Counter
from rpy2.robjects.packages import importr
import itertools
import argparse


class PEntry:

    input = ""
    aligner = ""
    junctions_in_ref = 0
    junctions_out_ref = 0
    junctions_missing = 0
    junctions_in_ref_perc = 0
    junctions_missing_perc = 0

    def __init__(self):
        self.data = []

    def __str__(self):
        return self.input + "\t" + self.aligner + "\t" + str(self.junctions_in_ref)+ "\t" + format(self.junctions_in_ref_perc, '.2f') \
               + "\t" + str(self.junctions_missing) + "\t" + format(self.junctions_missing_perc, '.2f') + "\t" + str(self.junctions_out_ref)


    def calc_percs(self, nb_in_ref):
        self.junctions_in_ref_perc = (float(self.junctions_in_ref) / float(nb_in_ref)) * 100.0
        self.junctions_missing_perc = (float(self.junctions_missing) / float(nb_in_ref)) * 100.0

    @staticmethod
    def header():
        return "Dataset\tAligner\tInRef\tInRef%\tMissing\tMissing%\tOutRef"

def make_key(line, usestrand, tophat):
    words = line.split()
    overhang = words[10]
    overhang_parts = overhang.split(",")
    lo = int(overhang_parts[0])
    ro = int(overhang_parts[1])
    chr = words[0]
    start = str(int(words[6]) + lo) if tophat else words[6]
    end = str(int(words[7]) - ro) if tophat else words[7]
    strand = words[5]
    key = chr + "_" + start + "_" + end
    if usestrand:
        key += "_" + strand
    return key


def loadbed(filepath, usestrand, tophat) :
    with open(filepath) as f:
        index = 0
        items = set()
        for line in f:
            if index > 0:
                items.add(make_key(line, usestrand, tophat))
            index += 1
    if len(items) != index - 1 :
        print ("non unique items in bed file " + filepath)
    return items

def main():
    
    parser = argparse.ArgumentParser("Script to create the Venn Plots from BED files")
    parser.add_argument("input", help="The directory containing BED files from pipeline")
    parser.add_argument("-r", "--reference", required=True, help="The reference BED file to compare against")
    parser.add_argument("-o", "--output", required=True, help="The output prefix")
    args = parser.parse_args()

    ref_bed = loadbed(args.reference, False, False)
    print ("Loaded Reference BED file.  # junctions: " + str(len(ref_bed)))

    # Load all bed files
    bed_data = {}
    aligners = set()
    reads = set()
    junc_analysers = set()
    for bed_file in os.listdir(args.input):
        if bed_file.endswith(".bed"):
            bed_base = os.path.splitext(bed_file)[0]
            bed_data[bed_base] = loadbed(args.input + "/" + bed_file, False, False)
            parts = bed_base.split('-')
            aligners.add(parts[0])
            reads.add(parts[1])
            junc_analysers.add(parts[2])
            print ("Loaded: " + bed_file + "; # junctions: " + str(len(bed_data[bed_base])))

    print ("Found these aligners: " + ', '.join(aligners))
    print ("Found these reads: " + ', '.join(reads))
    print ("Found these junction analysis tools: " + ', '.join(junc_analysers))


    # Build table
    tab = list()
    for a in aligners:
        for r in reads:
            p = PEntry()
            p.aligner = a
            p.input = r
            p.junctions_in_ref = len(ref_bed & bed_data[a + "-" + r + "-all"])
            p.junctions_out_ref = len(bed_data[a + "-" + r + "-all"] - ref_bed)
            p.junctions_missing = len(ref_bed - bed_data[a + "-" + r + "-all"])
            p.calc_percs(len(ref_bed))

            tab.append(p)

    # Output table to disk
    with open(args.output + "-align_reads.tab", "w") as tab_out:
        print(PEntry.header(), file=tab_out)
        for p in tab:
            print(p, file=tab_out)


    # Create Venns
    cols = rpy2.robjects.vectors.StrVector( ["lightblue", "purple", "green",
                                             "orange", "red"])

    r = rpy2.robjects.r  # Start the R thread
    base = importr("base")
    venn = importr("VennDiagram")
    grdevices = importr("grDevices")


    for r in reads:

        categories = list()
        categories.append("Reference")

        sets = list()
        sets.append(ref_bed)

        nums = dict()
        nums["area1"] = len(ref_bed)
        i=2
        for a in aligners:
            s = bed_data[a + "-" + r + "-all"]
            sets.append(s)
            categories.append(a)
            nums["area{0}".format(i)] = len(s)
            i+=1

        for num_combs in range(2,6):
            for comb in itertools.combinations(range(1,6), num_combs):
                index = "".join([str(x) for x in comb])
                curr_sets = [sets[num-1] for num in comb]
                nums["n{0}".format(index)] = len(set.intersection(*curr_sets))

        grdevices.tiff(args.output + "-" + r + ".venn.tiff", width=960, height=960)
        venn.draw_quintuple_venn(height=5000,
                             width=5000,
                             # This will be in alphabetical order X(
                             fill=cols,
                             category=rpy2.robjects.vectors.StrVector(categories),
                             margin=0.2,
                             cat_dist=rpy2.robjects.vectors.FloatVector([0.25, 0.3, 0.25, 0.25, 0.25]),
                             cat_cex=3,
                             cat_col=rpy2.robjects.vectors.StrVector(["darkblue",
                                                                      "purple",
                                                                      "darkgreen",
                                                                      "darkorange",
                                                                      "darkred"]),
                             cex=1,
                             main="Comparison on junctions found by alignment tools",
                             main_col="black",
                             main_cex=8,
                             sub="" + r + " dataset",
                             sub_col="black",
                             sub_cex=5,
                             **nums)
    grdevices.dev_off()


main()