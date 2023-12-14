import tkinter
from tkinter import filedialog
import csv


# import time

def get_file(title, open):
    root = tkinter.Tk()
    root.withdraw()
    if open:
        filename = filedialog.askopenfilename(parent=root, initialdir="/",
                                          title=title)
    else:
        filename = filedialog.asksaveasfile(filetypes = [("tsv file", ".tsv")],defaultextension=".tsv").name
    return filename


def convert():
    print("Please select the .tsv file containing the data to process.")
    filename = ""
    while len(filename) == 0:
        filename = get_file('Please select your .tsv file to process', True)
    print("Please select the file for output.")
    out_filename = ""
    while len(out_filename) == 0:
        out_filename = get_file('Please select the output file', False)
    data = []
    # st = time.time()
    print("Reading file.")
    with open(filename) as file:
        headers = file.readline().strip().split("\t")
        for line in file:
            data.append(line.strip().split("\t"))

    # print(f"Reading file takes: {time.time() - st} seconds")
    # st = time.time()

    pcmz_index = headers.index("PrecursorMz")
    prod_index = headers.index("ProductMz")
    prec_ion_index = headers.index("PrecursorIonMobility")
    prec_charge_index = headers.index("PrecursorCharge")
    frag_type_index = headers.index("FragmentType")
    frag_charge_index = headers.index("FragmentCharge")
    frag_series_index = headers.index("FragmentSeriesNumber")
    pep_seq_index = headers.index("PeptideSequence")
    rt_index = headers.index("NormalizedRetentionTime")

    print("Accessing data.")
    obj_list = {}
    for line in data:
        pcmz = line[pcmz_index]
        obj = get_obj(obj_list, pcmz)
        if not obj:
            obj = DataObject(pcmz)
            obj_list[pcmz] = obj

        product = line[prod_index]
        frag_type = line[frag_type_index]
        frag_charge = line[frag_charge_index]
        frag_series = line[frag_series_index]
        precursor = line[prec_ion_index]
        rt = float(line[rt_index])
        if int(frag_charge) == 1:
            combined = f"{product}:{precursor}:{frag_type}{frag_series}"
        else:
            combined = f"{product}:{precursor}:{frag_type}{frag_series}[{frag_charge}+]"
        obj.add_peaks_list(combined)
        obj.set_z(line[prec_charge_index])
        obj.set_activation("high energy CID (y and b ions)")
        obj.set_sequence(line[pep_seq_index])
        obj.add_peaks_count()
        obj.set_rt(rt)

    # print(f"Accessing data takes: {time.time() - st} seconds")
    # st = time.time()

    print("Consolidating peaks.")
    for obj in obj_list.keys():
        obj_list[obj].consolidate_peaks_list()

    # print(f"Consolidating peaks takes: {time.time() - st} seconds")
    # st = time.time()

    print("Writing output.")
    try:
        with open(out_filename, 'w', newline='\n') as tsvfile:
            writer = csv.writer(tsvfile, delimiter='\t', lineterminator='\n')

            writer.writerow(["m/z", "z", "rt (seconds)", "Activation Mode", "Sequence (backbone)",
                             "Modifications", "Peaks Count", "Peaks List", "Engine"])
            for obj in sorted(obj_list.keys()):
                obj = obj_list[obj]
                writer.writerow([obj.mz, obj.z, obj.rt, obj.activation, obj.sequence, obj.modifications,
                                 obj.peaks_count, obj.peaks_list, obj.engine])
    except PermissionError:
        print("Is your file open in a different location? Please press a key and try again.")
        input()
    # print(f"Writing output takes: {time.time() - st} seconds")
    print("Done. Please press a key to exit, or close the window.")
    input()
    return


def get_obj(obj_list, mz_val):
    if mz_val in obj_list.keys():
        return obj_list[mz_val]
    return False


class DataObject:
    def __init__(self, mz):
        self.mz = mz
        self.z = None
        self.rt = None
        self.activation = None
        self.sequence = None
        self.modifications = ""
        self.peaks_count = 0
        self.peaks_list = []
        self.engine = "DB_SEARCH"

    def set_z(self, z):                     self.z = z

    def set_rt(self, rt):                   self.rt = rt

    def set_activation(self, activation):   self.activation = activation

    def set_sequence(self, seq):            self.sequence = seq

    def add_peaks_count(self):              self.peaks_count += 1

    def add_peaks_list(self, pl):           self.peaks_list.append(pl)

    def consolidate_peaks_list(self):
        peak_str = ""
        for peak in sorted(self.peaks_list):
            peak_str += peak
            peak_str += ";"
        peak_str = peak_str[:-1]
        self.peaks_list = peak_str


if __name__ == '__main__':
    convert()
