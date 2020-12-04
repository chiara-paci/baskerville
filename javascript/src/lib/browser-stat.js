/*** browser statistic ***/

var collect_stat = function(url){
    var form=$("#browserinfo");
    var luxon_prop=luxon.Info.features();
    var dt=luxon.DateTime.local();
    var data = {
	"csrf_token": form.children("input[name=csrfmiddlewaretoken]").val(),
	"code_name": navigator.appCodeName,
	"name": navigator.appName,
	"version": navigator.appVersion,
	"language": navigator.language,
	"platform": navigator.platform,
	"user_agent": navigator.userAgent,
	"cookies_enabled": navigator.cookieEnabled,
	"screen_width": screen.width,
	"screen_height": screen.height,
	"screen_available_width": screen.availWidth,
	"screen_available_height": screen.availHeight,
	"screen_color_depth": screen.colorDepth,
	"screen_pixel_depth": screen.pixelDepth,
	"luxon_intl": luxon_prop["intl"],
	"luxon_intl_tokens": luxon_prop["intlTokens"],
	"luxon_zones": luxon_prop["zones"],
	"luxon_relative": luxon_prop["relative"],
	"timezone": dt.zoneName,
	"iso_timestamps": dt.toISO(),
	"viewport_width": Math.max(document.documentElement.clientWidth, window.innerWidth || 0),
	"viewport_height": Math.max(document.documentElement.clientHeight, window.innerHeight || 0)
    }
    $.ajax({
	"url": url,
	"data": data,
	"headers": {
	    "Accept": "application/json"
	},
	"method": "POST",
	"success":function( data ) {
	    console.log("ok",ret);
	},
	"error": function(ret){
	    console.log("error",ret);
	    
	}	
    }); 
    
};


