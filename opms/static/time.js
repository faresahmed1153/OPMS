$(document).ready(function () {
    $("#add_my_schedual").submit(function (e) {

        var start_time = $('#f').val();
        var end_time = $('#t').val();




        alert(start_time);
        alert(end_time);
        if ((start_time > end_time) || (start_time === end_time)) {
            alert("from time must be lower than to time")
            e.preventDefault();
        }

    });
});