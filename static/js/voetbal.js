$(function() {
  $("body").append("<div id=\"output\"></div>");
  $.getJSON("/BBCC89Q/all", function(data) {
    $("#wait").remove();
    table = "<h2>Programma</h2>";
    table += "<table class=\"programma\">";
    table += "<tr><th class=\"datum\">Datum</th><th class=\"wedstrijd\">Wedstrijd</th></tr>";

    table += "<tr><th colspan=\"2\">Thuis</th></tr>";
    $(data.programma.thuis).each(function(idx, val) {
      table += "<tr><td class=\"datum\">" + val["datum-tijd"] + "</td><td class=\"wedstrijd\">" + val["wedstrijd"] + "</td></tr>";
    });

    table += "<tr><th colspan=\"2\">Uit</th></tr>";
    $(data.programma.uit).each(function(idx, val) {
      table += "<tr><td class=\"datum\">" + val["datum-tijd"] + "</td><td class=\"wedstrijd\">" + val["wedstrijd"] + "</td></tr>";
    });

    table += "</table>";
    $("#output").append(table);

    table = "<h2>Uitslagen</h2>";
    table += "<table class=\"uitslagen\">";
    table += "<tr><th class=\"datum\">Datum</th><th class=\"wedstrijd\">Wedstrijd</th><th class=\"uitslag\">Uitslag</th></tr>";

    table += "<tr><th colspan=\"3\">Thuis</th></tr>";
    $(data.uitslagen.thuis).each(function(idx, val) {
      table += "<tr><td class=\"datum\">" + val["datum"] + "</td><td class=\"wedstrijd\">" + val["wedstrijd"] + "</td><td class=\"uitslag\">" + val["uitslag"] + "</td></tr>";
    });

    table += "<tr><th colspan=\"3\">Uit</th></tr>";
    $(data.uitslagen.uit).each(function(idx, val) {
      table += "<tr><td class=\"datum\">" + val["datum"] + "</td><td class=\"wedstrijd\">" + val["wedstrijd"] + "</td><td class=\"uitslag\">" + val["uitslag"] + "</td></tr>";
    });

    table += "</table>";
    $("#output").append(table);
  });
});
