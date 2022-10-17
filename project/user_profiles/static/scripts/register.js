$(function(){
    $('#license').keyup(function( event ){
        $(this).val($(this).val().replace(/(\d{2})\-?(\d*)/,'$1-$2').replace(/(.{5})\-?(\d*)/,'$1-$2').replace(/(.{8})\-?(\d*)/,'$1-$2').replace(/(.{11}).*/,'$1'))
    });

    // source: https://www.c-sharpcorner.com/blogs/how-to-check-password-strength-in-jquery
    $('#password').keyup(function () {
        $('#strength').html(checkStrength($('#password').val()))
    })
    function checkStrength(password) {
        var strength = 0
        if (password.length > 6) strength += 1
        if (password.length > 9) strength += 1
        if (password.match(/([a-z].*[A-Z])|([A-Z].*[a-z])/)) strength += 1
        if (password.match(/([a-zA-Z])/) && password.match(/([0-9])/)) strength += 1
        if (password.match(/([!,%,&,@,#,$,^,*,?,_,~])/)) strength += 1

        if (strength < 3) {
            $('#strength').removeClass()
            $('#strength').addClass('Weak')
            return 'Weak'
        } else if (strength == 3 | strength == 4) {
            $('#strength').removeClass()
            $('#strength').addClass('Good')
            return 'Medium'
        } else {
            $('#strength').removeClass()
            $('#strength').addClass('Strong')
            return 'Strong'
        }
    }
});