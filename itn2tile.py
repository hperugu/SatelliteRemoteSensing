
from glob import glob
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from pyproj import Proj
import os
os.environ['DISPLAY'] = ':1000.0'
import sys

# CONSTANTS
EXT = 'png'
# DATA FILES
INPUT_DIR = 'input/'
OUTPUT_DIR = 'output/'
PICKLE_DIR = INPUT_DIR + 'pickles/'
COABDIS_SHAPES = INPUT_DIR + 'coabdis_gai_oc1_oc2_latlon_20140924/coabdis_gai_oc1_oc2_latlon_20140924'


class ItnFile(object):

    COLOR_SCHEME = ['#777777', '#4C4CFF', '#9999FF', '#E5E5FF',  # gray to light blue
                    '#FF9999', '#FF4C4C', '#FF0000']             # pink to red
    BOUNDS = [1e-9, 1e-5, 1e-3, 0.01, 0.1, 0.5, 1.0]

    def __init__(self, basemap, itn_type='dat'):
        self.basemap = basemap
        self.plcc = Proj(proj='lcc', lat_1=30.0, lat_2=60, lat_0=37, lon_0=-120.5,
                         rsphere=6370000.00, ellps='WGS84')
        self.itn_type = itn_type
        self.link_x = {}
        self.link_y = {}
        self.link_colors = {}
        self.taz_x = {}
        self.taz_y = {}
        self.taz_colors = {}

    def load_file(fin):
        ''' Load an ITN file, based on the ITN version. '''
        if self.itn_type == 'dat':
            self.load_dtim_file(fin)
        else:
            print('ERROR: file type unknown: ' + self.itn_type)
            exit()

    def load_dtim_file(self, fin):
        ''' Plot ITN Link file on top of a map of California.
            (and, if possible, plot the associated TAZ file).
        '''
        # find county
        county = (int(fin.split('_')[2]) + 1) / 2

        # read ITN link file
        self.link_x[county] = []
        self.link_y[county] = []
        self.link_colors[county] = []
        nodes = {}
        f = open(fin, 'r')
        for line in f.xreadlines():
            vals = line.strip().split()
            anode_name = int(line[:10])
            anodex = float(int(line[10:20]))
            anodey = float(int(line[20:30]))
            bnode_name = int(line[30:40])
            bnodex = float(int(line[40:50]))
            bnodey = float(int(line[50:60]))
            anodex, anodey = self.plcc(anodex, anodey, inverse=True)
            anodex, anodey = self.basemap(anodex, anodey)
            nodes[anode_name] = (anodex, anodey)
            bnodex, bnodey = self.plcc(bnodex, bnodey, inverse=True)
            bnodex, bnodey = self.basemap(bnodex, bnodey)
            nodes[bnode_name] = (bnodex, bnodey)
            volume = sum([float(v) for v in slices(line[80:].rstrip(), 11, 26)])
            if volume <= 0.0:
                continue
            self.link_x[county].append([anodex, bnodex])
            self.link_y[county].append([anodey, bnodey])
            self.link_colors[county].append(volume)
        f.close()

        # try to read ITN TAZ file
        link_index = fin.rfind('link')
        taz_path = fin[:link_index] + 'taz' + fin[link_index + 4:]
        taz_exists = False
        if os.path.exists(taz_path):
            taz_exists = True

            self.taz_x[county] = []
            self.taz_y[county] = []
            self.taz_colors[county] = []

            f2 = open(taz_path, 'r')
            for line in f2.xreadlines():
                node = int(line[:10].strip())
                value = sum([float(v) for v in slices(line[40:].rstrip(), 11, 78)])
                if value == 0.0:
                    continue
                node_x, node_y = nodes[node]
                self.taz_x[county].append(node_x)
                self.taz_y[county].append(node_y)
                self.taz_colors[county].append(value)
            f2.close()

    def plot(self, fin, dpi=300, fig_size=(7, 3)):
        ''' Plot ITN Link file(s) on a map of California.
            (and, if possible, plot the associated TAZ file).
        '''
        # setup a plot
        fig = plt.figure(figsize=fig_size)
        outname = "_".join(os.path.basename(fin).split(".")[:-1]).replace(' ', '_')
        index = outname.rfind('link_')
        if len(self.link_x) > 1:
            outname = outname[:index] + outname[index + 9:]
        else:
            outname = outname[:index] + outname[index + 5:]
        plt.figtext(0.75, 0.02, "gray & blue are fine, pink and red are hotspots", size="xx-small")

        # set colors for link file
        link_total = sum([sum(cs) for cs in self.link_colors.itervalues()])
        for c in self.link_colors:
            for i in xrange(len(self.link_colors[c])):
                self.link_colors[c][i] /= link_total

        print('Creating plot...')
        # add link data to plot
        if self.taz_x:
            ax = fig.add_subplot(121)
        else:
            ax = fig.add_subplot(111)
        # plot each link separately
        for county in self.link_x:
            for i in xrange(len(self.link_colors[county])):
                # pick a color for the link
                k = 0
                for j in xrange(1, len(self.BOUNDS)):
                    if self.link_colors[county][i] > self.BOUNDS[j]:
                        k = j
                    else:
                        break
                color1 = self.COLOR_SCHEME[k]
                alpha = 0.1
                if self.link_colors[county][i] > 0.1:
                    alpha = 1.0

                # finally, plot the link
                self.basemap.plot(self.link_x[county][i], self.link_y[county][i], color1,
                                  linewidth=1, alpha=alpha)
        self.basemap.readshapefile(COABDIS_SHAPES, 'GAI')
        plt.title('ITN link file volumes', fontsize=5)

        # add taz data to plot
        if self.taz_x:
            # set colors for taz file
            taz_total = sum([sum(cs) for cs in self.taz_colors.itervalues()])
            for c in self.taz_colors:
                for i in xrange(len(self.taz_colors[c])):
                    self.taz_colors[c][i] /= taz_total

            for c in self.taz_colors:
                for i in xrange(len(self.taz_colors[c])):
                    # pick a color for the link
                    k = 0
                    for j in xrange(1, len(self.BOUNDS)):
                        if self.taz_colors[c][i] > self.BOUNDS[j]:
                            k = j
                        else:
                            break
                    self.taz_colors[c][i] = self.COLOR_SCHEME[k]

            # pull together data for all counties (if there are more than one)
            all_tax_x = []
            all_taz_y = []
            all_taz_colors = []
            for c in self.taz_x:
                all_tax_x += self.taz_x[c]
                all_taz_y += self.taz_y[c]
                all_taz_colors += self.taz_colors[c]
            # add TAZ sub-plot scatter-plot
            ax = fig.add_subplot(122)
            self.basemap.scatter(all_tax_x, all_taz_y, c=all_taz_colors, s=1, edgecolors='none')
            self.basemap.readshapefile(COABDIS_SHAPES, 'GAI')
            plt.title('ITN taz file activity', fontsize=9)

        # set up the plot-wide attributes and save the file
        fig.savefig(OUTPUT_DIR + outname + "." + EXT,
                    format=EXT.upper(),
                    bbox_inches='tight',  # TODO: Test if we need this. Ideally, we remove it.
                    dpi=dpi)
        fig.clf()

        # reset all of the link & TAZ data
        self.link_x = {}
        self.link_y = {}
        self.link_colors = {}
        self.taz_x = {}
        self.taz_y = {}
        self.taz_colors = {}


def slices(s, width, number):
    position = 0
    args = [width]*number
    for length in args:
        yield s[position:position + length]
        position += length


def usage():
    print('\nPurpose:\n\nCreate tile plots from ITN road network files.')
    print('This script is only optimized for data plotted within CA.\n')
    print('Usage:\n\npython itn2tile.py -[county|dir|b|c] /path/2/files')
    print('(e.g.) python itn2tile.py -dir /share/tornado/aa/emis/onroad/itn/s2012v1/\n')
    print('(e.g.) python itn2tile.py -1county s2012v1/003/dtim_link_003_tuth_17.dat\n')
    print('Flags:\n\n-dtimdir\tCreate one plot for the ITN of the whole state (DEFAULT)')
    print('-1county\tCreate plots of ITN link files, separately by county')
    print('-h\tShow help menu.')
    print('-x\tCreate high res plots (WARNING: VERY SLOW).')
    print('\tTitle Text')
    print('-c:Your_Custom_Title_Text')
    print('\tAdd custom title text to your plots (no spaces).\n')
    print('\tBounding Box')
    print('-b:33.3,-118.2,34.0,-117.3')
    print('\tPlot using a new bounding box (say, to plot just LA county).\n')
    exit()


def main():
    # Normal Quality Images (fast to produce)
    dpi = 300
    quality = 'c'
    itn_type = 'dat'

    # Bounding Box for plots
    lllat, lllon, urlat, urlon = (32.25, -124.55, 42.0, -113.0)  # Full California
    # lllat, lllon, urlat, urlon = (33.3, -118.2, 34.0, -117.3)  # Orange County
    # lllat, lllon, urlat, urlon = (33.6, -119.0, 34.9, -117.5)  # LA County
    # lllat, lllon, urlat, urlon = (33.6, -119.5, 35.1, -117.5)  # Ventura County

    # parse command line for flags and input NetCDF files
    run_type = '-dir'
    a = 1
    files = []
    title_txt = ''

    # parse commandline flags
    while(a < len(sys.argv)):
        if sys.argv[a][0] == '-':
            if sys.argv[a] in ['-1county']:
                run_type = sys.argv[a]
            elif sys.argv[a] in ['-dir']:
                run_type = sys.argv[a]
            elif sys.argv[a] == '-x':
                # High Quality Images (very slow to produce)
                dpi = 600
                quality = 'f'
            elif sys.argv[a][1] == 'c':
                title_txt = sys.argv[a][3:]
            elif sys.argv[a][1] == 'b':
                lllat,lllon,urlat,urlon = [float(n) for n in sys.argv[a][3:].split(',')]
            else:
                usage()
        else:
            # all non-flags are presumed to be files (or master ITN directory)
            files.append(sys.argv[a])
        a += 1

    # verify the user gave reasonable input
    if a <= 1:
        usage()
    elif len(files) < 1:
        raise UnboundLocalError('No input files found.')

    # if running for the whole state, find the relevant files
    if run_type == '-dir':
        if itn_type == 'dat':
            files = glob(os.path.join(files[0], '*', 'dtim_link_*_tuth_17.dat'))

    # initiate a map (MM5 Sphere LCC projection)
    basemap = Basemap(llcrnrlat=lllat, llcrnrlon=lllon, urcrnrlat=urlat, urcrnrlon=urlon,
                      projection='lcc', lat_1=30.0, lat_2=60, lat_0=37, lon_0=-120.5,
                      rsphere=6370000.00, resolution=quality)

    # loop through input files and create outputs
    sf = ItnFile(basemap, itn_type)
    files = sorted(files)
    for fin in files:
        print('Processing: ' + str(os.path.basename(fin)))

        # optional outputs, defined by the user
        sf.load_dtim_file(fin)
        if run_type == '-1county':
            sf.plot(fin, dpi)

    if run_type != '-1county':
        sf.plot(fin, dpi)


if __name__ == "__main__":
    main()
