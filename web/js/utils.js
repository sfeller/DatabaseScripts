/************************************************************
 * isObject 
 ************************************************************/
isObject = function ( obj ) 
{
   return obj && (typeof obj  === "object");
}

/************************************************************
 * isArray
 ************************************************************/
isArray = function ( obj ) 
{
   return self.isObject(obj) && (obj instanceof Array);
}

var utils = 
{
   isObject: isObject,
   isArray: isArray,

  /************************************************************
   * Function to remove all children of an element
   ************************************************************/
   removeChildren: function( element)
   {
      var fc = element.firstChild;

      while( fc)
      {
         element.removeChild( fc );
         fc = element.firstChild;
      }
   },

   /************************************************************
    * function to get a URL value
    ************************************************************/
   getUrlValues: function ()
   {
      var vars={};
      var params=[];

      var searchString = window.location.search.substring(1);
      var variableArray = searchString.split('&');

      for(var i = 0; i < variableArray.length; i++)
      {
         //Otherwise, a key value pair
         var keyValuePair = variableArray[i].split('=');
         if( keyValuePair != null )
         {
            if(keyValuePair.length == 1)
            { 
               vars[keyValuePair[0]] = true;
            }
            else
            {
               vars[keyValuePair[0]] = keyValuePair[1];
               continue;
            }
         }
      }
      return vars;
   },

   getDocumentHeight: function()
   {
      var D = document;
      return Math.max(
         D.body.scrollHeight, D.documentElement.scrollHeight,
         D.body.offsetHeight, D.documentElement.offsetHeight,
         D.body.clientHeight, D.documentElement.clientHeight
         );
   }
}

