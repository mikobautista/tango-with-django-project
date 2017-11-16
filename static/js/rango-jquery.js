$(document).ready(function() {
    $('#like').click(function() {
        var catid;
        catid = $(this).attr("data-catid");
        $.get('/rango/like_category/', {category_id: catid}, function(data) {
                   $('#like_count').html(data);
                   $('#like').hide(); // TODO: Users can still "like" a category multiple times
        });
    });

    $('#suggestion').keyup(function() {
        var query;
        query = $(this).val();
        $.get('/rango/suggest_category/', {suggestion: query}, function(data) {
         $('#cats').html(data);
        });
    });
});