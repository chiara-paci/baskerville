$(".menu-opener").click(function(event){
    event.preventDefault();
    var target=$( $(this).data("target") );
    console.log( $(this),target);
    target.children("a").each(function(){
	console.log($(this),$(this).css("display"));
	
	if ($(this).css("display")=="none") {
	    $(this).css({ 
		"display": "inline-block"
	    });
	} else { 
	    $(this).css({ 
		"display": "none"
	    });
	};
    });
});
