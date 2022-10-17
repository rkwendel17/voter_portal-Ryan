$(function(){
    $('.candidate_select').on('click', function(event) {
        if ($(this).hasClass('selected')) {
            $(this).removeClass('selected');
            $(this).html("Select");
            $('#candidate_id').val("");
        } else {
            $('.candidate_select').removeClass('selected').html("Select");;
            $(this).addClass('selected');
            $(this).html("Selected");
            $('#candidate_id').val($(this).val());
        }
    });
});