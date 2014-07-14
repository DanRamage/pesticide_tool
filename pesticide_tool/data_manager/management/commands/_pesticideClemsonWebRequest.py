import ConfigParser
import requests
import logging
import logging.config
from bs4 import BeautifulSoup
import re
from urlparse import urlparse,parse_qs
import simplejson as json
import csv


class web_data_collector(object):
  def __init__(self, url, params, logger_name):
    self.logger = None
    self.url = url
    self.params = params
    self.session = None
    if(logger_name):
      self.logger = logging.getLogger(logger_name)

  def sendRequest(self, url=None, params=None):
    try:
      if self.session is None:
        self.session = requests.session()
      if url is None:
        url = self.url
      if params is None:
        params = self.params
      if(self.logger):
        self.logger.debug("Sending request: %s Params: %s" % (url, params))
      results = self.session.get(url, params=params)
      if(results.status_code == 200):
        self.scrape_page(results.text)
        return(True)
      else:
        self.logger.error("Did not receive a valid response from request. Reason: %s" % (results.reason))
    except Exception,e:
      if(self.logger):
        self.logger.exception(e)
    return(False)

  def scrap_page(self, page):
    soup = BeautifulSoup(page)
    pages = soup.find_all('input', type='Submit', value="  >|  ")

  def page_results(self, pages):
    if pages:
      try:
        if pages.attrs and 'name' in pages.attrs:
          next_page = pages.attrs['name']
          value = pages.attrs['value']
          params = self.params
          params[next_page] = value
          self.sendRequest(self.url, params)
      except Exception, e:
        if self.logger:
          self.logger.exception(e)

class application_sites(list):

  def load_from_json(self, json_data):
    for site in json_data:
      self.append(site['name'])

  def __dict__(self):
    sites_dict = []
    for rec in self:
      sites_dict.append({'name': rec})
    return sites_dict

class application_sites_web_collector(web_data_collector):
  def __init__(self, url, params, logger_name):
    web_data_collector.__init__(self, url, params, logger_name)
    self.sites = application_sites()

  def scrape_page(self, page):
    soup = BeautifulSoup(page)

    pages = soup.find('input', type='Submit', value="  >   ")

    #Aplpication sites page is a single column table.
    #Find the table name Site Name, then get its parent.
    table = soup.find(text=re.compile("Site Name")).find_parent('table')
    #Find the table body, then iterate the rows.
    for row in table.find('tbody').find_all('tr'):
      #get all the coluns in the row, should only have one.
      col = row.find_all('td')
      name = col[0].text.strip()
      try:
        matched = re.search(name, "(\[\d+\/\d+\])")
      except Exception,e:
        if self.logger:
          self.logger.error("%s caused RegEx error when search for [PageNum/PageCnt]" % (name))
        matched = None
      if matched is None:
        self.sites.append(name)
    web_data_collector.page_results(self, pages)



class active_ingredient_search(web_data_collector):
  def __init__(self, url, params, logger_name):
    web_data_collector.__init__(self, url, params, logger_name)
    self.ingredients = []

  def scrape_page(self, page):
    soup = BeautifulSoup(page)

    pages = soup.find('input', type='Submit', value="  >   ")

    #Find the Chemical Name string then get the parent table.
    table = soup.find('table', border=1).find(text=re.compile("Chemical Name")).find_parent('table')
    #Find the table body, then iterate the rows.
    for row in table.find('tbody').find_all('tr'):
      #get all the coluns in the row, should only have one.
      """
      <td><a href="showproductsbychem.asp?PC_Code=080803&amp;PctStart=0&amp;PctEnd=100&amp;Chemical_Name=Atrazine">
      Atrazine
        </a></td>
      """
      col = row.find_all('td')
      tag = col[0].find('a')
      name = tag.text.strip()
      url = ""
      if 'href' in tag.attrs:
        url = tag.attrs['href'].strip()
      try:
        matched = re.search(name, "(\[\d+\/\d+\])")
      except Exception,e:
        if self.logger:
          self.logger.error("%s caused RegEx error when search for [PageNum/PageCnt]" % (name))
        matched = None

      if matched is None:
        self.ingredients.append({'name': name, 'url': url})

    web_data_collector.page_results(self, pages)

class ingredient(object):
  def __init__(self):
    self.active_ingredient = None
    self.percentage_active_ingredient = None
  def __dict__(self):
    ingr = {'active_ingredient': self.active_ingredient,
            'percentage_active_ingredient': self.percentage_active_ingredient}
    return ingr

class active_ingredients(list):
  def add(self, **kwargs):
    ingr = ingredient()
    ingr.active_ingredient = kwargs['ingredient']
    ingr.percentage_active_ingredient = kwargs['percentage']
    self.append(ingr)

  def load_from_json(self, json_data):
    for ingr in json_data:
      active_ingr = ingredient()
      active_ingr.active_ingredient = ingr['active_ingredient']
      active_ingr.percentage_active_ingredient = ingr['percentage_active_ingredient']
      self.append(active_ingr)

  def __dict__(self):
    ingrs = []
    for rec in self:
      ingrs.append(rec.__dict__())
    return ingrs

class active_ingredients_web_collector(web_data_collector):
  def __init__(self, url, params, logger_name):
    web_data_collector.__init__(self, url, params, logger_name)
    self.ingredients = active_ingredients()

  def scrape_page(self, page):
    soup = BeautifulSoup(page)

    pages = soup.find('input', type='Submit', value="  >   ")


    #Find the Chemical Name string then get the parent table.
    table = soup.find(text=re.compile("Chemical Name")).find_parent('table')
    #Find the table body, then iterate the rows.
    for row in table.find('tbody').find_all('tr'):
      #get all the coluns in the row, should only have one.
      col = row.find_all('td')

      try:
        matched = re.search(active_in.ingredient, "(\[\d+\/\d+\])")
      except Exception,e:
        if self.logger:
          self.logger.error("%s caused RegEx error when search for [PageNum/PageCnt]" % (col[0].text.strip()))
        matched = None
      if matched is None:
        self.ingredients.add( ingredient = col[0].text.strip(), percentage = col[1].text.strip())

    web_data_collector.page_results(self, pages)

class Pest(object):
  def __init__(self):
    self.name = None
    self.display_name = None
    self.image_url = None


  def __dict__(self):
    pest =  {'name': self.name,
            'display_name': self.display_name,
            'image_url': self.image_url}
    if pest['display_name'] is None:
      pest['display_name'] = self.name
    return pest
class Pests(list):
  def add(self, **kwargs):
    pest = Pest()
    pest.name = kwargs['name']
    self.append(pest)

  def load_from_json(self, json_data):
    for pest in json_data:
      pest_obj = Pest()
      pest_obj.name=pest['name']
      if pest['name'].find("ErrorResult"):
        pest['name'] = "Unknown"
      pest_obj.display_name=pest['display_name']
      if pest_obj.display_name is None:
        pest_obj.display_name = pest_obj.name
      pest_obj.image_url=pest['image_url']
      self.append(pest_obj)

  def __dict__(self):
    pest_list = []
    for rec in self:
      pest_list.append(rec.__dict__())
    return pest_list

class pests_treated_web_collector(web_data_collector):
  def __init__(self, url, params, logger_name):
    web_data_collector.__init__(self, url, params, logger_name)
    self.pests = Pests()

  def scrape_page(self, page):
    soup = BeautifulSoup(page)
    #Determine if we have multiple pages of pests.
    pages = soup.find('input', type='Submit', value="  >   ")

    #Find the Pest Name string then get the parent table.
    table = soup.find(text=re.compile("Pest Name")).find_parent('table')
    #Find the table body, then iterate the rows.
    rows = table.find('tbody').find_all('tr')
    for ndx, tag in enumerate(rows):
      #get all the coluns in the row, should only have one.
      col = tag.find_all('td')
      val = col[0].text.strip()
      #For results that have multiple pages, the page number page count is
      #formatted like "[1/4]" so we search the values to see if me match
      #that pattern, if we do, we don't add it.
      try:
        matched = re.search(val, "(\[\d+\/\d+\])")
      except Exception,e:
        if self.logger:
          self.logger.error("%s caused RegEx error when search for [PageNum/PageCnt]" % (val))
        matched = None

      if matched is None:
        self.pests.add(name=col[0].text.strip())

    web_data_collector.page_results(self, pages)


class product(object):
  def __init__(self):
    self.name = None
    self.label_url = None
    self.epa_registration_number = None
    self.registration_status = None
    self.restricted_use = None
    self.special_local_need = None
    self.experimental_use = None

    self.company_name = None
    self.company_number = None
    self.pesticide_type = None
    self.active_ingredients = None
    self.application_areas = None
    self.pests_treated = None

    self.formulation = None

    self.name = None
    self.sln = None
    self.registration_status = None
    self.percent = None

    self.active_ingredients_url = None
    self.application_sites_url = None
    self.pests_url = None

  def load_from_json(self, json_data):
    self.name = json_data['name']
    self.label_url = json_data['label_url']
    self.restricted_use = json_data['restricted_use']
    self.experimental_use = json_data['experimental_use']
    self.special_local_need = json_data['special_local_need']
    if json_data['special_local_need'] == "No":
      self.special_local_need = False
    elif json_data['special_local_need'] == "yes":
      self.special_local_need = True

    self.formulation = json_data['formulation']
    self.epa_registration_number = json_data['epa_registration_number']
    self.company_name = json_data['company_name']
    self.company_number =json_data['company_number']
    self.pesticide_type =json_data['pesticide_type']

    self.pests_treated = Pests()
    self.pests_treated.load_from_json(json_data["pests_treated"])
    self.active_ingredients = active_ingredients()
    self.active_ingredients.load_from_json(json_data["active_ingredients"])
    self.application_areas = application_sites()
    self.application_areas.load_from_json(json_data["application_areas"])

  def __dict__(self):
    ais = []
    if self.active_ingredients:
      ais = [rec.__dict__() for rec in self.active_ingredients]
    if self.pests_treated.__dict__():
      pest_list = self.pests_treated.__dict__()
    if self.application_areas.__dict__():
      application_areas = self.application_areas.__dict__()
    prod = {'name' : self.name,
            'label_url': self.label_url,
            'restricted_use' : self.restricted_use,
            'experimental_use': self.experimental_use,
            'special_local_need': self.special_local_need,
            'formulation': self.formulation,
            'epa_registration_number' : self.epa_registration_number,
            'company_name': self.company_name,
            'company_number': self.company_number,
            'pesticide_type': self.pesticide_type,
            'active_ingredients': ais,
            'pests_treated': pest_list,
            'application_areas': application_areas
            }
    return prod

class product_web_collector(web_data_collector):
  def __init__(self, url, params, logger_name):
    web_data_collector.__init__(self, url, params, logger_name)

    self.prod = product()


  def scrape_page(self, page):
    soup = BeautifulSoup(page)
    #On page example
    """
    <p style="margin: 0">
    <b>Company Name and Reg. No.:</b> <a href="showcoinfo.asp?Company_Name=CHEMSICO&amp;EPA_Id=9688">CHEMSICO</a>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
    [9688]
      </p>
    """
    tag = soup.find(text=re.compile('Company Name and Reg. No.:'))
    if tag:
      tag = tag.find_parent().find_next_sibling()
      self.prod.company_name = tag.text.strip()
      if tag.next_sibling:
        self.prod.company_number = int(unicode(tag.next_sibling).strip().replace('[', '').replace(']', ''))

    """
    <p style="margin: 0">
    <b>Formulation:&nbsp;&nbsp;</b>Granular<b>&nbsp;</b>&nbsp;&nbsp;&nbsp;
    </p>
    """
    tag = soup.find(text=re.compile("Restricted Use\?"))
    if tag:
      tag = tag.find_parent()
      if tag.next_sibling:
        val = unicode(tag.next_sibling).strip()
        self.prod.restricted_use = False
        if val.lower() == 'yes':
          self.prod.restricted_use = True

    tag = soup.find(text=re.compile("Experimental Use\?"))
    if tag:
      tag = tag.find_parent()
      if tag.next_sibling:
        val = unicode(tag.next_sibling).strip()
        self.prod.experimental_use = False
        if val.lower() == 'yes':
          self.prod.experimental_use = True

    tag = soup.find(text=re.compile("Special Local Need \(SLN\)\?"))
    if tag:
      tag = tag.find_parent()
      if tag.next_sibling:
        self.prod.special_local_need = False
        if val.lower() == 'yes':
          self.prod.special_local_need = True


    tag = soup.find(text=re.compile('Formulation:'))
    if tag:
      tag = tag.find_parent()
      if tag.next_sibling:
        self.prod.formulation = unicode(tag.next_sibling).strip()
    """
    <p style="margin: 0">
    <b>Pesticide Type:&nbsp;&nbsp;</b>
    Herbicide Terrestrial
      <b>&nbsp;</b>&nbsp;&nbsp;&nbsp;
      </p>
    """
    tag = soup.find(text=re.compile('Pesticide Type:'))
    if tag:
      tag = tag.find_parent()
      if tag.next_sibling:
        self.prod.pesticide_type = unicode(tag.next_sibling).strip()
    """
    Click here to <a href="http://www.kellysolutions.com/erenewals/documentsubmit/KellyData\SC\pesticide\Product%20Label\9688\2217%2D819%2D9688\2217%2D819%2D9688%5FACE%5FGREEN%5FTURF%5FPHOSPHORUS%5FFREE%5FWEED%5F%5F%5FFEED%5F29%5F0%5F3%5F9%5F21%5F2010%5F11%5F26%5F02%5FAM%2Epdf" target="_blank">View  Product Label
    </a> <font size=2>(revision date: 9/21/2010 11:26:02 AM)</font><br>
    """
    #Look for one or more spaces between words since at least the page I am testing on
    #has View  Product Label
    tag = soup.find(text=re.compile("View\s+Product\s+Label"))
    if tag:
      tag = tag.find_parent()
      if 'href' in tag.attrs:
        self.prod.label_url = tag.attrs['href'].strip()

    tag = soup.find(text=re.compile("Active\s+Ingredients"))
    if tag:
      tag = tag.find_parent()
      if 'href' in tag.attrs:
        self.prod.active_ingredients_url = tag.attrs['href'].strip()

    tag = soup.find(text=re.compile("Pests\s+Controlled\s+by\s+this\s+Product"))
    if tag:
      tag = tag.find_parent()
      if 'href' in tag.attrs:
        self.prod.pests_url = tag.attrs['href'].strip()

    tag = soup.find(text=re.compile("Sites\s+to\s+which\s+this\s+Product\s+may\s+be\s+Applied"))
    if tag:
      tag = tag.find_parent()
      if 'href' in tag.attrs:
        self.prod.application_sites_url = tag.attrs['href'].strip()


class products_web_collector(web_data_collector):
  def __init__(self, url, params, logger_name):
    web_data_collector.__init__(self, url, params, logger_name)
    self.products = []

  def scrape_page(self, page):
    soup = BeautifulSoup(page)

    #For some unknown reason when querying the brands/products page we get back
    #duplicate rows in the table listing. Use this dict to skip ones we already
    #have processed.
    names = []
    pages = soup.find('input', type='Submit', value="  >   ")

    table = soup.find(text=re.compile("Product Name")).find_parent('table')

    for row in table.find('tbody').find_all('tr'):
      try:
        col = row.find_all('td')
        #Have we already processed the product?
        if col[0].text.strip() not in names:
          names.append(col[0].text.strip())
          prod = product_web_collector(None, None, None)
          href = col[0].find('a')
          prod.prod.name = href.contents[0].strip()
          if 'href' in href.attrs:
            prod.prod.url = href.attrs['href']
          prod.prod.epa_registration_number = col[1].string.strip()
          prod.prod.special_local_need = col[2].string.strip()
          prod.prod.registration_status = col[3].string.strip()
          prod.prod.percent = col[4].string.strip()

          #For results that have multiple pages, the page number page count is
          #formatted like "[1/4]" so we search the values to see if me match
          #that pattern, if we do, we don't add it.
          try:
            matched = re.search(col[0].text.strip(), "(\[\d+\/\d+\])")
          except Exception,e:
            if self.logger:
              self.logger.error("%s caused RegEx error when search for [PageNum/PageCnt]" % (col[0].text.strip()))
            matched = None
          if matched is None:
            self.products.append(prod)


      except Exception,e:
        if self.logger:
          self.logger.exception(e)

    web_data_collector.page_results(self, pages)

class csv_data_collector(object):
  def __init__(self, logger_name):
    self.file_obj = None
    self.filename = None
    self.csv_reader = None
    self.logger = None
    if logger_name:
      self.logger = logging.getLogger(logger_name)

  def open(self, datafile, headers):
    self.filename = datafile
    try:
      if self.logger:
        self.logger.debug("Opening file: %s" % (datafile))
      self.file_obj = open(self.filename, "r")
      self.csv_reader = csv.DictReader(self.file_obj, headers)
      return True
    except Exception,e:
      if self.logger:
        self.logger.exception(e)
    except IOError, e:
      if self.logger:
        self.logger.exception(e)
    return False

  def __del__(self):
    if self.file_obj:
      self.file_obj.close()


class products_csv_collector(object):
  def __init__(self, logger_name, **kwargs):
    if logger_name:
      self.logger = logging.getLogger(logger_name)

    self.products = []
    self.pesticide_types_dict = {
    "01": "Chemosterilant",
    "02": "Poison, Multiple Dose",
    "03": "Poison, Single Dose",
    "04": "Repellent",
    "05": "Acaricide",
    "06": "Antibiotic",
    "07": "Antimicrobial",
    "09": "Attractant",
    "10": "Avicide",
    "11": "Biocide",
    "12": "Emulsifier",
    "13": "Feeding Depressant",
    "14": "Fertilizer",
    "15": "Fire Retardant",
    "16": "Intrastate",
    "17": "Tuberculocide",
    "18": "Sterilizer",
    "19": "Sporicide",
    "20": "Disinfectant",
    "21": "Sanitizer",
    "22": "Bacteriostat",
    "23": "Water Purifier Bacteriostat",
    "24": "Microbicide ",
    "25": "Microbistat ",
    "26": "Fungistat",
    "27": "Fungicide",
    "28": "Nematicide",
    "29": "Fumigant",
    "30": "Industrial Chemical",
    "31": "Bacteriocide",
    "32": "Insect Growth Regulator",
    "33": "Insecticide Synergist ",
    "34": "Herbicide",
    "35": "Algicide",
    "36": "Defoliant",
    "37": "Desiccant",
    "38": "Antifoulant",
    "39": "Herbicide Terrestria",
    "40": "Herbicide Aquatic",
    "41": "Slimacide",
    "42": "Biochemical Pesticide",
    "43": "Insecticide",
    "44": "Miticide",
    "45": "Tadpole Shrimpicide",
    "46": "Molluscicide",
    "47": "Feeding Stimulant",
    "48": "Mating Disruptant",
    "49": "Plant Growth Regulator",
    "50": "Sex Attractant",
    "51": "Mechanical ",
    "52": "Microbial Pesticide",
    "53": "Plant Growth Stimulator",
    "54": "Rodenticide",
    "55": "Soil Fumigant",
    "56": "Termiticide",
    "57": "Repellent Or Feeding Depressant",
    "58": "Sex Attractant Or Feeding Stimulant",
    "59": "Algaecide",
    "60": "Bacteriocide/bacteriostat",
    "61": "Molluscicide And Tadpole Shrimp",
    "62": "Microbicide/microbistat",
    "63": "Fungicide/fungistat",
    "64": "Regulator",
    "65": "Virucide",
    "66": "Nonviable Microbial/transgenic Plant",
    "67": "Fungicide And Nematicide",
    "68": "Antifouling",
    "69": "Water Purifier Bacteriastatic",
    "70": "Slimacides",
    "71": "Water Purifier Bacteriacidal",
    "72": "Medical Waste Treatment",
    "73": "Contraceptive" }

    self.products_datafile = kwargs["products_datafile"]
    self.products_header = kwargs["product_header"]
    self.pests_datafile = kwargs["pests_datafile"]
    self.pest_header = kwargs["pest_header"]
    self.sites_datafile = kwargs["sites_datafile"]
    self.site_header = kwargs["site_header"]
    self.labels_datafile = kwargs["labels_datafile"]
    self.label_header = kwargs["label_header"]

  def get_data(self, **kwargs):
    try:
      if self.logger:
        self.logger.debug("Opening file: %s" % (self.products_datafile))
      products_file_obj = open(self.products_datafile, "r")
      products_csv_reader = csv.DictReader(products_file_obj, self.products_header)
    except IOError, e:
      if self.logger:
        self.logger.exception(e)
    else:
      ai_name = kwargs['active_ingredient']
      if self.logger:
        self.logger.debug("AI: %s searching for products" % (ai_name))
      row_num = 0
      for row in products_csv_reader:
        if row_num > 0:
          if row["Chemical_Name"] == ai_name:
            prod = product()
            prod.name = row["product_name"]
            prod.epa_registration_number = row["epa_id"]
            prod.company_name = row["company_name"]
            prod.company_number = row["Company_EPA_Id"]
            types = row['Type'].split(',')
            p_types = [self.pesticide_types_dict[type] for type in types]
            prod.pesticide_type = ",".join(p_types)
            prod.special_local_need = row["SLN"]

            prod.pests_treated = self.get_pests(prod.name)
            if self.logger:
              self.logger.debug("%s Product: %s %d pests treated" % (ai_name, prod.name, len(prod.pests_treated)))

            prod.application_areas = self.get_sites(prod.name)
            if self.logger:
              self.logger.debug("%s Product: %s %d sites" % (ai_name, prod.name, len(prod.application_areas)))

            self.products.append(prod)
        row_num += 1
      products_file_obj.close()
      return

  def get_pests(self, product_name):
    pests_treated = Pests()
    try:
      if self.logger:
        self.logger.debug("Opening file: %s" % (self.pests_datafile))
      pests_file_obj = open(self.pests_datafile, "r")
      pests_csv_reader = csv.DictReader(pests_file_obj, self.pest_header)
    except IOError, e:
      if self.logger:
        self.logger.exception(e)
    else:
      row_cnt = 0
      for row in pests_csv_reader:
        if row_cnt > 1:
          if row["product_name"] == product_name:
            pests_treated.add(name=row["Pest_Name"])
        row_cnt += 1
      pests_file_obj.close()

    return pests_treated

  def get_sites(self, product_name):
    sites_treated = application_sites()
    try:
      if self.logger:
        self.logger.debug("Opening file: %s" % (self.sites_datafile))
      file_obj = open(self.sites_datafile, "r")
      csv_reader = csv.DictReader(file_obj, self.site_header)
    except IOError, e:
      if self.logger:
        self.logger.exception(e)
    else:
      row_cnt = 0
      for row in csv_reader:
        if row_cnt > 1:
          if row["product_name"] == product_name:
            sites_treated.append(row["Site_Name"])
        row_cnt += 1
      file_obj.close()

    return sites_treated


class clemsonCSVWebData(object):
  def __init__(self, configFilename, logger_name=None):
    self.logger_name = logger_name
    if self.logger_name:
      self.logger = logging.getLogger(logger_name)

    self.configFile = ConfigParser.RawConfigParser()
    self.configFile.read(configFilename)

    self.product_header = [
      "product_name",
      "epa_id",
      "company_name",
      "Company_EPA_Id",
      "Active",
      "Type",
      "Pct",
      "Chemical_Name",
      "expiration_date",
      "Form_Code",
      "RUP",
      "SLN",
      "PC_Code",
      "Synonym",
      "Nametype"
    ]
    self.label_header = [
      "product_name",
      "epa_id",
      "status_date",
      "file_path"
    ]
    self.pest_header = [
      "product_name",
      "epa_id",
      "Pest_Name"
    ]
    self.site_header = [
      "product_name",
      "epa_id",
      "Site_Name"
    ]
    try:
      self.products_csv_url = self.configFile.get("csv_settings", "products_url")
      self.products_datafile = self.configFile.get("csv_settings", "products_file")
      self.pests_url = self.configFile.get("csv_settings", "pests_url")
      self.pests_datafile = self.configFile.get("csv_settings", "pests_file")
      self.sites_url = self.configFile.get("csv_settings", "sites_url")
      self.sites_datafile = self.configFile.get("csv_settings", "sites_file")
      self.labels_url = self.configFile.get("csv_settings", "labels_url")
      self.labels_datafile = self.configFile.get("csv_settings", "labels_file")
    except ConfigParser.Error, e:
      if self.logger:
        self.logger.exception(e)

  def searchByActiveIngredient(self, active_ingredient):
    if self.logger:
      self.logger.error("%s searching for active ingredient" % (active_ingredient))

    collector = products_csv_collector(self.logger_name,
                                       products_datafile=self.products_datafile,
                                       product_header=self.product_header,
                                       pests_datafile=self.pests_datafile,
                                       pest_header=self.pest_header,
                                       sites_datafile=self.sites_datafile,
                                       site_header=self.site_header,
                                       labels_datafile=self.labels_datafile,
                                       label_header=self.label_header)

    collector.get_data(active_ingredient=active_ingredient)

    if self.logger:
      self.logger.error("%s finished searching for active ingredient" % (active_ingredient))


class clemsonWebService(object):
  def __init__(self, configFilename, logger_name=None):
    try:
      self.logger_name = logger_name
      if(logger_name):
        self.logger = logging.getLogger(logger_name)

      self.configFile = ConfigParser.RawConfigParser()
      self.configFile.read(configFilename)
      self.baseURL = self.configFile.get('url', 'baseurl')
      self.jsonOutputDir = self.configFile.get('output', 'jsonoutdir')

      #URL and params for pest name search.
      pagename = self.configFile.get('searchbypest', 'pagename')
      self.searchByPestURLParams = self.configFile.get('searchbypest', 'params')
      self.searchByPestURL = self.baseURL + pagename

      #URL and params for active ingredient search.
      pagename = self.configFile.get('searchbyactive', 'pagename')
      self.searchByActiveURLParams = self.configFile.get('searchbyactive', 'params')
      self.searchByActiveURL = self.baseURL + pagename
    except Exception, e:
      if self.logger:
        self.logger.exception(e)

  def getUrlAndParams(self, baseUrl):
    parts = urlparse(baseUrl)
    params = parse_qs(parts.query)
    url = "%s://%s%s" % (parts.scheme, parts.netloc, parts.path)
    return (url,params)

  """
  Function: searchByActiveIngredient
  Purpose: Given the active ingredient, search for the brands of pesticide that uses the active ingredient.
    Then drill down into the brand retrieving the sites the product can be applied to, get the product label if
    there is one.
  Parameters:
    activeIngredient - String with the name of the active ingredient to lookup.
  Return:
    A List with each entry being a dictionary of brand information. Each dictionary has a 'brandName', 'brandInfo' entry.
    The 'brandInfo' has a 'labelLink' which is the url to the products label, if there is one, then a List, 'siteList' the 
    product can be applied to.
  """
  def searchByActiveIngredient(self, activeIngredient):
    activeIngredientInfo = None    
    if(self.logger):
      self.logger.info("AI: %s Attempting to request active ingredient data" %(activeIngredient))

    ai_search = active_ingredient_search(self.searchByActiveURL, {self.searchByActiveURLParams : activeIngredient}, self.logger_name)
    if(ai_search.sendRequest()):
      if self.logger:
        self.logger.debug("AI: %s search returned: %d matches." % (activeIngredient, len(ai_search.ingredients)))
      for active_i in ai_search.ingredients:
        #Verify the active ingredient is an exact match for now.
        foundIngredient = False
        if activeIngredient.lower() == active_i['name'].lower():
          try:
            filename = "%s/%s.json" % (self.jsonOutputDir, activeIngredient)
            outfile = open(filename, "w")
          except IOError,e:
            if self.logger:
              self.logger.exception(e)
          foundIngredient = True
          if self.logger:
            self.logger.debug("%s Active Ingredient match found." % (activeIngredient))
          brandList = self.getBrandsForIngredient(active_i['url'], activeIngredient)
          if self.logger:
            self.logger.debug("%s has %d brands" % (activeIngredient, len(brandList.products)))
          outfile.write("{\n\"%s\":\n[\n" % (activeIngredient))
          for ndx,brand in enumerate(brandList.products):
            self.getBrandInformation(brand, activeIngredient)
            outfile.write(json.dumps(brand.prod.__dict__(), sort_keys=True, indent=2 * ' '))
            if ndx < len(brandList.products) - 1:
              outfile.write(',')
          outfile.write(']\n}')
          outfile.close()
          break
        if foundIngredient == False and self.logger:
          self.logger.error("AI: %s No match found for active ingredient: %s" % (activeIngredient, active_i['name']))
    
    else:
      if(self.logger):
        self.logger.error("AI: %s Failed to retrieve the active ingredient" % (activeIngredient))
            
    return(activeIngredientInfo)
  
  """
  Function: getBrandsForIngredient
  Purpose: Does a web request for the parameter, brandLookupURL, to retrieve a List of brand names as well as a link to 
    further product information.
  Parameter:
    brandLookupURL - String with the relative URL plus POST parameters to request. We add this to the base URL to
      create the full query URL.
  Return: A List of dictionaries. Each dictionary contains 'brandName' which is a brand name of a product that 
    uses the particular active ingredient we've requested as well as a 'productInfoLink' which is a relative
    URL plus parameters that leads to a page with more information about this specific brand.
  """
  def getBrandsForIngredient(self, brandLookupURL, activeIngredient):
    if(self.logger):
      self.logger.info("AI: %s Querying to create Brand url." % (activeIngredient))

    url, params = self.getUrlAndParams(self.baseURL + brandLookupURL)
    brandList = products_web_collector(url, params, self.logger_name)
    parseResults = brandList.sendRequest()

    if parseResults and len(brandList.products):
      return brandList
    else:
      if self.logger:
        self.logger.error("AI: %s Failed to retrieve the brand list." % (activeIngredient))

    return(None)
  
  """
  FUnction: getBrandInformation
  Purpose: Give the parameter, brandInfoURL, scrapes the webpage retrieving items such as the product label if available
    as well as the sites the product can be applied to.
  Parameter:   
    brandInfoURL - A String representing the relative URL to do the web query.
  Return:
    A Dictionary with 'labelLink' entry that is the full URL to the product label, if available and 'siteList'
    which is a List of the areas the product may be applied.
  """
  def getBrandInformation(self, product_collector, activeIngredient):
    if(self.logger):
      self.logger.info("AI: %s Brand: %s querying brand information." % (activeIngredient, product_collector.prod.name))
    #parseResults = self.sendRequestBS(self.baseURL + product.url, None, product)
    url, params = self.getUrlAndParams(self.baseURL + product_collector.prod.url)
    product_collector.url = url
    product_collector.params = params
    if product_collector.sendRequest():
      #If there is a link for the site application, let's query that page and get the data.
      if product_collector.prod.application_sites_url:
        if self.logger:
          self.logger.info("AI: %s Brand: %s Querying for application sites." % (activeIngredient, product_collector.prod.name))
        url, params = self.getUrlAndParams(self.baseURL + product_collector.prod.application_sites_url)
        app_sites = application_sites_web_collector(url, params, self.logger_name)
        app_sites.sendRequest()
        product_collector.prod.application_areas = app_sites.sites
        if self.logger:
          self.logger.debug("AI: %s Brand: %s has %d application sites" % (activeIngredient,  product_collector.prod.name, len(app_sites.sites)))

      if product_collector.prod.active_ingredients_url:
        if self.logger:
          self.logger.info("AI: %s Brand: %s querying for active ingredients." % (activeIngredient, product_collector.prod.name))
        url, params = self.getUrlAndParams(self.baseURL + product_collector.prod.active_ingredients_url)
        ingredients = active_ingredients_web_collector(url, params, self.logger_name)
        if ingredients.sendRequest(url, params):
          product_collector.prod.active_ingredients = ingredients.ingredients
        else:
          if self.logger:
            self.logger.error("AI: %s Brand: %s no ingredients found." % (activeIngredient, product_collector.prod.name))

        if self.logger:
          self.logger.debug("AI: %s Brand: %s has %d active ingredients" % (activeIngredient, product_collector.prod.name, len(ingredients.ingredients)))

      if product_collector.prod.pests_url:
        if(self.logger):
          self.logger.info("AI: %s Brand: %s querying for pests treated." % (product_collector.prod.name, product_collector.prod.name))
        url, params = self.getUrlAndParams(self.baseURL + product_collector.prod.pests_url)
        pests = pests_treated_web_collector(url, params, self.logger_name)
        if pests.sendRequest():
          product_collector.prod.pests_treated = pests.pests
        else:
          if self.logger:
            self.logger.error("AI: %s Brand: %s no pests found" % (activeIngredient, product_collector.prod.name))
        if self.logger:
          self.logger.debug("AI: %s Brand: %s has %d pests treated" % (activeIngredient, product_collector.prod.name, len(pests.pests)))

    else:
      if(self.logger):
        self.logger.error("AI: %s Failed to retrieve the brand information page." % (activeIngredient))

    if(self.logger):
      self.logger.info("AI: %s finished querying brand information." % (activeIngredient))

  """
  Function: searchByPest
  Purpose: Given a pest name, use the web service to get a list of pests that have the search string in their.
    name. THe results are then linked to the brand name pesticides to control the pest.
  Parameters:
    pestName - List of strings, each with a pest name to search for.
  """
  def searchByPest(self, pestNames):

    if(self.logger):
      self.logger.debug("Attempting to request pest data for: %s" %(pestNames))
    for pest in pestNames:
      params = {self.searchByPestURLParams : pest}
      parseResults = self.sendRequest(self.pestSearchResults, self.searchByPestURL, params)
      if(parseResults):
        for pestData in parseResults['pestresults']:
          pesticideList = self.getPestcidesForPest(pestData['pestid'])
      else:
        if(self.logger):
          self.logger.error("Failed to retrieve the pest list.")
    return(False)

  """
  Function: getPestsForBrands
  Purpose: Query the pests the given brand treats.
  """
  def getPestsForBrands(self):
    if(hasattr(self, 'brandsSearchResults')):
      self.pesticideSearchResults = { 'pesticideresults' : {
        'pestsLink' : "//p/a/"
        }
      }
    parseResults = self.sendRequest(self.pesticideSearchResults, self.baseURL + pestLookupUrl, None)
    if(parseResults):
      for pesticideData in parseResults['pesticideSearchResults']:
        i=0
    else:
      if(self.logger):
        self.logger.error("Failed to retrieve the pest list.")
      
    return(False)
  
  def getPestcidesForPest(self, pestLookupUrl):    
    parseResults = self.sendRequest(self.pesticideSearchResults, self.baseURL + pestLookupUrl, None)
    if(parseResults):
      for pesticideData in parseResults['pesticideSearchResults']:
        i=0
    else:
      if(self.logger):
        self.logger.error("Failed to retrieve the pest list.")

    return(None)
    
