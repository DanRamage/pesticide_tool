ko.observableArray.fn.asDictionary = function (keyName) {
    return ko.computed(function () {
        var list = this() || [];    // the internal array
        var keys = {};              // a place for key/value
        ko.utils.arrayForEach(list, function (v) {
            if (keyName) {          // if there is a key
                keys[v[keyName]] = v;    // use it
            } else {
                keys[v] = v;
            }
        });
        return keys;
    }, this);
};

pagedObservableArray = function (options)
  {
    var self = this;
    options = options || {};
    if ($.isArray(options))
        options = { data: options };


    //the complete data collection
    self.allData = ko.observableArray(options.data || [])

    //the size of the pages to display
    self.pageSize = ko.observable(options.pageSize || 10)

    //the index of the current page
    self.pageIndex = ko.observable(0);

    //the current page data
    self.page = ko.computed(function () {
        var pageSize = self.pageSize(),
            pageIndex = self.pageIndex(),
            startIndex = pageSize * pageIndex,
            endIndex = pageSize * (pageIndex + 1);

        return self.allData().slice(startIndex, endIndex);
    },
    this,
    {deferEvaluation: true});

    //the number of pages
    self.pageCount = ko.computed(function () {
        return Math.ceil(self.allData().length / self.pageSize()) || 1;
    });

    //move to the next page
    self.nextPage = function () {
        if (self.pageIndex() < (self.pageCount() - 1))
            self.pageIndex(self.pageIndex() + 1);
    };

    //move to the previous page
    self.previousPage = function () {
        if (self.pageIndex() > 0)
            self.pageIndex(self.pageIndex() - 1);
    };

    //reset page index when page size changes
    self.pageSize.subscribe(function () { self.pageIndex(0); });
    self.allData.subscribe(function () { self.pageIndex(0); });


    return(self);
  };

function buttonModel(name, img)
{
  var self = this;
  self.name = ko.observable(name);
  self.img  = ko.observable(img);
  var href = name.replace(/ /g, '_');
  self.href = ko.observable(href);

  return self;
}
function categoryModel(name, config)
{
  var self = this;


  //self.buttonData = new buttonModel(name, config.button_img);
  self.name = ko.observable(name || "");
  self.img  = ko.observable((config ? config['image_url'] : ""));
  var href = null;
  if(name != null)
    href = name.replace(/ /g, '_');
  self.href = ko.observable(href || "");

  self.subCategories = [];

  //Build the subcategories.
  self.buildSubCategories = function(subCategories)
  {
    $.each(subCategories, function(ndx, subCategoryNfo)
    {
      var subCat = new subCategoryModel(subCategoryNfo['name'], subCategoryNfo);
      self.subCategories.push(subCat);
    });
  };

  return self;
}
function subCategoryModel(name, config)
{
  var self = this;
  //self.buttonData = new buttonModel(name, config.button_img);
  self.name = ko.observable(name || "");
  self.img  = ko.observable((config ? config['image_url'] : ""));
  var href = null;
  if(name != null)
    href = name.replace(/ /g, '_');
  self.href = ko.observable(href || "");

  self.pests = ko.observableArray([]);

  self.buildPests = function(pests)
  {
    //Empty the array if there are entries.
    if(self.pests().length)
    {
      self.pests().splice(0, self.pests().length);
    }
    $.each(pests, function(ndx, pest)
    {
      self.pests().push(new pestModel(pest));
    });
    self.pests().sort(function(rec1, rec2)
    {
      var name1 = rec1.name();
      var name2 = rec2.name();
      //var name1 = rec1.buttonData.name();
      //var name2 = rec2.buttonData.name();
      if (name1 < name2)
         return -1;
      if (name1 > name2)
        return 1;
      return 0;
    });
    var i = 0;
  };
}

function categoriesViewModel()
{
  var self = this;
  //Array to track which parts should be visible.
  self.visibleTracker = {
    'category': ko.observable(true),
    'sub_category': ko.observable(false),
    'pest': ko.observable(false)
  };

  self.categoryModels = ko.observableArray([]); //The major categories of pests.
  self.activeCategory = ko.observable(new categoryModel());
  self.activeSubCategory = ko.observable(new subCategoryModel());
  self.aisForPestPage = ko.observable('');
  self.currentUrl = ''

  self.initialize = function()
  {
    // Bind the url hash change event.
    $(window).bind('hashchange', self.hashchanged);

    //Query the server for the category data.
    var url = 'http://sccoastalpesticides.org/pesticide_tool/get_categories';
    $.getJSON(url,
        function(data)
        {
          $.each(data.categories, function(ndx, categoryNfo) {
            //Construct the categoryModel.
            var catModel = new categoryModel(categoryNfo['name'], categoryNfo);
            catModel.buildSubCategories(categoryNfo['sub_categories']);

            self.categoryModels.push(catModel);
          });

          //Setup hover event function for categories.
          $("[rel='tooltip']").tooltip();

          $('#hover-col .thumbnail').hover(
            function()
            {
              $(this).find('.caption').slideDown(250); //.fadeIn(250)
            },
            function()
            {
              $(this).find('.caption').slideUp(250); //.fadeOut(205)
            }
          );

          self.check_url();
        });
  };
  self.findByName = function(name, searchArray)
  {
    var retVal = null;
    ko.utils.arrayFirst(searchArray(), function(object)
    {
      if(object.href() === name)
      {
        retVal = object;
        return(true);
      }
    });
    return(retVal);
  };

  self.check_url = function()
  {
    var state = $.bbq.getState();

    //Look at the url to determine if we are on the category page or we're starting
    //on a specific subcategory.
    var url = decodeURIComponent($.param.fragment());
    //We're starting at a specific category, so let's update.
    if(url.length)
    {
      if(url !== self.currentUrl) {
        var cat = self.findByName(url, self.categoryModels);
        if(cat)
        {
          //Hide the categories button, then build the sub categories.
          self.setVisible('sub_category');
          self.activeCategory(cat);
          //Setup the hover functions for sub category buttons.
          $('#sub-hover-col .thumbnail').hover(
            function () {
              $(this).find('.caption').slideDown(250); //.fadeIn(250)
            },
            function () {
              $(this).find('.caption').slideUp(250); //.fadeOut(205)
            }
          );
        }
      }
    }
    //No subcategory or pest, so we're on the main category.
    else
    {
      self.setVisible('category');
    }
    self.currentUrl = url
  };
  self.setVisible = function(pageName)
  {
    $.each(self.visibleTracker, function(ndx, page)
    {
      if(ndx === pageName)
      {
        page(true);
      }
      else
      {
        page(false);
      }
    });
  }
  self.categoryClicked = function(category, event)
  {
    //Hide the categories button, then build the sub categories.
    self.setVisible('sub_category');
    var hash = encodeURIComponent(category.href());
    var frag = $.param.fragment('', '#' + hash, 2);
    $.bbq.pushState(frag);

    self.activeCategory(category);
    //Setup the hover functions for sub category buttons.
    $('#sub-hover-col .thumbnail').hover(
      function()
      {
        $(this).find('.caption').slideDown(250); //.fadeIn(250)
      },
      function()
      {
        $(this).find('.caption').slideUp(250); //.fadeOut(205)
      }
    );

    return;
  };
  self.subCategoryClicked = function(subCategory, event)
  {

    //Get current hash which should represent the category.
    var url = $.param.fragment();

    var hash = url + '/' + encodeURIComponent(subCategory.href());
    var frag = $.param.fragment('', '#' + hash, 2);
    $.bbq.pushState(frag);
    if( subCategory.pests().length == 0)
    {
      var url = 'http://sccoastalpesticides.org/pesticide_tool/get_pests_for_subcategory';
      $.getJSON(url,
        {'sub_category': subCategory.name()},
        function (data) {
          subCategory.buildPests(data.pests);
          self.activeSubCategory(subCategory);
          self.setVisible('pest');
          //Setup the hover functions for sub category buttons.
          $('#pests-hover-col .thumbnail').hover(
            function()
            {
              $(this).find('.caption').slideDown(250); //.fadeIn(250)
            },
            function()
            {
              $(this).find('.caption').slideUp(250); //.fadeOut(205)
            }
          );
        }
      );
    }
    else
    {
      self.activeSubCategory(subCategory);
      self.setVisible('pest');
    }
    return;
  };
  self.pestTypeClicked = function(pest, event)
  {
    var url = 'pest_ai_page?pest_name=' + encodeURIComponent(pest.name());
    self.aisForPestPage(url);
    return(true);
    /*
    self.setVisible('pest')
    //Get current hash which should represent the category.
    var url = $.param.fragment();
    var hash = url + '/' + encodeURIComponent(pest.href());
    var frag = $.param.fragment('', '#' + hash, 2);
    $.bbq.pushState(frag);

    url = 'http://sccoastalpesticides.org/pesticide_tool/get_ai_for_pest';
    $.getJSON(url,
      {
        'pest': pest.name()
      },
      function(data) {
      }
    );
    */
  }
  self.hashchanged = function(event)
  {
    //Force the page to the top whenever we change pages since most are long lists of pics.
    //If we don't do this, when using the back key the previous page will pick up where we left
    //the currect page.
    $('body').scrollTop(0);
    self.check_url();
  }

}

function activeIngredientsForPestViewModel()
{
  var self = this;

  self.pest_name = ko.observable('');
  self.ai_results = ko.observableArray([]);
  self.initialize = function()
  {
    //Get url parameters so we can see what the pest name is.
    var pest_url = $.deparam.querystring();
    self.pest_name(pest_url.pest_name);
    url = 'http://sccoastalpesticides.org/pesticide_tool/get_ai_for_pest';
    $.getJSON(url,
      {
        'pest': pest_url.pest_name
      },
      function(data) {
        self.ai_results(data.ai_list);
      }
    );


  }
}

function pestModel(config)
{
  var self = this;
  ko.utils.extend(self, new buttonModel(config['display_name'], config['image_url']));

  //self.buttonData = new buttonModel(config['display_name'], config['image_url']);

  return self;
}

function modelContainer(modelName, templateId, configData)
{
  this.key = key;
  this.template = ko.observable(template);
  this.data = data;
}

function pestSearchResultModel(config)
{
  var self = this;

  ko.mapping.fromJS(config, {}, self);


}

function selectionViewModel(config)
{
  var self = this;

  self.layoutMapping = null;
  self.models = ko.observableArray([]);         //The container for all the view models on the page: Category, Sub Category, Pests, Results.

  self.categoryModels = ko.observableArray([]); //The major categories of pests.
  self.subCategory = ko.observableArray([]);    //Inside a category, these are the pest types;
  self.activeCategory = ko.observable();    //The active major category name.
  self.activeCategoryName = ko.observable();    //The active major category name.
  self.activeSubCategoryName = ko.observable();    //The active sub category name.
  self.activePestName = ko.observable();        //The specific pest name.
  self.pestList = ko.observableArray([]);       //The list of pest types chosen from selecting a subcategory.

  self.pesticideSearchRec = ko.observableArray([]);
  self.brandsForSelectedIngredient = ko.observableArray([]);
  self.searching = ko.observable(false);
  //self.pestListPaged = null;

  //Called before the specific category page gets loaded. Use this to scan the href to figure out which category
  //is being requested.
  self.setCategory = function(pageObj)
  {
    var page = pageObj.page;
    //Empty the previous selection.
    self.subCategory.removeAll();
    //Reset the active category name.
    self.activeCategoryName('');
    if(page.currentId === 'pest_subcategory')
    {
      var subCategoryName = page.route[0];
      $.each(self.categoryModels(), function(ndx, category)
        {
          if(category.href() === subCategoryName)
          {
            self.activeCategory(category);
            self.activeCategoryName(category.name());
            $.each(category.subCategories, function(ndx, subCategory)
              {
                self.subCategory.push(subCategory);
              });

            return(false);
          }
        });

    }
  };
  self.pestTypeButtonClick = function(subCategoryName, toUrl)
  {
    // Deactivate the pest_type section.
    $('#pest_subcategory').removeClass();

    //Set the selected sub category name, then loop through to find the subcategory so we can get the pest list.
    self.activeSubCategoryName(subCategoryName);
    $.each(self.subCategory(), function(ndx, subCategory)
      {
        if(subCategory.name() === subCategoryName)
        {
          self.pestList(subCategory.pests);
          return(false);
        }
      });
    // Activate the pest_selected section where we'll populate the query results.
    $('#pest_type').addClass('active');
    //Change the URL.
    window.location.href = toUrl;
  };

  self.pestButtonClick = function(pestName, toUrl)
  {
    self.activePestName(pestName);
    // Deactivate the pest_type section.
    $('#pest_type').removeClass();
    // Activate the pest_selected section where we'll populate the query results.
    $('#pest_selected').addClass('active');
    //Change the URL.
    window.location.href = toUrl;
    var searchType = 'pest';
    var pestType = self.activeCategoryName();
    var pestName = pestName;

    self.pesticideSearchRec([]);

    self.searching(true);

    $.ajax({
        url: app.pestDataQueryUrl,
        dataType: 'json',
        data : {'name' : pestName, 'searchtype' : 'pest', 'pesttype' : pestType},
        success: function(result)
        {
          self.searching(false);
          self.pesticideSearchRec(result.data);
        },
        error: function(result)
        {
          self.searching(false);
        }
    });
  };
  self.setActiveIngredient = function(activeIngredient)
  {
    //Clear the observable of the previous data.
    self.brandsForSelectedIngredient([]);
    //Given the active ingredient name parameter, find it in the pesticide search data.
    $.each(self.pesticideSearchRec(), function(ndx, pesticideRec)
    {
      if(pesticideRec['name'] === activeIngredient['name'])
      {
        self.brandsForSelectedIngredient(pesticideRec['brandList']);
        return(false);
      }
    });
    return(true);
  };

  self.getHazardColor = function(hazardLevel)
  {
    var colorCls = '.hazard_likely';
    if(hazardLevel === 'low')
    {
      colorCls = '.hazard_low';
    }
    else if(hazardLevel === 'moderate')
    {
      colorCls = '.hazard_moderate';
    }
    return(colorCls);
  }
  self.loadConfigurationData = function(data)
  {

    //self.layoutMapping = ko.mapping.fromJS(data.layout);

    $.each(data.layout.pest_categories, function(categoryName, categoryNfo) {
      //Construct the categoryModel.
      var catModel = new categoryModel(categoryName, categoryNfo);
      catModel.buildSubCategories(categoryNfo['sub_category'])

      self.categoryModels.push(catModel);
    });

    //Got the initialization data now initialize the page bindings.
    app.initPage();

    return(true);
  };

  /*
  self.dumpContext = ko.computed(function()
    {
      return(JSON.stringify(ko.toJS(self), null, 2));
    }
    );
  */
  //Click handler when someone chooses the type of pest they want to drill down into.
  //We load up the sub categories of the selection for the page.
  self.activateCategory = function(category)
  {
    //Empty the previous selection.
    app.viewModel.subCategory.removeAll();
    //Clear out the current categories for the new selection.
    app.viewModel.activeCategory(category);
    $.each(category.subCategories, function(ndx, subCategory)
      {
        app.viewModel.subCategory.push(subCategory);
      });
    //For the pager.js paging to work properly, this function needs to return true. It's the click event handler.
    return(true);
  };

  return self;
}



//app.viewModel = new selectionViewModel();
