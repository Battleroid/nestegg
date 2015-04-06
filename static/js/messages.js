$(document).ready(function () {
    $(".flash").each(function (index) {
        $(this).delay(5000 + (index * 1000)).slideUp(500);
    })
});