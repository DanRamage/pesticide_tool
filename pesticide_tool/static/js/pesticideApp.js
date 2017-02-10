
/*
//Load the initial configuration data that has the categories and button images.
app.viewModel.loadConfigData = function()
{
  //var url = 'http://129.252.139.124/projects/pesticide/feeds/layout_config.json';
  var url = 'http://sccoastalpesticides.org/feeds/layout_config.json';
  return $.getJSON(url,
          function(data)
          {
            app.viewModel.loadConfigurationData(data);
          });
};
app.viewModel.loadConfigurationData = function(data)
{
  $.each(data.layout.pest_categories, function(categoryName, categoryNfo) {
    //Construct the categoryModel.
    var catModel = new categoryModel(categoryName, categoryNfo);
    catModel.buildSubCategories(categoryNfo['sub_category'])

    app.viewModel.categoryModels.push(catModel);
  });
};

app.initialize = function()
{
  app.configData = null;
  app.pestDataQueryUrl = '../cgi-bin/pesticideWebReqHandler.py/safetyResults';

  app.viewModel.loadConfigData();
};
app.initPage = function()
{
  var self = this;
  // extend viewModel with a $__page__ that points to pager.page that points to a new Page
  pager.extendWithPage(app.viewModel);
  // apply your bindings
  ko.applyBindings(app.viewModel);
  // run this method - selectionViewModel to hashchange
  pager.start();


}
*/

function pesticideApp()
{
  var self = this;

  self.viewModel = null;
  self.configData = null;

  self.initialize = function()
  {
    self.pestDataQueryUrl = 'http://scpesticides.org/cgi-bin/new/pesticideWebReqHandler.py/safetyResults';
    //self.pestDataQueryUrl = 'http://129.252.139.124/projects/pesticide/handlers/pesticideWebReqHandler.py/safetyResults';
    var url = 'http://scpesticides.org/feeds/layout_config.json';
    //var url = 'http://129.252.139.124/projects/pesticide/feeds/layout_config.json';
    $.getJSON(url,
      function(data)
      {
        self.viewModel = new selectionViewModel();
        self.viewModel.loadConfigurationData(data);
      });

  };
  //This funciton initlizatizes the pager extension and knockout bindings. Our button data is in a json config file
  //and we don't want to call this funciton until it the Ajax request in the initialize function above completes.
  self.initPage = function()
  {
    // extend viewModel with a $__page__ that points to pager.page that points to a new Page
    pager.extendWithPage(self.viewModel);
    // apply your bindings
    ko.applyBindings(self.viewModel);
    // run this method - selectionViewModel to hashchange
    pager.start();


  }

  return(self);
}
