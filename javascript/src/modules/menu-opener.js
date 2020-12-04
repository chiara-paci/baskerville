$(".menu-opener").click(function(event){
    event.preventDefault();
    var target=$( $(this).data("target") );
    target.children("a").each(function(){
	if ($(this).css("visibility")=="visible") {
	    $(this).css({ 
		"visibility": "hidden"
	    });
	} else { 
	    $(this).css({ 
		"visibility": "visible"
	    });
	};
    });
});
