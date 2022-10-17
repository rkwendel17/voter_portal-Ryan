$(function(){
    $('#phone_number').keyup(function( event ){
        $(this).val($(this).val().replace(/(\d{3})\-?(\d+)/,'$1-$2').replace(/(.{7})\-?(\d+)/,'$1-$2').replace(/(.{12}).*/,'$1'))
    });

    $('.zipTable').on('click', '.rowWrapper', function(event) {
        if ($(this).hasClass('selected')) {
            $(this).removeClass('selected');
            $('#remove-row').prop('disabled', true);
        } else {
            $(this).addClass('selected').siblings().removeClass('selected');
            $('#remove-row').prop('disabled', false);
        }
    });

    $('#remove-row').on('click', function(event) {
        $('.selected').remove();
    });

    $('#add-zip').prop('disabled', true);

    function validateNextButton() {
        var buttonDisabled = $('#zip-start').val().trim() === '' || $('#zip-end').val().trim() === '';
        $('#add-zip').prop('disabled', buttonDisabled);
        $(this).removeClass('is-invalid');
    }

    $('#zip-start').on('keyup', validateNextButton);
    $('#zip-end').on('keyup', validateNextButton);

    $('#add-zip').on('click', function(event) {
        if (!/^(\d{9}|\d{5}-\d{4})$/.test($('#zip-start').val())) {
            $('#zip-start').addClass('is-invalid');
        }
        if (!/^(\d{9}|\d{5}-\d{4})$/.test($('#zip-end').val())) {
            $('#zip-end').addClass('is-invalid');
        }
        if (/^(\d{9}|\d{5}-\d{4})$/.test($('#zip-start').val()) && /^(\d{9}|\d{5}-\d{4})$/.test($('#zip-end').val())) {
            var idx = $('.zipTable').find('.rowWrapper').length - 1;
            $('.zipTable').append(`<div class='rowWrapper' onclick=''>
                                        <div class='col border'>
                                            ${$('#zip-start').val()} <input type='hidden' name='zip-start-${idx}' value='${$('#zip-start').val()}'/>
                                        </div>
                                        <div class='col border'>
                                            ${$('#zip-end').val()} <input type='hidden' name='zip-end-${idx}' value='${$('#zip-end').val()}'/>
                                        </div>
                                    </div>
                                    <div class="w-100"></div>
                                  `)
            $('#zip-start').val('');
            $('#zip-end').val('');
        }
    });
});