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
var spinner_opts = {
  lines: 13, // The number of lines to draw
  length: 37, // The length of each line
  width: 10, // The line thickness
  radius: 26, // The radius of the inner circle
  corners: 1, // Corner roundness (0..1)
  rotate: 0, // The rotation offset
  direction: 1, // 1: clockwise, -1: counterclockwise
  color: '#000', // #rgb or #rrggbb or array of colors
  speed: 0.8, // Rounds per second
  trail: 60, // Afterglow percentage
  shadow: false, // Whether to render a shadow
  hwaccel: false, // Whether to use hardware acceleration
  className: 'spinner', // The CSS class to assign to the spinner
  zIndex: 2e9, // The z-index (defaults to 2000000000)
  top: '50%', // Top position relative to parent
  left: '50%' // Left position relative to parent
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
  };
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

    //Create and show out loading indicator in the button.
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
          //ladda_loading.stop();
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

    //Array to track which parts should be visible.
  self.visibleTracker = {
    'active_ingredients': ko.observable(true),
    'brands': ko.observable(false),
    'brand_info': ko.observable(false)
  };
  self.showSpinner = ko.observable(false);
  self.pest_name = ko.observable('');
  self.ai_results = ko.observableArray([]);
  self.activeAI = ko.observable();
  self.activeBrands = ko.observableArray([]);
  self.activeBrand = ko.observableArray([]);
  self.listName = ko.observable("");
  self.activeList = ko.observableArray([]);
  self.spinner = null;

  self.initialize = function()
  {
    self.showSpinner(true);
    var target = document.getElementById('spinner');
    self.spinner = new Spinner(spinner_opts).spin(target);

    //Get url parameters so we can see what the pest name is.
    var pest_url = $.deparam.querystring();

    self.pest_name(pest_url.pest_name);
    url = 'http://sccoastalpesticides.org/pesticide_tool/get_ai_for_pest';
    $.getJSON(url,
      {
        'pest': pest_url.pest_name
      },
      function(data) {
        self.spinner.stop();
        self.showSpinner(false);
        self.ai_results(data.ai_list);
        $('[data-toggle="popover"]').popover({
          trigger: 'hover',
          'placement': 'top'
        });
      }
    );
  };
  self.hashchanged = function(event)
  {
    //Force the page to the top whenever we change pages since most are long lists of pics.
    //If we don't do this, when using the back key the previous page will pick up where we left
    //the currect page.
    $('body').scrollTop(0);
    self.check_url();
  };
  self.check_url = function()
  {
    var state = $.bbq.getState();
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
  };

  self.getPanelClass = function(hazard_level)
  {
    var css = "panel panel-default";
    if(hazard_level !== undefined)
    {
      var lc_level = hazard_level.toLowerCase();
      if (lc_level == 'low') {
        css = "panel panel-success";
      }
      else if (lc_level == 'moderate') {
        css = "panel panel-warning";
      }
      else if (lc_level == 'likely') {
        css = "panel panel-danger";
      }
    }
    return(css);
  };
  self.showProducts = function(ai, event)
  {
    self.setVisible('brands');
    self.activeAI(ai.display_name);
    //Empty the curent brands.
    self.activeBrands([]);
    //ADd the brands from the selected AI.
    if(ai.brands.length)
    {
      var sorted_brands = ai.brands.sort();
      self.activeBrands(sorted_brands);
    }
    return(true);
  };
  self.showBrandInfo = function(brand, event)
  {
    self.setVisible('brand_info');

    self.activeBrand([]);
    var target = document.getElementById('brand_nfo_spinner');
    self.spinner.spin(target);

    var url = 'http://sccoastalpesticides.org/pesticide_tool/get_info_for_brand';
    $.getJSON(url,
      {
        'brand': brand.name
      },
      function(data) {
        self.spinner.stop();
        self.activeBrand([data.brand_info]);
      }
    );

    self.showApplicationAreas = function(brand_nfo, event)
    {
      self.listName("Application Areas");
      self.activeList(brand_nfo.application_areas);
    };
    self.showPestsTreated = function(brand_nfo, event)
    {
      self.listName("Pests Treated");
      self.activeList(brand_nfo.pests_treated);
    };

    return(true);
  }
};

function pesticideSearchViewModel()
{
  var self = this;

  self.visibleTracker = {
    'pesticide_ai_search': ko.observable(true),
    'brand_info': ko.observable(false),
    'ai_info': ko.observable(false)
  };
  self.spinner = null;
  self.showSpinner = ko.observable(false);
  self.activeBrand = ko.observableArray([]);
  self.activeAI = ko.observableArray([]);
  self.listName = ko.observable('');
  self.activeList = ko.observableArray([]);

  //self.pesticide_names = ko.observableArray([]);
  //self.ai_names = ko.observableArray([]);
  self.initialize = function()
  {
    self.showSpinner(true);
    var target = document.getElementById('spinner');
    self.spinner = new Spinner(spinner_opts).spin(target);

    $.getJSON('http://sccoastalpesticides.org/pesticide_tool/get_pestcide_ai_names',
      function(data) {
        $("#pesticide_names").typeahead({ source: data.pesticides });
        $("#ai_names").typeahead({ source: data.active_ingredients });
      }
    );
  };
  self.hashchanged = function(event)
  {
    //Force the page to the top whenever we change pages since most are long lists of pics.
    //If we don't do this, when using the back key the previous page will pick up where we left
    //the currect page.
    $('body').scrollTop(0);
    self.check_url();
  };
  self.check_url = function()
  {
    var state = $.bbq.getState();
    var url = decodeURIComponent($.param.fragment());
    //We're starting at a specific category, so let's update.
    if(url.length) {
    }
    else
    {

    }
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
  };
  self.brandSearch = function(name, event)
  {
    var brand_name = $('#pesticide_names').val();

    var url = $.param.fragment();

    var hash = url + '/#' + encodeURIComponent(brand_name);
    var frag = $.param.fragment('', hash, 2);
    $.bbq.pushState(frag);

    self.setVisible('brand_info');
    self.activeBrand([]);
    var target = document.getElementById('brand_nfo_spinner');
    self.spinner.spin(target);
    var url = 'http://sccoastalpesticides.org/pesticide_tool/get_info_for_brand';
    $.getJSON(url,
      {
        'brand': brand_name
      },
      function(data) {
        self.spinner.stop();
        self.activeBrand([data.brand_info]);
      }
    );
  };
  self.showApplicationAreas = function(brand_nfo, event)
  {
    self.listName("Application Areas");
    self.activeList(brand_nfo.application_areas);
  };
  self.showPestsTreated = function(brand_nfo, event)
  {
    self.listName("Pests Treated");
    self.activeList(brand_nfo.pests_treated);
  };

  self.activeIngredientSearch = function(name, event)
  {
    var ai_name = $('#ai_names').val();

    var url = $.param.fragment();

    var hash = url + '/#' + encodeURIComponent(ai_name);
    var frag = $.param.fragment('', hash, 2);
    $.bbq.pushState(frag);

    self.setVisible('ai_info');
    self.activeAI([]);
    var target = document.getElementById('brand_nfo_spinner');
    self.spinner.spin(target);
    var url = 'http://sccoastalpesticides.org/pesticide_tool/get_ai';
    $.getJSON(url,
      {
        'ai': ai_name
      },
      function(data) {
        self.spinner.stop();
        self.activeAI([data.ai_list]);
        $('[data-toggle="popover"]').popover({
          trigger: 'hover',
          'placement': 'top'
        });

      }
    );
  };
  self.getPanelClass = function(hazard_level)
  {
    var css = "panel panel-default";
    if(hazard_level !== undefined) {
      var lc_level = hazard_level.toLowerCase();
      if (lc_level == 'low') {
        css = "panel panel-success";
      }
      else if (lc_level == 'moderate') {
        css = "panel panel-warning";
      }
      else if (lc_level == 'likely') {
        css = "panel panel-danger";
      }
    }
    return(css);
  };


};

function pestModel(config)
{
  var self = this;
  ko.utils.extend(self, new buttonModel(config['display_name'], config['image_url']));

  //self.buttonData = new buttonModel(config['display_name'], config['image_url']);

  return self;
}



//app.viewModel = new selectionViewModel();
