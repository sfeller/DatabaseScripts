/************************************************************
 * aqueti.js
 *
 * Interface function for aqueti web services
 *************************************************************/
"use strict";

//Global variables
//var socket = null; 

/************************************************************
 * Listener function for page events
 ************************************************************/
$(document).ready(function()
{
   //AddItem button callback
   $(document.body).on('click', "#addButton", function() 
   {
      //Go to parent and down to sibling UL
      var par = $(this).parent()
      var child = $(par).children().first(); //sibling UL

      //Create copy of last LI
      //get last li elment in sibling
      var ref = $(child).children().last().children().first(); 
      var element = $(ref).clone()

      //Step through element and change values
      clearElement( element);

      //Get child of child to set UL value
      var index = $(element).val();
      $(element).attr("index", index+1);

      //Create li element
      var li = document.createElement("li");
      var text = document.createTextNode(index+1);
      li.appendChild(text);
      li.appendChild(element[0]);

      //Add element into html
      $(li).appendTo(child);
   });

   //We are submittnig data
   $(document.body).on('click', "#submitButton", function()
   {
      ///////////////////////
      //Extract query data
      ///////////////////////
 
      var args = {};

      //Get collection name from the title
      var collection = $(this).attr("name");

      //The top-level ul is defined by the id of root
      var root = document.getElementById("root");

      var data = parseInputTree(root);

      //Put data in a form for submission
      args.collection = collection;
      args.data = data["root"];
      args.query = {"id":args.data["id"]};
      args.sort = {};

      db.setData( args, setResultCallback);
   });
});

/************************************************************
 * clear values for a given element and all of its children
 ************************************************************/
function clearElement( element )
{
   $(element).val("");

   var children = $(element).children();

   if(children.length > 0)
   {
      for( var i= 0; i <children.length; i++)
      {
         clearElement(children[i]);
      }
   }
}

/************************************************************
 * function to get a list of images
 *
 * This function gets a list of images from the database
 ************************************************************/
var genEditDiv = function(args)
{
   args.query={};
   args.sort={};

   if(args.id == "new")
   {
      args.create = true;
      db.genNewId( args, genNewIdCallback);

      return;
   }

   //Set query for the data we are looking for
   //sdf - Modify here to make general
   //Create query from the input value
   args.query[args["key"]] = args["value"];
   
   //get template for teh specified type
   alert("EditDiv: "+JSON.stringify( args))
   db.getData(args,getTemplateCallback);
}

/************************************************************
 * Callback to get new timestamp
 ************************************************************/
var genNewIdCallback = function(args)
{ 
   args.data = args.query;

   args.query["id"] = args["id"];

   //get template for teh specified type
   alert("newIDCall: "+JSON.stringify( args))
   db.getTemplateList(args, getTemplateListCallback);
}


/************************************************************
 * Callback from the loadTemplate Function
 ************************************************************/
var getTemplateListCallback = function(args,json) 
{
   args.template = json;

   alert("template:"+JSON.stringify( args));

   //get Data and generate form
   db.getData( args, getDataCallback);
}

/************************************************************
 * Function that generates forms
 *
 * args:
 *    collection - name of collection
 *    query      - search parameters
 *    sort       - sort paramerts
 *    template   - reference template
 *    data       - array of data from the database
 ************************************************************/
var getDataCallback = function(args)
{
   //Delete workDiv
   if( $("#workDiv").length != 0)
      document.getElementById("workDiv").remove();

   var workDiv = document.createElement("div");
   workDiv.setAttribute("id","workDiv");
   mainDiv.appendChild(workDiv);
   workDiv.setAttribute("title",args.collection);

   var item={};

   //Take first object if more than one generated
   if(isObject(args.data[0]))
      item = args.data[0];
   else
      item = args["query"];

   /////////////////////////////////////////////
   //Generate the preview image
   /////////////////////////////////////////////
   if( "preview" in item )
   {
      /////////////////////////////////////////////
      //Add preview image to webpage - if composite 
      /////////////////////////////////////////////
      var imgargs =
      {
         "src":item["preview"],
         "width":"80%",
         "height":"200px",
         "allowfullscreen":true,
         "seamless":true
      }

      //Generate preview images
      var previewFrame = genImage(imgargs);
      previewFrame.setAttribute("id","previewImg");
      workDiv.appendChild(previewFrame);
   }


   //sdf    if( $("#querySelect").length == 0)
   //Create the select element if we haven't. If we have, clear it
   //of its options
   /////////////////////////////////////////////
   //Generate the editForm content  
   /////////////////////////////////////////////
   //get workDiv and clear all history
   //Create a preview box
   /*
   var workDiv = document.createElement("div");
   workDiv.setAttribute("id","workDiv");
   mainDiv.appendChild(workDiv);
   workDiv.setAttribute("title",args.collection);
*/
   //Check if the root ul exists. It so, delete it.
 
   //Function to generate the edit form
   var ul = genUL( args["template"], item, "" );

   ul.setAttribute("title", "root");
   ul.setAttribute("id", "root");
   workDiv.appendChild(ul);

   var submitButton = document.createElement("input");
   submitButton.setAttribute("type","submit");
   submitButton.setAttribute("id","submitButton");
   submitButton.setAttribute("value","submit");
   submitButton.setAttribute("name",args.collection);


//   $('#submit').attr('onClick','alert("done"); return false;');
   
//   var text = document.createTextNode("Submit");
//   submitButton.appendChild(text);
   workDiv.appendChild(submitButton);

   workDiv.setAttribute("name","workDiv");
   workDiv.setAttribute("style","overflow-y: scroll");
   workDiv.setAttribute("method","post");
}
   
/************************************************************
 * Generate an iamge form a given value
 *
 * Top level function to generate the homepage. 
 ************************************************************/
function genWorkPage(input)
{
   //Get the mainDiv and assign some values
   var mainDiv = document.getElementById("mainDiv");
   mainDiv.setAttribute("id","mainDiv");
   mainDiv.setAttribute("style","overflow-y: scroll");

   utils.removeChildren(mainDiv);

   var args = {};

   if(input == undefined){
      args.collection = "templates";
   }
   else {
      args.collection = input;
   }

   //Get a list of collections in the database
   db.getCollectionList( args, getCollectionListCallback);
}

/************************************************************
 * This function is called whenever a new list of collections
 * is selected.
 *
 * args variables
 * - data - list of collection in the database
 ************************************************************/
var getCollectionListCallback = function( response, args)
{
   //Get the main element
   var mainDiv = document.getElementById("mainDiv");

   //Create select box at top
   var selectCollDiv = document.createElement("div");
   selectCollDiv.setAttribute("id","selectCollDiv");
   mainDiv.appendChild(selectCollDiv);

   args.collectionList = response;

   //Create dropdown list
   var select = genDropDownList( "collections","collections",args["collectionList"]);
   select.setAttribute("id","collectionDropDown");
   select.value = args.collection;

   //Add to the page elements
   selectCollDiv.appendChild(document.createTextNode("Collection: "));
   selectCollDiv.appendChild(select);

   //Create listener for a colleciton change. This is an event driven call
   $(select).change( function() 
   {
      //Establish collection and query
      //Get selected value and generate remaining pages
      args.collection = $("#collectionDropDown option:selected").text();

      //get data with the given callback
      db.getTemplates(args, getTemplatesCallback);
   });

   //trigger default selection
   $(select).trigger('change');
}

/************************************************************
 * This function is called whenever a new list of collections
 * is selected.
 *
 * args variables
 * - data - list of collection in the database
 ************************************************************/
var getTemplatesCallback = function(response, args)
{
   args["templates"] = response;

   //Get the main element
   var mainDiv = document.getElementById("mainDiv");

   //Create select box at top
   var templateDiv = document.createElement("div");
   templateDiv.setAttribute("id","templateDiv");
   mainDiv.appendChild(templateDiv);

   var templateList = [];
   var versionList = [];
   //Create dropdown list of templates to choose. 
   for( var i = 0; i < args["templates"].length; i++ )
   {
      templateList[i] = args["templates"][i]["name"];
      versionList[i] = args["templates"][i]["version"];
   }

   var select = genDropDownList( "templates","templates",templateList);
   select.setAttribute("id","templateDropDown");

   var versionSelect = genDropDownList( "templateVersion","templateVersion",versionList);
   versionSelect.setAttribute("id","templateVersionDropDown");

   //Add to the page elements
   templateDiv.appendChild(document.createTextNode("Templates: "));
   templateDiv.appendChild(select);
   templateDiv.appendChild(versionSelect);

   //Create the version field
   var versionSelect = genDropDownList

   //Create listener for a collection change. This is an event driven call
   $(select).change( function() 
   {
      //Establish collection and query
      //Get selected value and generate remaining pages
      args.template = $("#templateDropDown option:selected").text();
      args.query={"version":args["template"]}

      //get data with the given callback
      db.getData(args, getDataCallback());
   });

   //Create listener for version change
   $(select).change( function() 
   {
      //Establish collection and query
      //Get selected value and generate remaining pages
      args.template = $("#templateDropDown option:selected").text();
      args.query={"version":args["template"]}

      //get data with the given callback
      db.getData(args, getDataCallback());
   });

   //trigger default selection
   $(select).trigger('change');
}

/************************************************************
 * Function that is executed when a collection is selected
 *
 * Inputs:
 * - args.collection - name of selected collection
 * - args.query - query values for selecting items
 * - args.sort - sort options for data
 * - args.data - results from the getData
 ************************************************************/
var selectSelectCollectionCallback = function(args)
{
   //Get the queryDiv and set the title to the new value
   var mainDiv = document.getElementById("mainDiv");

   //Create select box at top
   var selectDocDiv = document.createElement("div");
   selectDocDiv.setAttribute("id","selectDocDiv");
   mainDiv.appendChild(selectDocDiv);

   //Create dropdown list
   for( var i = 0; i < args.data.length; i++ )
   {

   }
   var select = genDropDownList( "documents","documents",args.data);
   select.setAttribute("id","documentDropDown");

   //Add to the page elements
   selectDocDiv.appendChild(document.createTextNode("Document:"));
   selectDocDiv.appendChild(select);
/*
   //Create listener for a colleciton change. This is an event driven call
   $(select).change( function() 
   {
      var args = {};

      //Establish collection and query
      //Get selected value and generate remaining pages
      args.document= $("#selectDocDiv option:selected").text();
      args.query={};
      args.sort={};

      //get data with the given callback
      db.getData(args, documentSelectCallback);
   });
*/
   //trigger default selection
   $(select).trigger('change');
}

/************************************************************
 * Function that is executed when a collection is selected
 *
 * Inputs:
 * - args.collection - name of selected collection
 * - args.query - query values for selecting items
 * - args.sort - sort options for data
 * - args.data - results from the getData
 ************************************************************/
var documentSelectCallback = function(args)
{
   //Get the queryDiv and set the title to the new value
   var mainDiv = document.getElementById("mainDiv");

   //delete queryDiv if it exists
   if( $("#queryDiv").length != 0)
      document.getElementById("queryDiv").remove();

   //Create a preview box
   var queryDiv = document.createElement("div");
   queryDiv.setAttribute("title",args.collection);
   queryDiv.setAttribute("id","queryDiv");

   mainDiv.appendChild(queryDiv);

   //Create the select element if we haven't. If we have, clear it
   //of its options
   var select = document.createElement("select");
   select.setAttribute("id","querySelect");
   
   queryDiv.appendChild(document.createTextNode("Document:"));
   queryDiv.appendChild(select);

/*
   //Option to create a new document
   var newoption = document.createElement("option");
   $(newoption).val("new");
   $(newoption).attr("label","new");
   select.appendChild(newoption);
*/

   //Add an item for each item returned in args["data"]
   var data = args["data"]
   for( var i = 0; i < data.length; i++)
   {
      var item = data[i]
      alert( "Item: "+ JSON.stringify(item[item["key"]]))
      var option = document.createElement("option");
        $(option).val(item[item["key"]]);
        $(option).attr("key",item["key"]);
        $(option).attr("label",item[item["key"]]+" - "+item[item["timestamp"]]);
       select.appendChild(option);
   }
/*
   //Create listener to detect change in selected document
   $(select).change( function() 
   {
      var args={};
      args.collection = $("#queryDiv").attr("title");

      //Pull value from the calling function
      args.key = $("option:selected", this).attr("key");
      args.value= $(this).val();

      //Generate the edit element (top level for entire document)
      genEditDiv(args);
   });

   //Call change for the defult (new value0
   $(select).trigger('change');
*/
}

/************************************************************
 * Generate an dropdown list
 ************************************************************/
function genDropDownList( name, id, options )
{
   var select = document.createElement("select");

   for( var i = 0; i < options.length; i++ )
   {
      var opt = document.createElement("option");
      var text = document.createTextNode(options[i]);
      opt.appendChild(text);
 
      select.appendChild(opt);
   }

   select.setAttribute("id",id);
   select.setAttribute("name",name);

   return select;
}
      

/************************************************************
 * Generate an iamge form a given value
 ************************************************************/
function genImage(args)
{
   var frame = document.createElement("iframe");
   frame.setAttribute("src",args["src"]);
   frame.setAttribute("width",args["width"]);
   frame.setAttribute("height",args["height"]);
   if( args["allowfullscreen"])
      frame.setAttribute("allowfullscreen",true);
   if( args["seamless"])
      frame.setAttribute("seamless",true);
   
   return frame;
}

var setResultCallback = function(args)
{
   var url = document.URL;
   url = url.substring(0,url.indexOf("?"));
   url = url+"?"+args.collection+"="+args.query["id"];

   //reload with the given url
   window.location.assign(url);
   window.location.reload(true);
}

/************************************************************
 * parseInputTree
 *
 * Funciton to extract data from long list
 ************************************************************/
function parseInputTree( root )
{
   var tag = $(root).prop("tagName");
   var children = root.childNodes;
   var title = $(root).attr("title");

   //If UL
   if( tag == "UL")
   { 

      /////////////////////////////////////////////
      //If we're an array
      /////////////////////////////////////////////
      if( $(root).attr("class") == "array")
      {
         var  arr = [];

         for( var i= 0; i <children.length; i++)
         {
            var data = {};

            var tag = $(children[i]).prop("tagName");
            if( tag == "LI")
            {
               
               var local = {};
               var element = parseInputTree(children[i]);

               if( element != "")
                  arr.push(element);
            }
         }

         var data = {};
         data[title] = arr;

         return data;
      }
      /////////////////////////////////////////////
      //If we're a group
      /////////////////////////////////////////////
      else if( $(root).attr("class") == "group")
      {
         var result = [];
         var data = {};
         for(var i = 0; i< children.length; i++)
         {
            var element = parseInputTree(children[i]);

            if(element != -1)
            {
               var keys = Object.keys(element);
               for( key in keys)
                  data[keys[key]] = element[keys[key]];
            }
         }

         result.push(data);
         return data;
      }

      //Standard list processing
      else
      {
         var result={};
         var data={};

//         var listkey = $(root).attr("title");
         var listkey = title;

         for( var i= 0; i <children.length; i++)
         {
            var value = parseInputTree( children[i]);

            if( value != -1)
            {
               var keys = Object.keys(value);
               for( key in keys)
                  data[keys[key]] = value[keys[key]];
            }
         }
         result[listkey] = data;

         return result;
//         return data;
      }
   }
   //If an li element, add to dictionary
   else if( tag == "LI" )
   {
      for( var i = 0; i < children.length; i++)
      {

         var element = parseInputTree( children[i]);

         if( element != -1)
         {
            return element;
         }
      }
      return -1;
   }
   //If an input element, return value
   else if( tag == "INPUT")
   {
      var data = {};
//      var key = $(root).attr("title");
      var key = title;
      data[key] = $(root).val();
      return data
   }
   else if( tag == "SELECT")
   {
      var data = {};
      var key = title;
//      var s = $(root).find('option:selected');
//      alert("Options:"+s.text());

      data[key] = $(root).find("option:selected").text();
      return data;
   }

   return -1;
}

/************************************************************
 * parseForm
 *
 * Function that pulls all field from a form based on a template file
 ************************************************************
var parseForm = function(args, json)
{
   args.template = json["collections"][args.collection]["data"];

   //Load form into the object
   var item = document.getElementById(args.formName);

   var data = {};

   var $inputs = $('#mainDiv :input');

   $inputs.each( function()
   {
      var name = $(this).attr("title");
      data[name] = parseChildren(this);
      alert("Top:"+name+":"+data[name]);
   });
      alert(JSON.stringify(data));


   alert("Data:"+JSON.stringify(data));

   //Ready to write
   args.data = data;
   args.query = {"id":data["id"]};
   args.sort = {};

   setData( args, socketResult(args));
}
*/
/************************************************************
 * Recursive function to assign 
 ************************************************************
//function parseTitle(arr, data, value)
function parseTitle(arr, value)
{
   if(isObject(arr))
   {
      if( arr.length > 0)
      {
         var data = {};
         var key = arr[0];
         var newarr = arr.shift();
         data[key] = parseTitle(newarr, value);
         return data;
      }
      else
         return "";
   }
   else
   {
      var data = {};
      var key = arr[0];
      return data[key] = value;
   }

}
*/
/************************************************************
 * Recursive parsing function
 ************************************************************/
var parseChildren = function(item)
{
   var mydata = {};
   var title = item.getAttribute("title");
   var tag = $(item).prop("tagName");
   
   //If select option
   if(tag == "SELECT")
   {
      var value = $(item).val();
      var name = $(item).attr("title");
      var id = $(item).attr("id");

      if( typeof name == 'undefined')
         mydata[title] = name;
      else
      {
         var keys = name.split(":");
         mydata[title] = parseTitle( keys.shift(), value)
      }
   }

   //INPUT and SELECT options
   else if(tag == "INPUT")
   {
      var value = $(item).val();
      var name = $(item).attr("title");
      if( typeof name == 'undefined')
         mydata[title] = name;
      else
      {
         var keys = name.split(":");
         mydata[title] = parseTitle( keys.shift(), value);
      }
   }

   return mydata[name];
}

/************************************************************
 * Edit form validation procedure
 ************************************************************
function validateEditForm()
{
   var args={};
   args.url = "./js/template.json";
   
   //Form title defines the database we're using
   args.collection = document.getElementById("mainDiv").getAttribute("title");

   var data={};

/* 

   ///////////////////////
   //Extract query data
   ///////////////////////
   $('#editForm').submit(function() {
      // get all the inputs into an array.
      var $inputs = $('#editForm :input');

      $inputs.each( function()
      {
         data = findParents(this, data);
      });
      alert(JSON.stringify(data));

      var $selects = $('#editForm :selected');
      $selects.each( function()
      {
         var id = this.id;
//         var id = this.getAttribute("id");

         //Check if we're a key...
         if( id != "" )
         {
            if( id == "key")
            {
               //Create a dummy object to add to dictionary
               var par = $(this).parent().parent().parent();
               var val = $(this).val();

               var input = document.createElement("input");
               input.setAttribute("value",123);
               input.setAttribute("title",val);
               input.setAttribute("id",array);
               par.append(input);

               data = findParents(input, data);
            }
         }
         else
            data = findParents(this, data);
      });

      alert(JSON.stringify(data));

      args.data = data;
      args.query = {"id":data["id"]};
      args.sort = {};
      setData( args, socketResult(args));


      //set data
//   });

}
*/
/************************************************************
 * find Parents
 ************************************************************
var findParents = function(element, data, local )
{
   //Make local a dictionary if not defined
   if( !isObject(local))
      local = {};

   //Get the parent of the parent
   var par = $(element).parent().parent();

   //get the granparents title
   var ptitle = $(par).attr("title");
   var ptag = $(par).prop("tagName");
   var tag = $(element).prop("tagName");
   var id = $(element).prop("id");

   //If we're at the top, go here
   if((tag=="INPUT")||(tag=="input"))
   {
      if(ptitle == "root")
      {
         data[ $(element).attr("title")] = $(element).val();
         return data;
      }
      else if( id == "array")
      {
         local = [$(element).val()];
      }
      else
      {
         local = $(element).val();
         data = findParents(par, data, local);
      }
   }
   //We're at the top with a local object
   else if(ptitle == "root")
   {
      var title = $(element).attr("title");
      data[title] = local; 
      return data;
   }
   //Need to create new object and pass up
   if((ptag == "UL")||(ptag=="ul"))
   {
      var title = $(element).attr("title");
      var local2 = {};
      local2[title] = local;

      data = findParents( par, data, local2 );
      return data;
   }

   return data;
}
*/

/*
var genDataDict = function( args, json)
{
   var template = json["collections"][args["collection"]]["data"];

   var result = genDict(template, args["data"]);

   //set data
   setData( result, socketResult(args));
   
}

function genDict( template, data)
{
   var result = {}

   //loop through template to move form info into dictionary
   for( var key in template)
   {
      if(template[key]["type"] == "dictionary")
      {
         result[key] = genDict(template[key]["data"], data[key]);
      }
      else if( key in data)
      {
         result[key] = data[key]
      }
   }

   return result;
}
*/

   
/***********************************************************
 * genUL
 *
 * function to generate an unordered list
 ***********************************************************/
function genUL( template, item)
{
   //Create the unordered list
   var ul = document.createElement("ul");

   //Loop through all of the keys in the template and
   //generate the appropriate item
   for( var key in template)
   {
      if(item==undefined)
         var li = genInput( template[key],"",key);
      else
         var li = genInput( template[key],item[key], key);

//      li.setAttribute("title",key);
      ul.appendChild(li);
   }
   return ul;
}

/***********************************************************
 * genInput
 *
 * Function to generate the input Form
 *
 * Steps through all template component provided.
 ************************************************************/
function genInput(template, item, key)
{
   //Create an li component
   var li = document.createElement("li");

   /////////////////////////////////////////////
   //Generate a dictionary UL
   /////////////////////////////////////////////
   if(template["type"] == "dictionary")
   {
      var ul2 = genUL(template["data"], item, key);
      ul2.setAttribute("title",key);
      ul2.setAttribute("class","dict");

      var text = document.createTextNode(key);

      li.appendChild(text);
      li.appendChild(ul2);
   }

   /////////////////////////////////////////////
   // Generate an array ul
   /////////////////////////////////////////////
   else if( template["type"] =="array")
   {
      //Create a ne ul element
      var ul = document.createElement("ul");
      ul.setAttribute("class","array");
      ul.setAttribute("title",key);
     
      //Key key if it does not exist make it an empty array
      if( !isArray(item))
         item = [];

      //Add text to descript li
      var text = document.createTextNode(key)
      li.appendChild(text);

      if(item.length == 0)
      {
         item.push("");
      }

      //Loop through the array and generate an li for each
      if( item.length > 0)
      {
         for( var i = 0; i < item.length; i++ )
         {
            var li2 = document.createElement("li");
            var text = document.createTextNode(i);
            li2.appendChild(text);

            //sdf - perhaps we shoudl 
            //generate an UL 
            var ul2 = genUL( template["data"],item[i], key)
            ul2.setAttribute("index",i);
            ul2.setAttribute("class","group");

            li2.appendChild(ul2);
            ul.appendChild(li2);
         }

         //Create add button
         var addButton = document.createElement("button");
         var text = document.createTextNode("Add");
         addButton.appendChild(text);
         addButton.setAttribute("title",key);
         addButton.setAttribute("id","addButton");

         li.appendChild(ul);
         li.appendChild(addButton);
      }
   }

   /////////////////////////////////////////////
   // If input is select type
   /////////////////////////////////////////////
   else if( template["type"] == "select")
   {
      var select = genDropDownList( key,key,template["options"]);
      select.setAttribute("title",key);

      for( var value in template["options"])
      {
         if( item == template["options"][value])
         {
            $(select).val(item);
         }
      }

      li.innerHTML = key;
      li.appendChild(select);
   }

   /////////////////////////////////////////////
   // If all else fails, use normal text input
   /////////////////////////////////////////////
   else
   {
      //Normal processing
      var input = document.createElement("input");
      input.setAttribute("type","text");
 
      if( isObject(item ))
         input.setAttribute("value",item[key]);
      else
         input.setAttribute("value",item);

      input.setAttribute("name",key);
      input.setAttribute("title",key);

      //check if readonly
      if( template["edit"] == false)
      {
         input.setAttribute("readonly",true);
         input.setAttribute("disable",true);
      }

//      li.setAttribute("title",key);
      li.innerHTML=key;
      li.appendChild(input);
   }
   
   return li;
}
   
/************************************************************
 * genArray
 ************************************************************/
function genArray( template )
{
   var item = {};

   //Loop through template and add a field for each item
   for( var key in template)
   {
      if(template[key]["type"] == "array")
         item[key]= [];
      else if( template[key]["type"] == "dictionary")
         item[key]= {};
      else
         item[key]="";
   }

   return item;
 }
   
/************************************************************
 * function to get a list of images
 *
 * This function gets a list of images from the database
 ************************************************************
function genImageList( id )
{
   //Parse url to get query
   var query = getUrlValues();
   var sort ={};
   
   var listElement = document.getElementById(id);
      
   //Set up processing function for callback to be called when imagelist data is receieved
   var callback = 
   {
      args:{"listElement":listElement, "fields":["test1","test2"]},
      process: function(data, args)
      {
         var home = "";
         var items=data.length;
   
         for( var i = 0; i<items; ++i)
         {
            home = "";
               
            var listItem = document.createElement("li");
   
            //Generate components
            var url=data[i]["outputFiles"]["krpano"];
            url = home+url.replace(/"/g,"");
   
            //This is for Cameron
            var link = "<a href=\""+url+"/index.html\"></a>";
            var div = "<div class=\"title\">"+data[i]["title"]+"</div>";
            var img = "<img src=\""+url+"/preview.jpg\" />"; 
            var embed = "<a href=\""+url+"/index.html\"><iframe width=100% height=100% src=\""+link+"\"></iframe></a>";
            var embed2 = "&lt;iframe width=100% height=50% src=\""+url+"/index.html\"&gt;&lt;/iframe&gt;";
   
   	      if( "title" in data[i])
            {
   	         var item = "<a href=\""+url+"/index.html\">"+img+"<h2>"+data[i]["title"]+"</h2></a>";
            }
            else
            {
   	         var item = "<a href=\""+url+"/index.html\">"+img+"</a>";
            }
   
            listItem.innerHTML = item;
            listElement.appendChild(listItem);
         }
      }
   };
   
   var dataArgs={"collection":collection,"query":query,"sort":sort};

   //Initial call to get data
   getData(dataArgs, callback );
};
*/
   
/************************************************************
 * generateUL
 ************************************************************
function generateUL(id, query, sort, fields)
{
   //Find container element in html
   var listElement = document.getElementById(id);
   
   //Establish listen function to process results
   socket.once('data', function(data)
   {
      if(data.error)
      {
         alert("Data transmission error!");
      }
      else
      {
         var items=data.length;
         for( var i = 0; i<items; ++i)
         {
            var listItem = document.createElement("li");
            listItem.innerHTML = JSON.stringify(data[i]['title']);
            listElement.appendChild(listItem);
         }
      }
   });
   
   //Everything is ready. Emit data request. Call back should take results.
   socket.emit("getData", {"query":query, "sort":sort});
}
*/
   
/************************************************************
 * genDropDownList 
 *
 * Generate a dropdown list for an dictionary passed in
 ************************************************************/
var genSelectInput = function(items, fields) 
{
   var select = document.createElement("select");
   var item="";
   for( var i = 0; i < items.length; i++)
   {
      var option = document.createElement("option");
      option.value = items[i][fields[0]];
      option.text =  items[i][fields[0]];
      select.appendChild(option);
   }
   
   return select;
}
  
/************************************************************
 * isArray
 ************************************************************/
function isArray( obj )
 {
    return isObject(obj) && (obj instanceof Array);
 }

 /************************************************************
  * isObject 
  ************************************************************/
function isObject( obj )
  {
     return obj && (typeof obj  === "object");
  }


