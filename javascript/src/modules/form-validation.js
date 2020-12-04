/*var invalidClassName = 'invalid';
var inputs = document.querySelectorAll('input, select, textarea');
inputs.forEach(function (input) {
  // Add a css class on submit when the input is invalid.
  input.addEventListener('invalid', function () {
    input.classList.add(invalidClassName)
  })

  // Remove the class when the input becomes valid.
  // 'input' will fire each time the user types
  input.addEventListener('input', function () {
    if (input.validity.valid) {
      input.classList.remove(invalidClassName)
    }
  })
})
*/


$("input").focus(function(event){
    $(this).parent().removeClass("invalid");
    $("section.auth-form div.errors p").fadeOut();
});

$("input#id_password2").change(function(event){
    var obj1=$("input#id_password1");
    if (obj1.length==0) return;

    var pwd1=$("input#id_password1").val();
    var pwd2=$("input#id_password2").val();
    var parent=$(this).parent();
    if (pwd1==pwd2) {
	parent.removeClass("invalid");
	return;
    }

    parent.addClass("invalid");
    var errmsg=gettext("The two passwords don't match");
    var errors=parent.find("div.requirements").find("ul.errorlist");
    if (errors.length==0) {
	parent
	    .find("div.requirements")
	    .prepend('<ul class="errorlist"><li>'+errmsg+'</li></ul>');
    }
    errors.html('<li>'+errmsg+'</li>');

});
