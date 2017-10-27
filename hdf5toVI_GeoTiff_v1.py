#### Import Libraries#############

import os, sys
from os import path, uname, mkdir
from glob import glob
import string, logging, traceback
from time import time

import numpy as np
from  numpy import ma as ma
import scipy as scipy

import matplotlib
import matplotlib.cm as cm
from matplotlib.colors import ListedColormap
from matplotlib.figure import Figure

matplotlib.use('Agg')
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
# This must come *after* the backend is specified.
import matplotlib.pyplot as ppl

import optparse as optparse
from ViirsData import ViirsTrimTable
#import viirs_edr_data

import tables as pytables
from tables import exceptions as pyEx

# every module should have a LOG object
# e.g. LOG.warning('my dog has fleas')
import logging
LOG = logging.getLogger(__file__)

dpi=200
import pdb
##############
### Moderate and Imager resolution trim table arrays. These are 
### bool arrays, and the trim pixels are set to True.
trimObj = ViirsTrimTable()
modTrimMask = trimObj.createModTrimArray(nscans=192,trimType=bool)
onboardTrimMask = trimObj.createOnboardImgTrimArray(nscans=192,trimType=bool)
ongroundTrimMask = trimObj.createOngroundImgTrimArray(nscans=192,trimType=bool)

def get_hdf5_dict(hdf5Path,filePrefix):
    shortNameDict = {}
    hdf5Path = path.abspath(path.expanduser(hdf5Path))
    print "hdf5Path = %s" % (hdf5Path)

    hdf5Dir = path.dirname(hdf5Path)
    hdf5Glob = path.basename(hdf5Path)

    print "hdf5Dir = %s" % (hdf5Dir)
    print "hdf5Glob = %s" % (hdf5Glob)

    if (hdf5Glob == '' or hdf5Glob == '*'):
        print "prefix = %s" % (filePrefix)
        hdf5Glob = path.join(hdf5Dir,'%s_*.h5'%(filePrefix))
    else :
        hdf5Glob = path.join(hdf5Dir,'%s'%(hdf5Glob))
    print "Final hdf5Glob = %s" % (hdf5Glob)
     hdf5Files = glob(hdf5Glob)
    if hdf5Files != []:
        hdf5Files.sort()
        granIdDict = {}
        for files in hdf5Files :

            #open the hdf5 file
            fileObj = pytables.open_file(files)

            # Get a "pointer" to the granules attribute group.
            VIIRS_VI_EDR_Gran_0 = fileObj.get_node('/Data_Products/VIIRS-VI-EDR/VIIRS-VI-EDR_Gran_0')

            # Retrieve a few attributes
            granID =  getattr(VIIRS_VI_EDR_Gran_0.attrs,'N_Granule_ID')[0][0]
            print 'N_Granule_ID = %s' % (granID)

            dayNightFlag =  getattr(VIIRS_VI_EDR_Gran_0.attrs,'N_Day_Night_Flag')[0][0]
            print 'N_Day_Night_Flag = %s' % (dayNightFlag)

            shortName = fileObj.get_node_attr('/Data_Products/VIIRS-VI-EDR','N_Collection_Short_Name')[0][0]
            print 'N_Collection_Short_Name = %s' % (shortName)

            # Strip the path from the filename
            hdf5File = path.basename(files)

            # Add the granule information to the dictionary, keyed with the granule ID...
            granIdDict[granID] = [hdf5File,fileObj]

        shortNameDict[shortName] = granIdDict

    return shortNameDict

class VIclass():

    def __init__(self,hdf5Dir):

        self.hdf5Dir = hdf5Dir

        self.collShortNames = [
                               'VIIRS-VI-EDR',
                              ]

        self.plotDescr = {}
        self.plotDescr['VIIRS-VI-EDR'] = ['Top of Atmosphere NDVI','Top of Canopy EVI']

        self.plotLims = {}
        self.plotLims['VIIRS-VI-EDR'] = [None,None]

        self.dataName = {}
               self.dataName['VIIRS-VI-EDR'] = ['/All_Data/VIIRS-VI-EDR_All/TOA_NDVI',
                '/All_Data/VIIRS-VI-EDR_All/TOC_EVI']

        self.dataFactors = {}
        self.dataFactors['VIIRS-VI-EDR'] = ['/All_Data/VIIRS-VI-EDR_All/TOA_NDVI_Factors',
                '/All_Data/VIIRS-VI-EDR_All/TOC_EVI_Factors']

        self.hdf5_dict = get_hdf5_dict(hdf5Dir,'VIVIO')
    def plot_VI_granules(self,plotProd='EDR',vmin=None,vmax=None,pngDir=None,
            pngPrefix=None,annotation='',dpi=300):

        if pngDir is None :
            pngDir = path.abspath(path.curdir)

        plotDescr = self.plotDescr
        plotLims = self.plotLims

        hdf5_dict = self.hdf5_dict
        collShortNames = hdf5_dict.keys()

        print 'collShortNames = %r' % (collShortNames)

        for shortName in collShortNames :

            print 'shortName = %s' % (shortName)

            if (plotProd == 'EDR'):

                dataNames = self.dataName[shortName]
                factorsNames = self.dataFactors[shortName]
                plotDescrs = plotDescr[shortName]
                prodNames = ['NDVI','EVI']

            elif (plotProd == 'NDVI'):

                dataNames = [self.dataName[shortName][0]]
                factorsNames = [self.dataFactors[shortName][0]]
                plotDescrs = [plotDescr[shortName][0]]
                prodNames = ['NDVI']

            elif (plotProd == 'EVI'):

                dataNames = [self.dataName[shortName][1]]
                factorsNames = [self.dataFactors[shortName][1]]
                plotDescrs = [plotDescr[shortName][1]]
                prodNames = ['EVI']

            granID_list =  hdf5_dict[shortName].keys()
            granID_list.sort()

            for granID in granID_list :

                print '%s --> %s ' % (shortName, granID)

                hdf5Obj = hdf5_dict[shortName][granID][1]

                VIIRS_VI_EDR_Gran_0 = hdf5Obj.get_node('/Data_Products/VIIRS-VI-EDR/VIIRS-VI-EDR_Gran_0')
                dayNightFlag =  getattr(VIIRS_VI_EDR_Gran_0.attrs,'N_Day_Night_Flag')[0][0]
                                print '%s --> %s ' % (shortName, granID)

                hdf5Obj = hdf5_dict[shortName][granID][1]

                VIIRS_VI_EDR_Gran_0 = hdf5Obj.get_node('/Data_Products/VIIRS-VI-EDR/VIIRS-VI-EDR_Gran_0')
                dayNightFlag =  getattr(VIIRS_VI_EDR_Gran_0.attrs,'N_Day_Night_Flag')[0][0]
                print 'N_Day_Night_Flag = %s' % (dayNightFlag)
                orient = -1 if dayNightFlag == 'Day' else 1

                for dataName,factorsName,plotDescr,prodName in zip(dataNames,factorsNames,plotDescrs,prodNames):

                    data = hdf5Obj.get_node(dataName)[:,:]
                    print "Int data = {}".format(data[:16,:10])
                    factors = hdf5Obj.get_node(factorsName)[:]
                    data = data * factors[0] + factors[1]

                    print "float data = {}".format(data[:16,:10])
                    print "factors = {}".format(factors)
                    pdb.set_trace()
                    VIqualFlag = hdf5Obj.get_node('/All_Data/VIIRS-VI-EDR_All/QF1_VIIRSVIEDR')
                    VIqualFlag = np.bitwise_and(VIqualFlag,1) >> 0 # NDVI quality
                    #VIqualFlag = np.bitwise_and(VIqualFlag,2) >> 1 # EVI quality
                    VIqualFlagMask = ma.masked_equal(VIqualFlag,0).mask

                    # What value are the bowtie deletion pixels
                    ongroundPixelTrimValue = trimObj.sdrTypeFill['ONGROUND_PT_FILL'][data.dtype.name]
                   print "Onground Pixel Trim value is {}".format(ongroundPixelTrimValue)
                    onboardPixelTrimValue = trimObj.sdrTypeFill['ONBOARD_PT_FILL'][data.dtype.name]
                    print "Onboard Pixel Trim value is {}".format(onboardPixelTrimValue)

                    # Apply the On-board pixel trim
                    data = ma.array(data,mask=onboardTrimMask,fill_value=ongroundPixelTrimValue)
                    data = data.filled() # Substitute for the masked values with ongroundPixelTrimValue

                    ## Apply the On-board pixel trim
                    data = ma.array(data,mask=ongroundTrimMask,fill_value=onboardPixelTrimValue)
                    data = data.filled() # Substitute for the masked values with onboardPixelTrimValue

                    plotTitle = '%s : %s %s' % (shortName,granID,annotation)
                    cbTitle = plotDescr

                    # Create figure with default size, and create canvas to draw on
                    scale=1.5
                    fig = Figure(figsize=(scale*8,scale*3))
                    canvas = FigureCanvas(fig)

                    # Create main axes instance, leaving room for colorbar at bottom,
                    # and also get the Bbox of the axes instance
                    ax_rect = [0.05, 0.18, 0.9, 0.75  ] # [left,bottom,width,height]
                    ax = fig.add_axes(ax_rect)

                    # Granule axis title
                    ax_title = ppl.setp(ax,title=plotTitle)
                    ppl.setp(ax_title,fontsize=12)
                    ppl.setp(ax_title,family="sans-serif")

                    # Plot the data
                    print "%s is of kind %r" % (shortName,data.dtype.kind)
                    if (data.dtype.kind =='i' or data.dtype.kind =='u'):
                        fill_mask = ma.masked_greater(data,200).mask
                    else:
                        fill_mask = ma.masked_less(data,-800.).mask

                    # Construct the total mask
                    #totalMask = VIqualFlagMask + fill_mask
                    totalMask = fill_mask
                   # Mask the aerosol so we only have the retrievals
                    data = ma.masked_array(data,mask=totalMask)

                    im = ax.imshow(data[::orient,::orient],interpolation='nearest',vmin=vmin,vmax=vmax)

                    ppl.setp(ax.get_xticklabels(),visible=False)
                    ppl.setp(ax.get_yticklabels(),visible=False)
                    ppl.setp(ax.get_xticklines(),visible=False)
                    ppl.setp(ax.get_yticklines(),visible=False)

                    # add a colorbar axis
                    cax_rect = [0.05 , 0.05, 0.9 , 0.10 ] # [left,bottom,width,height]
                    cax = fig.add_axes(cax_rect,frameon=False) # setup colorbar axes

                    # Plot the colorbar.
                    cb = fig.colorbar(im, cax=cax, orientation='horizontal')
                    ppl.setp(cax.get_xticklabels(),fontsize=9)
                    ppl.setp(cax.get_xticklines(),visible=True)

                    # Colourbar title
                    cax_title = ppl.setp(cax,title=cbTitle)
                    ppl.setp(cax_title,fontsize=10)

                    # Turn off the tickmarks on the colourbar
                    #ppl.setp(cb.ax.get_xticklines(),visible=False)
                    #ppl.setp(cb.ax.get_xticklabels(),fontsize=9)

                    # Redraw the figure
                    canvas.draw()

                    # Save the figure to a png file...
                    pngFile = path.join(pngDir,'%s%s_%s_%s.png' % (pngPrefix,shortName,granID,prodName))
                    canvas.print_figure(pngFile,dpi=dpi)
                    print "Writing to %s..." % (pngFile)

                    ppl.close('all')
                    sys.exit(0)

                hdf5Obj.close()
def main():

    prodChoices=['EDR','QF','NDVI','EVI','QF1','QF2','QF3']

    description = \
    '''
    This is a brief description of %prog
    '''
    usage = "usage: %prog [mandatory args] [options]"
    version = version="%prog"
    parser = optparse.OptionParser(description=description,usage=usage,version=version)
       # Mandatory arguments
    mandatoryGroup = optparse.OptionGroup(parser, "Mandatory Arguments",
                        "At a minimum these arguments must be specified")

    mandatoryGroup.add_option('-i','--input_files',
                      action="store",
                      dest="hdf5Files" ,
                      type="string",
                      help="The fully qualified path to the input VIVIO HDF5 files. May be a directory or a file glob.")

    parser.add_option_group(mandatoryGroup)

    # Optional arguments
    optionalGroup = optparse.OptionGroup(parser, "Extra Options",
                        "These options may be used to customize plot characteristics.")

    optionalGroup.add_option('--pass',
                      action="store_true",
                      dest="plotPass",
                      help="Concatenate the granules")
    optionalGroup.add_option('--plotMin',
                      action="store",
                      type="float",
                      dest="plotMin",
                      help="Minimum value to plot.")
    optionalGroup.add_option('--plotMax',
                      action="store",
                      type="float",
                      dest="plotMax",
                      help="Maximum value to plot.")
    optionalGroup.add_option('-d','--dpi',
                      action="store",
                      dest="dpi",
                      default='200.',
                      type="float",
                      help="The resolution in dots per inch of the output png file. [default: %default]")
    optionalGroup.add_option('-a','--map_annotation',
                      action="store",
                      dest="mapAnn",
                      #default='',
                      type="string",
                      help="The map legend describing the dataset being shown. [default: IPPROD]")
    optionalGroup.add_option('-p','--product',
                      action="store",
                      dest="plotProduct",
                      type="choice",
                      choices=prodChoices,
                      help='''The VIIRS VI EDR or QF datasets to plot.\n\n
                           Possible values are...
                           %s
                           ''' % (prodChoices.__str__()[1:-1]))
    optionalGroup.add_option('--png_dir',
                      action="store",
                      dest="pngDir" ,
                      type="string",
                      help="The directory where png files will be written.")
    optionalGroup.add_option('-o','--output_file_prefix',
                                                                          default="",
                      type="string",
                      help="""String to prefix to the automatically generated 
                      png names, which are of the form 
                      <N_Collection_Short_Name>_<N_Granule_ID>_<dset>.png. 
                      [default: %default]""")
    optionalGroup.add_option('-v', '--verbose',
                      dest='verbosity',
                      action="count",
                      default=2,
                      help="""each occurrence increases verbosity 1 level from 
                      ERROR: -v=WARNING -vv=INFO -vvv=DEBUG""")

    parser.add_option_group(optionalGroup)

    # Parse the arguments from the command line
    (options, args) = parser.parse_args()

    # Set up the logging
    console_logFormat = '%(asctime)s : (%(levelname)s):%(filename)s:%(funcName)s:%(lineno)d:  %(message)s'
    dateFormat = '%Y-%m-%d %H:%M:%S'
    levels = [logging.ERROR, logging.WARN, logging.INFO, logging.DEBUG]
    logging.basicConfig(level = levels[options.verbosity],
            format = console_logFormat,
            datefmt = dateFormat)

    # Check that all of the mandatory options are given. If one or more 
    # are missing, print error message and exit...
    mandatories = ['hdf5Files']
    mand_errors = ["Missing mandatory argument [-i HDF5FILES | --input_files=HDF5FILES]"
                  ]
    isMissingMand = False
    for m,m_err in zip(mandatories,mand_errors):
        if not options.__dict__[m]:
            isMissingMand = True
            print m_err
    if isMissingMand :
        parser.error("Incomplete mandatory arguments, aborting...")

    vmin = options.plotMin
    vmax = options.plotMax

    hdf5Path = path.abspath(path.expanduser(options.hdf5Files))

    print "hdf5Path = %s" % (hdf5Path)
    pngDir = '.' if (options.pngDir is None) else options.pngDir
    pngDir = path.abspath(path.expanduser(pngDir))
    print "pngDir = %s" % (pngDir)
    if not path.isdir(pngDir):
        print "Output image directory %s does not exist, creating..." % (pngDir)
        try:
            mkdir(pngDir,0755)
        except Exception, err :
            print "%s" % (err)
            print "Creating directory %s failed, aborting..." % (pngDir)
            sys.exit(1)
                              pngPrefix = options.outputFilePrefix
    dpi = options.dpi
    plotProduct = options.plotProduct
    plotPass = options.plotPass

    plotEDR = False

    plotQF = False

    if (plotProduct is None):
        plotEDR = True
        plotQF = True
        edrPlotProduct = 'EDR'
        qfPlotProduct = 'QF'
    else :
        if ('EDR' in plotProduct) \
           or ('NDVI' in plotProduct) \
           or ('EVI' in plotProduct) :
            plotEDR = True
            edrPlotProduct = plotProduct

        if ('QF' in plotProduct) :
            plotQF = True
            qfPlotProduct = plotProduct

    if plotEDR :
        try :
            VIobj = VIclass(hdf5Path)
            if plotPass :
                VIobj.plot_VI_pass(plotProd=edrPlotProduct,vmin=vmin,vmax=vmax,pngDir=pngDir,pngPrefix=pngPrefix,dpi=dpi)
            else:
                VIobj.plot_VI_granules(plotProd=edrPlotProduct,vmin=vmin,vmax=vmax,pngDir=pngDir,pngPrefix=pngPrefix,dpi=dpi)

            pytables.file.close_open_files()
        except Exception, err:
            traceback.print_exc(file=sys.stdout)
            pytables.file.close_open_files()

    if plotQF :
        try :
            VIobj = VIclass(hdf5Path)
            if plotPass :
                VIobj.plot_VI_pass_tests(plotProd=qfPlotProduct,pngDir=pngDir,pngPrefix=pngPrefix,dpi=dpi)
            else:
                VIobj.plot_VI_tests(plotProd=qfPlotProduct,pngDir=pngDir,pngPrefix=pngPrefix,dpi=dpi)

            pytables.file.close_open_files()
        except Exception, err:
            traceback.print_exc(file=sys.stdout)
            pytables.file.close_open_files()

              print "Exiting..."
    sys.exit(0)


if __name__ == '__main__':
    main()
                                                                                                                                                                                    447,0-1       98%
                                                                                                                 337,1         70%




