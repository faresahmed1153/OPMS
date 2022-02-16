$(document).ready(function () {

    $(".use-address").click(function () {
        var info = [];
        $(this).closest('tr').find('td').each(function () {
            var textval = $(this).text();

            info.push(textval);


        });

        $.post("https://aqueous-tundra-43725.herokuapp.com/book-appointment", {
          name: info[0],
          specialty: info[1],
          price: info[2],
          day: info[3],
          date: info[4],
          fromt: info[5],
          to: info[6],
          room: info[7],
        });


    });

});