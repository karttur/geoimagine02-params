'''
Created on 31 Dec 2020

@author: thomasgumbricht
'''

import json

from sys import exit

from os import path

#from pprint import pprint

from ktpandas import PandasTS

from params.layers import VectorLayer, RasterLayer

import support.karttur_dt as mj_dt

def UpdateDict(mainD, defaultD, jsonFPN = False):
    '''
    '''
    
    if len(mainD) == 0:
        
        return defaultD
        
    elif mainD == 'processid' and jsonFPN:
        
        exitstr = 'It seems that the process clause of the json file is not a list\n    %s' %(jsonFPN) 
                
        exit(exitstr)
        
    else: 
        
        d = {key: defaultD.get(key, mainD[key]) for key in mainD}
        
        for key in defaultD:
            
            if key not in d:
            
                mainD[key] = defaultD[key]
        
        return mainD

class Composition:
    '''
    classdocs
    '''
    def __init__(self, compD, parameters, system, division, defPath):
        '''
        '''
        checkL  = ['source','product','content','layerid','prefix','suffix']
  
        for key in compD:
            
            if key in checkL:
                
                if '_' in compD[key]:
                    
                    exitstr = 'the "%s" parameter can not contain underscore (_): %s ' %(key, compD[key])
                    
                    exit(exitstr) 
                    
                if compD[key][0:10] == 'parameter:':
                
                    param = compD[key].split(':')[1]
                    
                    if not hasattr(parameters,param):
                        
                        exitstr = 'EXITING - error in Composition when identifying default parameter'
                    
                    compD[key] =  getattr(parameters, param)
                    
            setattr(self, key, compD[key])

        if not hasattr(self, 'layerid'):
            
            exitstr = 'All compositions must contain a layerid'
            BALLE
            exit(exitstr)
            
        if not hasattr(self, 'content'):
            exitstr = 'All compositions must have a content'
            exit(exitstr)
            
        if not hasattr(self, 'suffix'):
            self.suffix = '0'
        
        if self.suffix == '':
            self.suffix = '0'
            
        self._SetVolume(defPath)
        
        self._SetExtention(defPath)
            
        self._SetCompid()
        
        self._SetSystem(system)
        
        self._SetDivision(division)
    
    def _SetVolume(self, defPath):
        ''' Set the volume for each composition
        '''
        
        if not hasattr(self, 'volume'):
            
            self.volume = defPath.volume 
            
    def _SetExtention(self, defPath):
        ''' Set the volume for each composition
        '''
        
        if not hasattr(self, 'ext'):
            
            self.ext = defPath.hdr
             
        if not self.ext[0] == '.':
        
            self.ext ='.%s' %(self.ext)
            
            
        # Redo tbe same procedure for dat file
        
        if not hasattr(self, 'dat'):
            
            self.dat = defPath.hdr
        
        if len(self.dat) >= 2:
        
            if self.dat[0] == '.':
            
                self.dat = self.dat
            
            else:
            
                self.dat = '.%s' %(self.dat)
                
        
                    
    
    def _SetSystem(self,system):
        '''
        '''
        self.system = system
   
    def _SetDivision(self,division):
        '''
        '''
        self.division = division
        
    def _SetCompid(self):
        '''
        '''
        self.compid = '%(f)s_%(b)s' %{'f':self.content, 'b':self.layerid}
            
            
    def _Update(self, compD):
        '''
        '''
        for key in compD:
            if key in self.checkL:
                if '_' in compD[key]:
                    exitstr = 'the "%s" parameter can npot contain underscore (_): %s ' %(key, compD[key])
                    exit(exitstr) 
            setattr(self, key, compD[key])
    
class Location:
    ''' Set location
    '''
    
    def __init__(self, processid, defregid, system, division, epsg, session): 
        '''
        '''
        
        self.defregid = defregid
        
        self.system = system
        
        self.division = division
        
        self.epsg = epsg
        
        self.locusD = {}
        
        self.locusL = []

        if division in ['NA','none','None','na']:
            
            #No spatial data involved
            pass
        
        elif division == 'region':
            
            self.locusL.append(self.defregid)
            
            self.locusD[self.defregid] = {'locus':self.defregid, 'path':self.defregid}
        
        elif division == 'tiles' and system.lower() == 'modis':
            
            from support.modis import ConvertMODISTilesToStr as convTile
            
            tiles = session._SelectModisRegionTiles({'regionid':self.defregid})
            
            for tile in tiles:
                
                hvD = convTile(tile)
                
                self.locusL.append(hvD['prstr'])
                
                self.locusD[hvD['prstr']] = {'locus':hvD['prstr'], 'path':hvD}
                
        elif division == 'tiles' and system.lower() == 'sentinel' and processid[0:7] in ['downloa', 'explode','extract','geochec','findgra','reorgan']:
            self.locusL.append('unknown')
            self.locusD['unknown'] = {'locus':'unknwon', 'path':'unknown'}
        elif division == 'scenes' and system.lower() == 'landsat' and processid[0:7] in ['downloa', 'explode','extract','geochec','findgra','reorgan']:
            self.locusL.append('unknown')
            self.locusD['unknown'] = {'locus':'unknown', 'path':'unknown'}

        else:
            print ('add division, system', division, system, processid)
            ERRORCHECK
            
class TimeSteps:
    """Sets the time span, seasonality and timestep to process data for.
    """ 
      
    def __init__(self, period, verbose):
        """The constructor expects a string code for periodicty
        Additionally dates for strat and end, seasonality and addons can be given 
        """
        
        self.period = period
        
        self.verbose = verbose
        
        self.datumL = []
        
        self.datumD = {}
        
        if not period or period == None:
            
            # Set to static
            self.SetStaticTimeStep()
            
        elif self.period.timestep == 'static':
            
            # Set to static
            self.SetStaticTimeStep()
            
        elif self.period.timestep == 'singledate':
            
            self.SingleDateTimeStep()
            
        elif self.period.timestep == 'singleyear':
            
            self.SingleYearTimeStep()
            
        elif self.period.timestep == 'staticmonthly':
            
            self.SingleStaticMonthlyStep()
            
        elif self.period.timestep == 'fiveyears':
            
            self.FiveYearStep()
        
        # All timestep data containing periods
        else:
            
            # Get the startdata and enddate of the period
            self.SetStartEndDates()
            
            self.SetSeasonStartEndDates()
            
            if self.period.timestep in ['M','MS','monthly','monthlyday']:
                
                self.MonthlyTimeStep()
                
                self.startdatestr = self.startdatestr[0:6]
                
                self.enddatestr = self.enddatestr[0:6]
                
                self.pandasCode = 'MS'
                
                self.SetMstep()

            elif self.period.timestep == 'varying':
                
                self.Varying()
            
            elif self.period.timestep == 'allscenes':
                
                self.AllScenes()
            
            elif self.period.timestep == 'inperiod':
                
                self.InPeriod()
                
            elif self.period.timestep == 'ignore':
                
                self.Ignore()
                
            elif self.period.timestep[len(self.period.timestep)-1] in ['D', '1D']:
                
                self.SetDstep()
                
            elif self.period.timestep == '8D':
                
                self.SetDstep()
                
            elif self.period.timestep == '16D':
                
                self.SetDstep()
                
            else:
                exitstr = 'Unrecognized timestep in class TimeSteps %s' %(self.period.timestep)
                exit(exitstr)
            
            if self.verbose > 1:
                
                print ('    Timestep set: %s' %(self.period.timestep))
                
    def SetStartEndDates(self):
        ''' Set stardata and end date for period
        '''
        
        self.startdate = mj_dt.IntYYYYMMDDDate(self.period.startyear, 
                                self.period.startmonth, self.period.startday)       
        
        self.enddate = mj_dt.IntYYYYMMDDDate(self.period.endyear, 
                                self.period.endmonth, self.period.endday)  
        
        self.startdatestr = mj_dt.DateToStrDate(self.startdate)
        
        self.enddatestr = mj_dt.DateToStrDate(self.enddate)
        
        if self.enddate < self.startdate:
        
            exitstr = 'period starts after ending'
            
            exit(exitstr)

        
    def SetSeasonStartEndDates(self):
        '''
        '''
        self.startdoy = self.enddoy = 0
        
        if hasattr(self.period, 'seasonstartmonth') and self.period.seasonstartmonth > 0:
            
            if hasattr(self.period, 'seasonstartday') and self.period.seasonstartday > 0:
                               
                seasonstart = mj_dt.IntYYYYMMDDDate(2001, self.period.seasonstartmonth, self.period.seasonstartday )       
            
                self.startdoy = int(mj_dt.YYYYDOYStr(seasonstart))
                
        if hasattr(self.period, 'seasonendmonth') and self.period.seasonendmonth > 0:
            
            if hasattr(self.period, 'seasonendday') and self.period.seasonendday > 0:
                                
                seasonend = mj_dt.IntYYYYMMDDDate(2001, self.periodD.seasonendmonth, self.period.seasonendday)
                      
                self.enddoy = int(mj_dt.YYYYDOYStr(seasonend))
                
        if self.enddoy < self.startdoy:
            
            errorigen
 
    def SetStaticTimeStep(self):
        ''' Set to static
        '''
        self.datumL.append('0')
        
        self.datumD['0'] = {'acqdate':False, 'acqdatestr':'0'}
        
 
        
    def SingleYearTimeStep(self):
        '''
        '''
        if not self.period.startyear == self.period.endyear:
            
            exitstr = 'error in period: year'
            
            exit(exitstr)
            
        acqdatestr = '%(y)d' %{'y':self.period.startyear}
        
        if not len(acqdatestr) == 4 or not acqdatestr.isdigit:
            
            exitstr = 'len(acqdatestr) != 4'
            
            exit(exitstr)
            
        self.datumL.append(acqdatestr)
        
        acqdate = mj_dt.SetYYYY1Jan(int(acqdatestr))

        self.datumD[acqdatestr] = {'acqdate':acqdate, 'acqdatestr':acqdatestr}
    
    def FiveYearStep(self,periodD):
        if not periodD['startyear'] < periodD['endyear'] or periodD['startyear'] < 1000 or periodD['endyear'] > 9999:
            exitstr = "periodD['startyear'] < periodD['endyear'] or periodD['startyear'] < 1000 or periodD['endyear'] > 9999"
            exit(exitstr)
        for y in range(periodD['startyear'],periodD['endyear']+1,5):
            acqdatestr = '%(y)d' %{'y':y}
            if not len(acqdatestr) == 4:
                exitstr = 'len(acqdatestr) != 4'
                exit(exitstr)

            #self.datumL.append({'acqdatestr':acqdatestr, 'timestep':'fiveyears'})

    def SingleStaticMonthlyStep(self,periodD):
        if periodD['endmonth'] < periodD['startmonth'] or periodD['startmonth'] > 12 or periodD['endmonth'] > 12:
            exitstr = "periodD['endmonth'] < periodD['startmonth'] or periodD['startmonth'] > 12 or periodD['endmonth'] > 12"
            exit(exitstr)
        for m in range(periodD['startmonth'],periodD['endmonth']+1):
            if m < 10:
                mstr = '0%(m)d' %{'m':m}
            else:
                mstr = '%(m)d' %{'m':m} 
            ERRORCHECK
            #self.datumL.append({'acqdatestr':mstr, 'timestep':'staticmonthly'})
            
    def MonthlyDayTimeStepOld(self,periodD):
        mstr = self.MonthToStr(periodD['startmonth'])
        yyyymmdd = '%(yyyy)s%(mm)s01' %{'yyyy':periodD['startyear'],'mm':mstr }
        startmonth = mj_dt.yyyymmddDate(yyyymmdd)
        mstr = self.MonthToStr(periodD['endmonth'])
        yyyymmdd = '%(yyyy)s%(mm)s01' %{'yyyy':periodD['endyear'],'mm':mstr }
        endmonth = mj_dt.yyyymmddDate(yyyymmdd)
        acqdatestr = mj_dt.DateToStrDate(startmonth)
        self.datumL.append({'acqdatestr':acqdatestr[0:6], 'timestep':'monthlyday'})
        monthday = startmonth
        while monthday < endmonth:
            monthday = mj_dt.AddMonth(monthday)
            acqdatestr = mj_dt.DateToStrDate(monthday)
            #Only set the month, for ile structure consistency
            pass
            #self.datumL.append({'acqdatestr':acqdatestr[0:6], 'timestep':'monthlyday'})
            
    def MonthlyTimeStep(self,periodD):
        #get start date
        mstr = self.MonthToStr(periodD['startmonth'])
        yyyymmdd = '%(yyyy)s%(mm)s01' %{'yyyy':periodD['startyear'],'mm':mstr }
        startdate = mj_dt.yyyymmddDate(yyyymmdd)

        #get end date
        mstr = self.MonthToStr(periodD['endmonth'])
        yyyymm = '%(yyyy)s%(mm)s' %{'yyyy':periodD['endyear'],'mm':mstr }
        enddate = mj_dt.YYYYMMtoYYYYMMDD(yyyymm,32)

        #yyyymmdd = '%(yyyy)s%(mm)s31' %{'yyyy':periodD['endyear'],'mm':mstr }
        #endmonth = mj_dt.yyyymmddDate(yyyymmdd)
        acqdatestr = mj_dt.DateToStrDate(startdate)
        acqdate = startdate
        self.datumL.append({'acqdate':acqdate, 'acqdatestr':acqdatestr[0:6], 'timestep':'MS'})
        while True:
            acqdate = mj_dt.AddMonth(acqdate,1)
            if acqdate > enddate:
                break
            acqdatestr = mj_dt.DateToStrDate(acqdate)
            self.datumL.append({'acqdate':acqdate, 'acqdatestr':acqdatestr[0:6], 'timestep':'MS'})
        
    def SetDstep(self):
        '''
        '''

        pdTS = PandasTS(self.period.timestep)
        
        
        
        npTS = pdTS.SetDatesFromPeriod(self.period, self.startdate, self.enddate, pdTS.centralday) 
        
        for d in range(npTS.shape[0]):
            
            acqdate = npTS[d].date()
            
            #acqdatestr = mj_dt.DateToStrDate(acqdate)
            
            acqyyydoy = mj_dt.DateToYYYYDOY(acqdate)
            
            #acqdatestr = '%(d)d' %{'d':acqyyydoy}
            
            self.datumL.append(acqyyydoy)
            
            self.datumD[acqyyydoy] = {'acqdate':acqdate, 'acqdatestr':acqyyydoy}

    def SetMstep(self):
        pdTS = PandasTS(self)
        npTS = pdTS.SetMonthsFromPeriod(self)
        for d in range(npTS.shape[0]):
            acqdate = npTS[d].date()

            acqdatestr = mj_dt.DateToStrDate(npTS[d])
            self.processDateD[acqdate] = {'acqdatestr':acqdatestr[0:6], 'acqdate':acqdate,'timestep':self.period.timestep}
            BALE
                       
    def Varying(self):
        self.datumL.append({'acqdatestr':'varying', 'timestep':'varying'})
        ERRORCHECK
        
    def AllScenes(self, periodD):
        self.SetStartEndDates( periodD)
        self.SetSeasonStartEndDates( periodD )
        #self.datumL.append({'acqdatestr':'allscenes', 'timestep':'allscenes'})
        self.datumL.append('all')
        self.datumD['all'] = {'acqdate':'all', 'acqdatestr':'all', 'startdate':self.startdate, 'enddate':self.enddate, 'startdoy':self.startdoy, 'enddoy':self.enddoy}

        
    def Ignore(self):
        self.datumL.append({'acqdatestr':'ignore', 'timestep':'ignore'})
        ERRORCHECK
        
    def InPeriod(self):
        self.datumL.append({'acqdatestr':'inperiod', 'timestep':'inperiod','startdate':self.startdate, 'enddate':self.enddate})
            
    def FindVaryingTimestep(self,path):
        ERRORCHECK
        if os.path.exists(path):
            folders = [f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))]
            self.datumL = []
            for f in folders:
                try:
                    int(f)
                    self.datumL.append({'acqdatestr':f, 'timestep':'varying'})
                except:
                    pass
                
    def MonthToStr(self,m):
        if m < 10:
            mstr = '0%(m)d' %{'m':m}
        else:
            mstr = '%(m)d' %{'m':m}
        return mstr

    def SetAcqDateDOY(self):
        ERRORCHECK
        for d in self.datumL:
            acqdate = mj_dt.yyyymmddDate(d['acqdatestr'])
            #d['acqdatedaystr'] = mj_dt.DateToYYYYDOY( acqdate)
                   
    def SetAcqDate(self):
        NALLE
        for d in self.datumL:
            pass
            #d['acqdate'] = mj_dt.yyyymmddDate(d['acqdatestr'])
    
class ProcessParams():
    ''' Class for setting all process parameters
    '''  
    
    def __init__(self, process, pnr, jsonFPN):
        '''
        '''
        # Define the process 
        
        self.process = process
        
        self.pnr = pnr
        
        self.jsonFPN = jsonFPN
        
        if self.process.delete and self.process.overwrite:
            
            strD = {'processid': self.process.processid, 'pnr':self.pnr, 'jsonFPN':self.jsonFPN}
            
            exitstr = 'EXITING: the subprocess %(processid)s has both delete and overwrite set to true, only one can he true\n' %strD
        
            exitstr += '    json file with error: %(jsonFPN)s\n' %strD
            
            exitstr += '    process sequence number in file: %(pnr)d' %strD
            
            exit(exitstr)
                 
    def _AssembleParameters(self, session):
        ''' Update missing parameters from default setting
        '''
        
        if self.process.parameters == None or not hasattr(self.process, 'parameters'):
            
            return
            
        jsonParams = dict( list( self.process.parameters.__dict__.items() ) )
        
        queryD = {'subprocid':self.process.processid, 'parent':'process', 
                  'element': 'parameters'}
        
        paramL =['paramid', 'defaultvalue', 'required']
        
        paramRecs = session._SelectMulti(queryD, paramL,'processparams', 'process')

        # Create a dict with non-required parameters     
        defaultD  = dict( [ (i[0],i[1]) for i in paramRecs if not i[2] ] )
        
        # Create a dict with compulsory parameters
        compulsD = dict( [ (i[0],i[1]) for i in paramRecs if i[2] ] )
        
        # Check that all compulsory parameters are included
        for key in compulsD:
            
            if not hasattr(self.process.parameters, key):
            
                exitstr = 'EXITING parameter %s missing for process %s' %(key,self.process.processid)
                
                exit(exitstr)
                
        # Update the parameters
        
        paramD = UpdateDict(jsonParams, defaultD)
        
        self.process.parameters = Struct(paramD)
        
    def _Verbose(self):
        ''' Set the level of text response
        '''
        
        if not hasattr(self.process,'verbose'):
            
            self.process.verbose = 0
                          
    def _SetDefRegion(self, defregion):
        ''' Set default region
        '''   
       
        self.defregion = defregion
                    
    def _SetDb(self, postgresdb):
        ''' Set postgres dataabse as a Struct
        '''   
       
        self.postgresdb = Struct(postgresdb) 
           
    def _SetUserProject(self, userproject):
        ''' Set user project  as a Struct
        '''
        
        self.userproject = Struct(userproject) 
            
    def _SetLayers(self):
        '''
        '''
        self.srcLayerD = {}
        self.dstLayerD = {}
        self._SetSrcLayers()
        self._SetDstLayers()
        
    def _SetSrcLayers(self):
        '''
        '''

        for locus in self.srcLocations.locusL:
            
            self.srcLayerD[locus] = {}
            
            for datum in self.srcPeriod.datumL:
                
                self.srcLayerD[locus][datum] = {}
                
                for comp in self.srcCompD:
                    
                    if self.srcCompD[comp].ext.lower() in ['.txt','.csv','.none']:
                        
                        self.srcLayerD[locus][datum][comp] = TextLayer(self.srcCompD[comp], self.srcLocations.locusD[locus], self.srcPeriod.datumD[datum])
                    
                    elif self.srcCompD[comp].ext.lower() in [ '.shp']:
                    
                        self.srcLayerD[locus][datum][comp] = VectorLayer(self.srcCompD[comp], self.srcLocations.locusD[locus], self.srcPeriod.datumD[datum])
                    
                    else:
                    
                        self.srcLayerD[locus][datum][comp] = RasterLayer(self.srcCompD[comp], self.srcLocations.locusD[locus], self.srcPeriod.datumD[datum])
                    
                    if not path.exists(self.srcLayerD[locus][datum][comp].FPN):
                        
                        warnstr = 'WARNING, source file does not exist: %(p)s' %{'p':self.srcLayerD[locus][datum][comp].FPN}
                        
                        print (warnstr)
               
    def _SetDstLayers(self):
        '''
        '''

        for locus in self.dstLocations.locusL:
            
            self.dstLayerD[locus] = {}
            
            for datum in self.dstPeriod.datumL:

                self.dstLayerD[locus][datum] = {}
                
                for comp in self.dstCompD:
                    
                    if self.dstCompD[comp].ext == '.shp':
                        
                        self.dstLayerD[locus][datum][comp] = VectorLayer(self.dstCompD[comp], self.dstLocations.locusD[locus], self.dstPeriod.datumD[datum])
                    
                    else:
                        
                        self.dstLayerD[locus][datum][comp] = RasterLayer(self.dstCompD[comp], self.dstLocations.locusD[locus], self.dstPeriod.datumD[datum])
                    
                    '''
                    #self.srcLayerD[locus][datum][comp] = self.srcCompD[comp]
                    #self.dstLayerD[locus][datum][comp]['comp'] = self.dstCompD[comp]
                    if (self.dstLayerD[locus][datum][comp]['comp'].celltype == 'vector'):
                        self.dstLayerD[locus][datum][comp]['layer'] = VectorLayer(self.dstCompD[comp], self.dstLocations.locusD[locus], self.srcPeriod.datumD[datum], self.dstpath)
                    else:
                        self.dstLayerD[locus][datum][comp]['layer'] = RasterLayer(self.dstCompD[comp], self.dstLocations.locusD[locus], self.srcPeriod.datumD[datum], self.dstpath)
                    '''
     
    def _SetPaths(self, session):
        ''' Set srouce path and destination path
        '''
                
        def AssemblePath(srcdstpath, jsonPathD):
            ''' Sub processes for assembling paths by combining db entries and json objects
            '''
                        
            # Set query for retrieving path parameters for this process from the db
            queryD = {'subprocid':self.process.processid, 'element': srcdstpath}
            
            # Set the params to retrieve from the db
            paramL = ['paramid', 'paramtyp', 'required', 'defaultvalue']
            
            compRecs = session._SelectMulti(queryD, paramL,'processparams', 'process')

            # Convert the nested list of paths to lists of parameters and default values
            # only include parameters that are not required by the user
            params = [ i[0] for i in compRecs if not i[2] ]
                        
            values = [ i[3] for i in compRecs if not i[2] ]
            
            # Convert the db retrieved parameters and values to a dict
            defaultD = dict( zip( params, values) )
            
            # If this destination path is in the jsonObj, prioritize the given parameters 
             
            if jsonPathD:   
            
                jsonPathD = UpdateDict(jsonPathD, defaultD)
                       
            else:
               
                jsonPathD = defaultD
                
            if srcdstpath == 'srcpath':
                
                self.srcPath = Struct(jsonPathD)
            
            else:
                
                self.dstPath = Struct(jsonPathD)
        
        ''' Source path'''
        
        # Get the json object list of source path
        if hasattr(self.process, 'srcpath'):
            
            jsonPathD = dict( list( self.process.srcpath.__dict__.items() ) )
            
        else:
            
            jsonPathD = False
        
        AssemblePath('srcpath', jsonPathD)
        
  
        ''' Destination path''' 
             
        # Get the json object list of destination compositions
        if hasattr(self.process, 'dstpath'):
             
            jsonPathD = dict( list( self.process.dstpath.__dict__.items() ) )
            
        else:
            jsonPathD = False
        
        AssemblePath('dstpath', jsonPathD)
        
    def _SetCompositions(self, session):
        '''
        '''
        
        # Set the dictionaries to hold the source /src) and destination (dst) compositions
        self.srcCompD = {}; self.dstCompD = {}
        
        def GetComps(srcdstcomp):
            '''
            '''
                        
            jsonCompD = {}
            
            # Select the composition(s) from the database
            queryD = {'subprocid':self.process.processid, 'parent': 'process', 'element': srcdstcomp, 'paramtyp': 'element'}
                
            paramL = ['paramid', 'defaultvalue', 'required']
            
            processComps = session._SelectMulti(queryD, paramL,'processparams', 'process')
     
            if len(processComps) > 0:
 
                if hasattr(self.process, srcdstcomp):
                    
                    if srcdstcomp == 'srccomp':
                        
                        compsL = self.process.srccomp
                        
                    else:
                        
                        compsL = self.process.dstcomp
                        
                    if not isinstance(compsL, list):
                        
                        exitstr = 'Either scrcomp or dstcomp is not a list'
                        
                        exit(exitstr)
                        
                                        
                    for jsonComp in compsL:
                        
                        # Convert the jsonComposition from Struct to dict_items
                        dct = jsonComp.__dict__.items()
                        
                        # Loop over the dcit_items (only contains 1 item)
                        for item in dct:
                            
                            # convert the dict_item to an ordinary dict 
                            jsonCompD[item[0]] = dict ( list(item[1].__dict__.items() ) )
                                                                                             
            return processComps, jsonCompD
           
        def AssembleComp(srcdstcomp, jsonCompD, defaultvalue, layerId):
            ''' Sub processes for assembling compostions by combining db entries and json objects
            '''
                           
            # Set query for retrieving compositions for this process from the db
            queryD = {'subprocid':self.process.processid, 'parent': srcdstcomp, 'element': defaultvalue}
        
            # Set the params to retrieve from the db
            paramL = ['paramid', 'paramtyp', 'required', 'defaultvalue']
            
            # Retrieve all compositions for this process from the db
            compParams = session._SelectMulti(queryD, paramL,'processparams', 'process')
            
            # Convert the nested list of compositions to lists of parameters and default values
            # only include parameters that are not required by the user
            params = [ i[0] for i in compParams if not i[2] ]
                        
            values = [ i[3] for i in compParams if not i[2] ]
            
            # Convert the db retrieved parameters and values to a dict
            defaultD = dict( zip( params, values) )
            
            # Convert the nested list of compositions to lists of parameters and default values
            # only include parameters that are not required by the user
            params = [ i[0] for i in compParams if i[2] ]
                        
            values = [ i[3] for i in compParams if i[2] ]
            
            # Convert the user required parameters and values to a dict
            requiredD = dict( zip( params, values) )
            
            # If this composition is in the jsonObj, prioritize the given json parameters 
            if defaultvalue == '*' or defaultvalue == layerId: 
                                
                mainD = UpdateDict( jsonCompD, defaultD)
                                       
            else:
               
                mainD = defaultD
                
            # Check that all required parameters are given
            for key in requiredD:
                
                if not key in mainD:
                    
                    exitstr = 'EXITING, the required parameter %s missing in %s for layer' %(key, self.process.processid, layerId)
                
                    exit ( exitstr )
                    
            if srcdstcomp == 'srccomp':
            
                self.srcCompD[mainD['layerid']] = Composition(mainD, self.process.parameters, self.procsys.srcsystem, self.procsys.srcdivision, self.srcPath)

            else:
                
                self.dstCompD[mainD['layerid']] = Composition(mainD, self.process.parameters, self.procsys.dstsystem, self.procsys.dstdivision, self.dstPath)
      
        ''' Source compositions''' 
                               
        processComps, jsonCompD = GetComps('srccomp')
                          
        # Start processing all the required compositions 
        
        if len(processComps) > 0:
            
            # if there is only one comp in the db and with default value == '*', 
            if len(processComps) == 1 and processComps[0][1] == '*':
                
                if len(jsonCompD) > 0:
                
                    for compkey in jsonCompD:
                    
                        AssembleComp('srccomp', jsonCompD[compkey], '*',compkey)
                        
                else:
                    
                    exitstr = 'Exiting, the process %s need at least one source composition' %(self.pp.processid)
                    
                    exit(exitstr)
            else:
                
                for rc in processComps:   
                
                    SNLLE
                    
        ''' Destination compositions''' 
        
        processComps, jsonCompD = GetComps('dstcomp')
              
        # Loop over all compositions
        if len(processComps) > 0:
            
            # if there is only one comp in the db and with default value == '*', 
            if len(processComps) == 1 and processComps[0][1] == '*':
                
                if len(jsonCompD) > 0:
                
                    for compkey in jsonCompD:
                        
                        AssembleComp('dstcomp', jsonCompD[compkey], '*',compkey)
                        
                else:
                    
                    AssembleComp('dstcomp', {}, '*', '*')

            else:
                
                for rc in processComps:   
                
                    SNLLE
             
    def _CopyCompositions(self, session): 
        ''' For processes where the source comp is copied to the destination comd
        '''  
            
        def AssembleDstComp(jsonCompD, compId):
            ''' Sub processes for assembling compostions by combining db entries and json objects
            '''
                                         
            # Set query for retrieving compositions for this process from the db
            queryD = {'subprocid':self.process.processid, 'parent': 'dstcopy'}
        
            # Set the params to retrieve from the db
            paramL = ['paramid', 'paramtyp', 'required', 'defaultvalue']
            
            # Retrieve all compositions for this process from the db
            compParams = session._SelectMulti(queryD, paramL,'processparams', 'process')
            
            # Convert the nested list of compositions to lists of parameters and default values
            # only include parameters that are not required by the user
            params = [ i[0] for i in compParams if not i[2] ]
                        
            values = [ i[3] for i in compParams if not i[2] ]
            
            # Convert the db retrieved parameters and values to a dict
            defaultD = dict( zip( params, values) )
            
            # Combine any data given in the json parameter file and the db  
                            
            mainD = UpdateDict( jsonCompD, defaultD )
                
            self.dstCompD[compId] = Composition(mainD, self.process.parameters, self.procsys.dstsystem, self.procsys.dstdivision, self.dstPath)
            
        # Select the composition(s) from the database
        queryD = {'subprocid':self.process.processid, 
                  'parent': 'process', 'element': 'dstcopy', 'paramid': 'srccomp'}
        
        paramL =['paramid', 'defaultvalue', 'required']
        
        copyRec = session._SelectMulti(queryD, paramL,'processparams', 'process')
        
        jsonCompD = {}
        
        for c in copyRec:
            
            if c[1] == '*':
                
                compsL = list( self.process.dstcopy[0].__dict__.items() )
                
                # Loop over the destination compositions (copies of srcComp)
                for jsonComp in compsL:
                       
                    # convert each composition to a dict_item (this is not a true dict) 
                    dct = jsonComp[1].__dict__.items()
                        
                    # Convert the dict_item to a true dict (oterhwise UpdateDict does not work)
                    jsonCompD[jsonComp[0]] = dict ( list (dct) )
                        
                    # Create a dict from the corresponding source compositon (srcComp)
                    srcD = dict ( list ( self.srcCompD[jsonComp[0]].__dict__.items() ) )
                    
                    # Combine the json object dict and the srccomp dict
                    mainD = UpdateDict( jsonCompD[jsonComp[0]], srcD)
                    
                    # Complement with any default settings (i.e. the parameters required for a destination composition)
                    AssembleDstComp(mainD,jsonComp[0])
                    
                '''   
                # Create a dict from the                 
                #mainD = dict (list ( self.process.dstcopy.__dict__.items() ) )
                
                srcD = dict ( list ( self.srcCompD[self.process.dstcopy.srccomp].__dict__.items() ) )
            
                mainD = UpdateDict( mainD, srcD)
                
                # Complement with any default settings (i.e. the parameters required for a destination composition)
                
                AssembleDstComp(mainD)
                
                self.dstCompD[self.process.dstcopy.srccomp] = Composition(mainD, self.process.parameters, self.procsys.dstsystem, self.procsys.dstdivision, self.dstPath)
                
                #self.dstCompD[self.process.dstcopy.srccomp] = mainD
                '''
                
            else:
                
                SNULLE
                     
    def _Location(self, session):
        ''' Set source and destination location
        '''
        
        self.srcLocations = Location(self.process.processid, self.defregion, self.procsys.srcsystem, self.procsys.srcdivision, self.procsys.srcepsg, session)

        self.dstLocations = Location(self.process.processid, self.defregion, self.procsys.dstsystem, self.procsys.dstdivision, self.procsys.dstepsg, session)

    def _SetTimeStep(self, timestep):
        ''' Set the timestep for the source and destination of this process
        '''
        if hasattr(self.process, 'srcperiod'):
            
            self.srcPeriod = TimeSteps(self.process.srcperiod, self.verbose)
            
        else:
            
            self.srcPeriod = timestep
            
        if hasattr(self.process, 'dstperiod'):
            
            self.dstPeriod = TimeSteps(self.process.dstperiod)
            
        else:
            
            self.dstPeriod = timestep
  
    def _GetProcessSystem(self, session, system):
        ''' The process system components is predefined
        '''
        
        queryD = {'subprocid': self.process.processid,'system':system}
                    
        paramL = ('srcsystem', 'dstsystem', 'srcdivision', 'dstdivision', 'srcepsg', 'dstepsg')
        
        record = session._SelectProcessSystem(queryD, paramL)
        
        if record == None:
            
            exitstr = 'EXITING - the system userproject system setting %(system)s is not support the process %(subprocid)s' %queryD
            
            exit(exitstr)

        self.procsys = Struct(record) 
            
    def _GetRootProcess(self, session):
        ''' Get the root process to which the sub process belongs
        '''
        
        queryD = {'subprocid': self.process.processid}
        
        record = session._SelectRootProcess(queryD)
            
        if record == None:
            
            exitstr = 'Exiting - The process "%(subprocid)s" is not registered in the Framework db' %queryD
        
            exit(exitstr)
            
        self.rootprocid, self.processStratum = record
        
      
    def _AssembleSrcRaw(self, session):
        ''' Set the raw source data
        '''

        srcRawD = {}; self.srcRawD = {}
        
        for item in self.process.srcraw:
            
            itemL = list( item.__dict__.items() )
                        
            srcRawD[itemL[0][0]] = itemL[0][1]
        
        # The srcraw must correspond to the destination compositions
        for key in self.dstCompD:
        
            if key not in srcRawD:
                
                exitstr = 'EXITING - the composition %s has no corresponding srcraw element' %(key)
             
                exit(exitstr)
                            
            queryD = {'subprocid':self.process.processid, 'parent':'srcraw', 
                      'element': '*'}
      
            paramL =['paramid', 'defaultvalue', 'required']
            
            paramRecs = session._SelectMulti(queryD, paramL,'processparams', 'process')
    
            # Create a dict with non-required parameters     
            defaultD  = dict( [ (i[0],i[1]) for i in paramRecs if not i[2] ] )
            
            # Create a dict with compulsory parameters
            compulsD = dict( [ (i[0],i[1]) for i in paramRecs if i[2] ] )
            
            # Check that all compulsory parameters are included
            for c in compulsD:
                
                if not hasattr(srcRawD[key], c):

                    exitstr = 'EXITING - srcraw element %s missing for composition %s' %(c,key)
                    
                    exit(exitstr)
                    
            # Update the parameters
            jsonParams = dict( list( srcRawD[key].__dict__.items() ) )
            
            #newDict = UpdateDict(srcRawD[key], defaultD)
            rawDict = UpdateDict(jsonParams, defaultD)
            
            #self.srcRawD[key] = Struct(srcRawD[key])
            self.srcRawD[key] = Struct(rawDict)
        
    def _UserStratumRights(self): 
        ''' Check if the logged in use has the right to the process and region
        '''
        pass
        '''
        stratum
        print ('hej',self.processStratum)
        print ('hej',self.processStratum)
        '''
          
class Struct(object):
    ''' Recursive class for building project objects
    '''
    def __init__(self, data):
        for name, value in data.items():
            setattr(self, name, self._wrap(value))

    def _wrap(self, value):
        if isinstance(value, (tuple, list, set, frozenset)): 
            return type(value)([self._wrap(v) for v in value])
        else:
            return Struct(value) if isinstance(value, dict) else value

class JsonParams ():
    '''
    classdocs
    '''
    def __init__(self, session):
        '''
        '''
        
        self.session = session
        
    def _JsonObj(self,jsonFPN):
        
        # Set the process list
        processD = {}
        
        # Read the initial (default) parameters   
        defaultjsonFPN = '/Users/thomasgumbricht/Documents/geoimagine_default_thomasg.json' 
        
        iniParams = self._JsonParams (defaultjsonFPN) 
                        
        self.jsonParams = self._JsonParams (jsonFPN)
                
        # update userproject, fill in any default setting from the project default json
        self.jsonParams = UpdateDict(self.jsonParams, iniParams)
        
        # update processes, fill in any default setting from the project default json
        if 'process' in self.jsonParams:
            
            pnr = -1
            
            for p in self.jsonParams['process']:
                
                pnr += 1
            
                processD[pnr] = {'json': p}
                
                # This seems to have no effect
                p = UpdateDict(p, iniParams['process'][0], jsonFPN)
            
        # Convert jasonParams for class attributes
        self.params = Struct(self.jsonParams)
                
        # Get the default region
        self._GetDefRegion(self.session)
        
        # Get the overall timestep
        if hasattr(self.params, 'period'):
            
            timestep = TimeSteps(self.params.period, p['verbose'])
            
        else:
            
            # When set to False timestep becomes static
            timestep = TimeSteps( False, p['verbose'] )
        
        # Loop over the processes defined in this object 
        pnr = -1
        
        for p in self.params.process:
            
            pnr += 1
            
            # Set the core information
            PP = ProcessParams(p,pnr,jsonFPN)

            # Check and assemble process parameters
            PP._AssembleParameters(self.session)
            
            # Said the level of text response
            PP._Verbose()
            
            # Set default region
            PP._SetDefRegion(self.defregion)
  
            # Set postgres dataabase as Struct 
            PP._SetDb(self.jsonParams['postgresdb'])
  
            # Set the user project as a Struct                
            PP._SetUserProject(self.jsonParams['userproject'])
        
            # Get the process rootprocess
            PP._GetRootProcess(self.session)
            
            # Get the processing system
            PP._GetProcessSystem(self.session, self.jsonParams['userproject']['system'])
            
            # Set the locations
            PP._Location(self.session)
            
            # Get the processing system
            PP._SetTimeStep(timestep)
            
            # Set the paths
            PP._SetPaths(self.session)
            
            # Set the compositions
            PP._SetCompositions(self.session)
            
            PP._CopyCompositions(self.session)
            
            PP._SetLayers()
            
            PP._UserStratumRights()
            
            processD[pnr]['PP'] = PP
            
            processD[pnr]['p'] = p
            
        return processD
    
    def _UpdateProjectOld(self, mainD, defaultD):
        '''
        '''
        
        d = {key: defaultD.get(key, mainD[key]) for key in mainD}
        
        for key in defaultD:
            
            if key not in d:
            
                mainD[key] = defaultD[key]
                                   
    def _JsonParams(self,path):
        '''
        '''
        
        # Opening JSON file 
        f = open(path, "r") 
                 
        # returns JSON object
        return json.load(f)
                                  
    def _GetDict(self):
        '''
        '''
        return self.jsonParams
    
    def _GetDefRegion(self, session):
        ''' Set default region
        '''

        if self.params.userproject.tractid:
            
            queryD = {'tract': self.params.userproject.tractid}
            
            rec = session._SelectTractDefRegion(queryD)

            if rec == None:
                
                exitstr = 'EXITING - the tractid %(tract)s does not exist in the database' %queryD
                
                exit(exitstr)
                
            elif rec[1] == 'D':
                
                exitstr = 'EXITING - the tractid %(tract)s is set to a default region' %queryD
                
                exit(exitstr)
                
            self.defregion = rec[0]
        
        elif self.self.params.userproject.siteid:
            
            exit('add site defregion')
        
        if self.defregion == 'globe':
            
            exit('EXITING - your defined region "%s" is based on the default region "globe", which is not allowed' %(self.params.userproject.tractid))
        
        #print ("TGTODO Check if user has the right to this region")

if __name__ == '__main__':

    jsonFPN = '/Users/thomasgumbricht/GitHub/geoimagine-setup_db/doc/xmlsql/general_schema_v80_sql.json'
    
    params = Params(jsonFPN)
    
