
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

function categoriesViewModel(options)
{
  var self = this;
  //Array to track which parts should be visible.
  self.visibleTracker = {
    'category': ko.observable(true),
    'sub_category': ko.observable(false),
    'pest': ko.observable(false)
  };
  self.options = options;
  self.categoryModels = ko.observableArray([]); //The major categories of pests.
  self.activeCategory = ko.observable(new categoryModel());
  self.activeSubCategory = ko.observable(new subCategoryModel());
  self.aisForPestPage = ko.observable('');
  self.currentUrl = ''

  $( document ).ready()
  {

  };

  self.initialize = function()
  {
    // Bind the url hash change event.
    $(window).bind('hashchange', self.hashchanged);


    if( 'categories' in self.options)
    {
        $.each(self.options.categories, function(ndx, categoryNfo) {
          //Construct the categoryModel.
          var catModel = new categoryModel(categoryNfo['name'], categoryNfo);
          catModel.buildSubCategories(categoryNfo['sub_categories']);

          self.categoryModels.push(catModel);
        });
        $(document).on('mouseenter', '#hover-col .thumbnail', function(e)
        {
          $(this).find('.caption').slideDown(250);
        });
        $(document).on('mouseleave', '#hover-col .thumbnail', function(e)
        {
          $(this).find('.caption').slideUp(250);
        });

        /*
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
        */
        self.check_url();

    }

    //Query the server for the category data.
    /*
    var url = 'http://sccoastalpesticides.org/pesticide_tool/get_categories';
    $.getJSON(url,
        function(data)
        {
          //$.each(data.categories, function(ndx, categoryNfo) {
          $.each(self.options.categories, function(ndx, categoryNfo) {
            //Construct the categoryModel.
            var catModel = new categoryModel(categoryNfo['name'], categoryNfo);
            catModel.buildSubCategories(categoryNfo['sub_categories']);

            self.categoryModels.push(catModel);
          });

          //Setup hover event function for categories.
          //$("[rel='tooltip']").tooltip();

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
    */
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
      var url = '/pesticide_tool/get_pests_for_subcategory';
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
    var ai_page = '/pesticide_tool/active_ingredient/pest_name/' + pest.name();
    window.location.href = ai_page;
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

function pesticideSearchViewModel()
{
  var self = this;

  self.visibleTracker = {
    'pesticide_ai_search': ko.observable(true),
    'brands': ko.observable(false),
    'ai_info': ko.observable(false)
  };
  self.spinner = null;
  self.showSpinner = ko.observable(false);
  self.activeBrands = ko.observableArray([]);
  self.activeAI = ko.observable();
  self.ai_results = ko.observableArray([]);

  self.initialize = function(options)
  {
    self.showSpinner(true);
    var target = document.getElementById('spinner');
    self.spinner = new Spinner(spinner_opts).spin(target);

    //Server query to get the names we use in the typeahead.
    if('pesticides_typeahead' in options)
    {
      $("#pesticide_names").typeahead({ source: pesticides_typeahead });
    }
    if('ai_typeahead' in options)
    {
      $("#ai_names").typeahead({ source: ai_typeahead });
    }
    /*
    $.getJSON('http://sccoastalpesticides.org/pesticide_tool/get_pestcide_ai_names',
      function(data) {
        $("#pesticide_names").typeahead({ source: data.pesticides });
        $("#ai_names").typeahead({ source: data.active_ingredients });
      }
    );
    */
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
    if(brand_name > 0) {
      var brand_page = '/pesticide_tool/brand_name/' + (encodeURIComponent(brand_name));
      if (brand_name.indexOf('#') != -1) {
        //Double encode '#' otherwise Django url seems to stop processing url.
        brand_page = brand_page.replace('%23', '%2523');
      }
      if (brand_name.indexOf('%') != -1) {
        //Double encode '%' otherwise Django url seems to stop processing url.
        brand_page = brand_page.replace('%25', '%2525');
      }

      window.location.href = brand_page;
    }
  };
  self.activeIngredientSearch = function(name, event)
  {
    var ai_name = $('#ai_names').val();
    if(ai_name.length > 0) {
      var ai_page = '/pesticide_tool/active_ingredient/ai_name/' + (encodeURIComponent(ai_name));
      window.location.href = ai_page;
    }
  };
  self.showBrandInfo = function(brand, event)
  {
    var brand_page = '/pesticide_tool/brand_name/' + (encodeURIComponent(brand.name));
    if(brand.name.indexOf('#') != -1)
    {
      //Double encode '#' otherwise Django url seems to stop processing url.
      brand_page = brand_page.replace('%23','%2523');
    }
    if(brand.name.indexOf('%') != -1)
    {
      //Double encode '%' otherwise Django url seems to stop processing url.
      brand_page = brand_page.replace('%25','%2525');
    }

    window.location.href = brand_page;
  };

};

function brandViewModel(config)
{
  var self = this;

  self.activeBrand = ko.observableArray(config);
  self.listName = ko.observable('');
  self.activeList = ko.observableArray([]);

  self.initialize = function()
  {
  };
  self.getPanelClass = function(restricted_use)
  {
    var css = "panel panel-default";

    if(restricted_use !== undefined)
    {
      if(restricted_use)
      {
        css = "panel panel-danger";
      }
    }
    return(css);
  };
  self.getRestrictedUseText = function(use)
  {
    var ret_val = "Unknown";
    if(use !== undefined)
    {
      if (use)
      {
        ret_val = "Yes";
      }
      else
      {
        ret_val = "No"
      }
    }
    return(ret_val);
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

};

function aiViewModel(config) {
  var self = this;

  self.visibleTracker = {
    'ai_info': ko.observable(true),
    'brands': ko.observable(false)
  };

  self.activeAI = ko.observable();
  self.activeList = ko.observableArray(config);
  self.activeBrands = ko.observableArray([]);

  self.initialize = function()
  {
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
  self.showProducts = function(ai, event)
  {
    self.setVisible('brands');
    $('body').scrollTop(0);
    self.activeAI(ai.display_name);
    //Empty the curent brands.
    self.activeBrands([]);
    //ADd the brands from the selected AI.
    if(ai.brands.length)
    {
      self.activeBrands(ai.brands);
    }
    return(true);
  };
  self.showBrandInfo = function(brand, event)
  {
    var brand_page = '/pesticide_tool/brand_name/' + (encodeURIComponent(brand.name));
    if(brand.name.indexOf('#') != -1)
    {
      //Double encode '#' otherwise Django url seems to stop processing url.
      brand_page = brand_page.replace('%23','%2523');
    }
    var brand_page = '/pesticide_tool/brand_name/' + (encodeURIComponent(brand.name));
    if(brand.name.indexOf('%') != -1)
    {
      //Double encode '%' otherwise Django url seems to stop processing url.
      brand_page = brand_page.replace('%25','%2525');
    }
    window.location.href = brand_page;
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
