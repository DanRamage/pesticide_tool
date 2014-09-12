import sys
import optparse
import logging
import logging.config

import simplejson
from datetime import datetime
import csv
import codecs


class pestCategory(object):
  def __init__(self, logger=False):
    self.categoryDict = {}
    self.subCategoryDict = {}
    self.pestDict = {}
    self.classPestDict = {}
    self.pestList = []
    self.pestClass = {}

    self.logger = None
    if(logger):
      self.logger = logging.getLogger(type(self).__name__)

  def UnicodeDictReader(self, utf8_data, fieldNames, **kwargs):    
      csv_reader = csv.DictReader(utf8_data, **kwargs)
      for row in csv_reader:
        yield dict([(key, unicode(value, 'utf-8')) for key, value in row.iteritems()])
  
  def importFile(self, buttonFilename):
    retVal = False
    row_entry_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if(self.logger):
      self.logger.info("Importing button configuration.")
    fieldNames = [
                  "Class of Pesticide",
                  "Main Category",
                  "category title",
                  "category picture",
                  "Pest",
                  "Pest Picture",
                  "Main Category Image"
                  ]
    try:
      csvSrcFile = codecs.open(buttonFilename, mode = 'r', encoding='utf-8')
      dataFile = self.UnicodeDictReader(csvSrcFile, fieldNames)
    except Exception,e:
      if(self.logger):
         self.logger.exception(e)
    else:
      catId = 0
      subCatId = 0
      pestId = 0
      pestClassId = 0
      try:     
        for line in dataFile:
          #Check for new category.
          curCategory = None
          catTitle = line['Main Category'].title()
          #for category in categoryList:
          if(catTitle not in self.categoryDict):
            category = {
              'pk': catId,
              'model': 'data_manager.category',
              'fields': {
                'row_entry_date': row_entry_date,
                'name': catTitle,
                'image_url': line['Main Category Image'],
                'sub_categories': []
                #'pesticide_class': []
              }
            }
            self.categoryDict[catTitle] = category
            catId += 1

          curCategory = self.categoryDict[catTitle]
            
          #Check for new sub category.
          curSubCat = None
          subCatTitle = line['category title'].title()
          if(subCatTitle not in self.subCategoryDict):
            subCat = {
              'pk': subCatId,
              'model': 'data_manager.SubCategory',
              'fields': {
                'row_entry_date': row_entry_date,
                'name': subCatTitle,
                'image_url': line['category picture'],
                'pests': []
              }
            }
            subCatId += 1

            self.subCategoryDict[subCatTitle] = subCat
            #Each time we add a new subcategory, add the id of it to the current category.
            #curCategory['sub_categories'].append(subCat['row_id'])
            curCategory['fields']['sub_categories'].append(subCat['pk'])
            
          curSubCat = self.subCategoryDict[subCatTitle]
          
          #Check for new pesticide class.
          classTitles = line['Class of Pesticide'].split(';')
          for classTitle in classTitles:
            classTitle = classTitle.title()
            #for category in categoryList:
            if(classTitle not in self.pestClass):
              pestCls = {
                'pk': pestClassId,
                'model': 'data_manager.PesticideClass',
                'fields': {
                  'row_entry_date': row_entry_date,
                  'name': classTitle
                }
              }
              self.classPestDict[classTitle] = {}
              pestClassId += 1
              self.pestClass[classTitle] = pestCls
              #Add the row ids of any new pesticide classes to the category.
              #curCategory['fields']['pesticide_class'].append(pestCls['pk'])
            
          #pestTitle = line['Pest'].title()
          pestTitle = line['Pest'].strip()

          """
          if(pestTitle not in self.pestDict):
            #Add the pest to the appropriate category structure.
            pest = {
              'pk': pestId,
              'model': 'data_manager.Pest',
              'fields': {
                'row_entry_date': row_entry_date,
                'name': pestTitle,
                'display_name': pestTitle.title(),
                'image_url': line['Pest Picture']
              }
            }
            pestId += 1
            self.pestDict[pestTitle] = pest
            curSubCat['fields']['pests'].append(pest['pk'])
          else:
            self.logger.debug("Repeat Pest: %40s in Sub Cat: %20s Class: %20s" % (pestTitle, subCatTitle, classTitles))
            i = 0
          """
          #Add the pest to the appropriate category structure.
          pest = {
            'pk': pestId,
            'model': 'data_manager.Pest',
            'fields': {
              'row_entry_date': row_entry_date,
              'name': pestTitle,
              'display_name': pestTitle.title(),
              'image_url': line['Pest Picture']
            }
          }
          curSubCat['fields']['pests'].append(pest['pk'])

          pestId += 1

          if(pestTitle not in self.pestDict):
            self.pestDict[pestTitle] = pest
          else:
            self.logger.debug("Repeat Pest: %40s in Sub Cat: %20s Class: %20s" % (pestTitle, subCatTitle, classTitles))


          self.classPestDict[classTitle][pestTitle] = {'pk': pest['pk']}

          self.pestList.append(pest)
        retVal = True
      except Exception,e:
        if(self.logger):
          self.logger.exception(e)
      csvSrcFile.close()
      if(self.logger):
        self.logger.info("Finished button configuration import.")      
      return(retVal)

  def writePestCategoriesJSON(self, jsonOutputFile):
    #Now write JSON configuration file.
    try:
      if(self.logger):
        self.logger.info("Creating button configuration json file.")
      jsonFile = open(jsonOutputFile, 'w')
    except Exception,e:
      if(self.logger):
        self.logger.exception(e)
    else:
      jsonData = {}
      jsonData['layout'] = {}
      jsonData['layout']['pest_categories'] = self.categoryDict
      try:
        jsonFile.write(simplejson.dumps(jsonData, sort_keys=False))
        jsonFile.close()
      except Exception,e:
        if(self.logger):
          self.logger.exception(e)

class pesticideData(object):
  def __init__(self, logger=True):
    self.logger = None
    if(logger):
      self.logger = logging.getLogger(type(self).__name__)
      
      self.pesticideData = None
      self.hazardsDict = None

  def UnicodeDictReader(self, utf8_data, fieldNames, **kwargs):    
      csv_reader = csv.DictReader(utf8_data, restkey='bucket', **kwargs)
      try:
        for row in csv_reader:
          if('bucket' in row):
            del row['bucket']
          yield dict([(key, unicode(value, 'utf-8')) for key, value in row.iteritems()])
      except Exception,e:
        if(self.logger):
          self.logger.exception(e)
  def importData(self, pesticideDataCSV, categoryDataCSV, clemsonWebReq): 
    retData = None
    self.categoryData = pestCategory(logger)  
    if(self.categoryData.importFile(categoryDataCSV)):
      self.importPesticideData(pesticideDataCSV, clemsonWebReq)      
      retData = {}
      retData['pesticide'] = self.pesticideData
      retData['category'] = self.categoryData.categoryDict
      retData['sub_category'] = self.categoryData.subCategoryDict
      #retData['pest'] = self.categoryData.pestDict
      retData['pest'] = self.categoryData.pestList
      retData['class'] = self.categoryData.pestClass
      retData['warning'] = self.hazardsDict
      retData['brand'] = self.brandsDict
      retData['application_area'] = self.applicationAreaDict 
    return(retData)
    
  def importPesticideData(self, pesticideDataCSV, clemsonWebReq):  
    #Attempt to open the file for reading.
    retVal = False
    fieldNames = [
      "Pesticide Usage Category",
      "Clemson Name",
      "Compound (Active Ingredient Pesticide)",
      "Insect",
      "Weed",
      "Algae",
      "Fungus",
      "Cumulative Score",
      "Relative Potential Ecosystem Hazard",
      "Cum. Score Color",
      "Class of Pesticide",
      "high runoff concern",
      "high_soil_binding",
      "drift_concern",
      "high_application_rate",
      "bioaccumulation_potential",
      "acute_mammalian_toxicity",
      "chronic_mammalian_toxicity",
      "toxic_honey_bee",
      "acute_aquatic_hazard",
      "chronic_aquatic_hazard",
      "high_avian_toxicity",
      "phytotoxicity warning",
      "long half-life"
                          
    ]           
    try:
      #csvSrcFile = codecs.open(pesticideDataCSV, mode='rU', encoding='utf-8', errors='ignore')        
      csvSrcFile = open(pesticideDataCSV, 'rU')
      dataFile = self.UnicodeDictReader(csvSrcFile, fieldNames)
    except Exception,e:
      if(self.logger):
         self.logger.exception(e)  
    else:
      row_entry_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
      self.pesticideData = {}
      pesticideId = 0
      self.hazardsDict = {}
      hazardId = 0
      self.brandsDict = {}
      brandId = 0
      self.applicationAreaDict = {}
      appId = 0
      #hazards are columns in the pest_pictures data. We can build their entries except for the image_url now,
      #then check each hazard type's image_url as we loop through the compound_list to see which ones are empty.
      ndx = fieldNames.index('high runoff concern')
      while ndx < len(fieldNames):
        hazTitle = fieldNames[ndx].title()
        self.hazardsDict[fieldNames[ndx]] = {
          'pk': hazardId,
          'model': 'data_manager.Warning',
          'fields': {
            'row_entry_date': row_entry_date,
            'name': hazTitle,
            'display_name': hazTitle.replace('_', ' '),
            'image_url': None
          }
        }
        hazardId += 1
        ndx += 1
      
      try:
        lineCnt = 1
        for line in dataFile:
          pesticide = {
            'pk': None,
            'model': 'data_manager.ActiveIngredient',
            'fields':
              {
                'row_entry_date': row_entry_date,
                'name': None,
                'display_name': None,
                'cumulative_score': None,
                'relative_potential_ecosystem_hazard': None,
                'warnings': [],
                'pests_treated': [],
                'pesticide_classes': []
              }
          }
          #line 0 is header, read it but don't process.
          if(lineCnt > 0):
            if(self.logger):
              self.logger.debug("Adding line: %d" % (lineCnt))
            #self.addData(line)
            if(len(line) < len(fieldNames)):      
              if(self.logger):
                self.logger.error("Line: %d Missing Columns.")
            else:
              if(self.logger):
                self.logger.info("Processing pesticide compound: %s" % (line['Compound (Active Ingredient Pesticide)']))
              pesticide['pk'] = pesticideId
              pesticideId += 1
              pesticide['fields']['name'] = line['Compound (Active Ingredient Pesticide)'].strip()
              pesticide['fields']['display_name'] = pesticide['fields']['name'].strip().title()
              try:
                pesticide['fields']['cumulative_score'] = float(line['Cumulative Score'])
              except ValueError,e:
                if(self.logger):
                  self.logger.error("Line: %d Cumulative Score Value: %s is not numeric. Value must be a float." %( lineCnt, line['Cumulative Score']))
                  break
              pesticide['fields']['relative_potential_ecosystem_hazard'] = line['Relative Potential Ecosystem Hazard']
              
              #Below are all data that are associated with the pesitide. We've got to look up the id's from the data
              #loaded from the pest_pictures data. 
              
              #The pests are categorized from the pestCategory object. Previously we only broke the pests
              #down into the 4 categories of weed, algae, fungus and insect. Now we use a CSV file that
              #categorizes, sub-categorizes the pests along with their images.
              pests = []
              cTypes = []
              pestTypes = line['Insect'].split(';')
              if(pestTypes[0] != '----'):
                pests.extend([pest.strip() for pest in pestTypes])
                cTypes.append("Insecticide")

              pestTypes = line['Weed'].split(';')
              if(pestTypes[0] != '----'):
                pests.extend([pest.strip() for pest in pestTypes])
                cTypes.append("Herbicide")

              pestTypes = line['Algae'].split(';')
              if(pestTypes[0] != '----'):
                pests.extend([pest.strip() for pest in pestTypes])
                cTypes.append("Algaecide")

              pestTypes = line['Fungus'].split(';')
              if(pestTypes[0] != '----'):
                pests.extend([pest.strip() for pest in pestTypes])
                cTypes.append("Fungicide")

              #Now use the pests list to look up the row_id(pest id) to associate with the pesticide.
              for pestName in pests:
                pestFound = False
                for cType in cTypes:
                  if cType in self.categoryData.classPestDict:
                    #if(len(pestName) and pestName in self.categoryData.pestDict):
                    if(len(pestName) and pestName in self.categoryData.classPestDict[cType]):
                      #pesticide['fields']['pests_treated'].append(self.categoryData.pestDict[pestName]['pk'])
                      pk = self.categoryData.classPestDict[cType][pestName]
                      pesticide['fields']['pests_treated'].append(pk['pk'])
                      pestFound =  True
                      break
                  else:
                    if(self.logger):
                      self.logger.error("Line: %d Pest: %s Class Type: %s does not exist." % (lineCnt,pestName,cType))

                if pestFound is not True:
                  if(self.logger):
                    self.logger.error("Line: %d Pest: %s in pesticide data was not defined in the pest_pictures data." % (lineCnt,pestName))


              #Now associate the pest classes
              pesticideClasses = line['Class of Pesticide'].split(';')
              for pestClassName in pesticideClasses:
                pestClassName = pestClassName.strip().title()
                if(pestClassName in self.categoryData.pestClass):
                  pesticide['fields']['pesticide_classes'].append(self.categoryData.pestClass[pestClassName]['pk'])
                else:
                  if(self.logger):
                    self.logger.error("Pesticide Class: %s in pesticide data was not defined in the pest_pictures data." % (pestClassName))
              
              #Check to see if the file line contains a hazards image that we didn't have.
              #If the hazard image url is present, then we want to add that hazard to the pesticide.
              ndx = fieldNames.index('high runoff concern')
              while ndx < len(fieldNames):
                hazardName = fieldNames[ndx]
                if(line[hazardName] != '----'):
                  if(self.hazardsDict[hazardName]['fields']['image_url'] == None):
                    url = line[hazardName]
                    if line[hazardName].find('http://') == -1:
                      url = "http://%s" % line[hazardName].strip()
                    self.hazardsDict[hazardName]['fields']['image_url'] = url
                  pesticide['fields']['warnings'].append(self.hazardsDict[hazardName]['pk'])
                ndx += 1

              #If we have a valid object for the clemson pesticide site, we do the screen scraping
              #for the brands and application sites of the active ingredient.
              if clemsonWebReq:
                pesticide['brandList'] = []
                #We use the Clemson centric name for the compound when doing the screen scraping.
                activeIngredient = line['Clemson Name']
                if(len(activeIngredient) == 0):
                  activeIngredient = pesticide['name']
                activeIngredientData = clemsonWebReq.searchByActiveIngredient(activeIngredient)
                if(activeIngredientData):
                  for ndx, brandData in enumerate(activeIngredientData):
                    #THe url for the label is not consistent on the website, so we have to do 2 searches.
                    imageUrl = ''
                    if('labelLink' in brandData['brandInfo']):
                      imageUrl = brandData['brandInfo']['labelLink']
                    elif('labelLink2' in brandData['brandInfo']):
                      imageUrl = brandData['brandInfo']['labelLink2']
                    brandCls = {'row_id' : brandId,
                             'image_url' : imageUrl,
                             'application_area' : []}
                    #Enmumerate through the application sites.
                    for siteNdx, appSiteName in enumerate(brandData['brandInfo']['siteList']):
                      #If we don't already have that application area, add it to the dictionary.
                      appSiteName = appSiteName.strip()
                      if(appSiteName not in self.applicationAreaDict):                        
                        self.applicationAreaDict[appSiteName] = {'row_id' : appId}
                        appId += 1                        
                      #Append the id of the application area to the brand.
                      brandCls['application_area'].append(self.applicationAreaDict[appSiteName]['row_id'])
                    #Add the brand information, keyed on the brandName.
                    brandName = brandData['brandName'].strip()
                    if(brandName not in self.brandsDict):                    
                      self.brandsDict[brandName] = brandCls
                      brandId += 1
                    #Add the brand id to the pesticide.
                    pesticide['brandList'].append(self.brandsDict[brandName]['row_id'])
                    
              self.pesticideData[pesticide['fields']['name']] = pesticide
              
          lineCnt += 1
          
          
        retVal = True
      except StopIteration,e:
        if(self.logger):
          self.logger.info("Finished reading file.")
          return(True)
      except Exception,e:
        if(self.logger):
          self.logger.exception(e)
          
      csvSrcFile.close()    
      return(retVal)
  
  def exportInitialJSON(self, jsonOutputFile):
    try:
      if self.logger:
        self.logger.info("Outputting initial json data file: %s" % (jsonOutputFile))
      jsonFile = open(jsonOutputFile, 'w')
    except Exception,e:
      if(self.logger):
        self.logger.exception(e)
    else:
      jsonData = []
      #Write out categories
      for category in self.categoryData.categoryDict:
        jsonData.append(self.categoryData.categoryDict[category])
      for subcategory in self.categoryData.subCategoryDict:
        jsonData.append(self.categoryData.subCategoryDict[subcategory])
      #for pest in self.categoryData.pestDict:
      #  jsonData.append(self.categoryData.pestDict[pest])
      for pest in self.categoryData.pestList:
        jsonData.append(pest)
      for pesticide_class in self.categoryData.pestClass:
        jsonData.append(self.categoryData.pestClass[pesticide_class])
      for warning in self.hazardsDict:
        jsonData.append(self.hazardsDict[warning])
      for pesticide in self.pesticideData:
        jsonData.append(self.pesticideData[pesticide])
      try:
        jsonFile.write(simplejson.dumps(jsonData, sort_keys=False, indent=4 * ' '))
        jsonFile.close()
        if self.logger:
          self.logger.info("Initial json data output complete")
      except Exception,e:
        if(self.logger):
          self.logger.exception(e)

    return False
if __name__ == '__main__':
  import ConfigParser
  
  logger = None
  try:
    parser = optparse.OptionParser()
    parser.add_option("-i", "--ImportDataFile", dest="importFilename",
                      help="Pesticide datafile to import." )   
    parser.add_option("-u", "--ImportButtonFile", dest="importButtonFilename",
                      help="CSV File with the pest/button assignments." )   
    parser.add_option("-f", "--JSONFile", dest="jsonFile",
                      help="Export the pesticide data in a JSON format")
    parser.add_option("-b", "--UseJSONCallbackFunction", dest="useCallback", action="store_true",
                      help="If set, wraps the JSON data in a callback function.")
    parser.add_option("-c", "--ConfigFile", dest="cfgFile",
                      help="Full path to the file containing the settings to use for database connection, log files, etc")
    parser.add_option("-d", "--DeleteRecordsBeforeImport", dest="deleteRecordsBeforeImport", action="store_true",
                      help="Flag if set will clean the database before importing the new data.")
    parser.add_option("-w", "--UseClemsonData", dest="useClemsonData", action="store_true",
                      help="Flag if set we connect to the Clemson pesticide web service to pull data such as Brands.")
    (options, args) = parser.parse_args()

    cfgFile = ConfigParser.RawConfigParser()
    cfgFile.read(options.cfgFile)
    logFile = cfgFile.get('logging', 'configfile')
    if(logFile):
      logging.config.fileConfig(logFile)
      logger = logging.getLogger("pesticide_logger")
      logger.info("Logging started.")

    if(options.importButtonFilename):
      try:
        jsonFilePath = cfgFile.get('client_config', 'configjson')
      except ConfigParser.Error, e:  
        jsonFilePath = 'layout_config.json'
      
    if(options.importFilename):
      pestData = pesticideData(logger=True)
      webLookup = None
      #if(options.useClemsonData):
      #  webLookup = clemsonWebService(options.cfgFile, True)
      
      pesticideData = pestData.importData(options.importFilename,
                                          options.importButtonFilename,
                                          webLookup)
      pestData.exportInitialJSON(options.jsonFile)

    if(logger):
      logger.info("Importing completed.")
      
  except Exception, e:
    import sys
    import traceback

    if( logger ):
      logger.exception(e)
    else:
      traceback.print_exc(e)
    sys.exit(-1)
  