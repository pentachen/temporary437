// Sends a new request to update the to-do list
function getPosts() {
  $.ajax({
    url: "/get-posts-json-followers",
    dataType : "json",
    success: updatePosts
  });

}

function updatePosts(items) {
  // Adds each new todo-list item to the list
  var posts = JSON.parse(items.posts);
  var users = JSON.parse(items.users);

  $(".post-common").remove();
  $(".shift-right").remove();

  $.each(posts, function(i, post) {
    var user = users[post.fields.user - 1];
    // regular post
    if(post.fields.parent == "") {      
      $("#post-feed").prepend(
        "<div class='post-common'>" + 
          "<p>" + sanitize(post.fields.text) + "</p>" + 
          "<form action=" + "\'/profile\'" + " method=\"GET\">" + 
            "<input type=\"hidden\" name=\"user\" value=" + user.fields.username + ">" + 
            "<table>" + 
            "<tr>" + 
              "<td>" + 
              "<img id=\"pp" + i + "\" src=\"/get_photo/" + post.fields.user + "\" alt=\"medium-rare pepe\" width=\"16px\">" + 
              "</td>" + 
              "<td> | </td>" + 
              "<td>" + post.pk + "</td>" + 
              "<td> | </td>" + 
              "<td><input class=\"plain\" type=\"submit\" value=" + user.fields.username + "></td>" + 
              "<td> | </td>" + 
              "<td>" + post.fields.datetime + "</td>" + 
            "</tr>" + 
            "</table>" + 
          "</form>" + 
        "</div>" +

        "<div class=\"shift-right\">" +

          "<div id=\'" + post.pk + "\' class=\"comment-list\">" +
          "</div>" +

          "<div class=\"post-box\">" +
            "<table>" +
            "<tr>" +
              "<td>" +
              "<button onclick=\"addComment(" + i + ")\" class=\"btn comment-btn pull-right\">comment</button>" +
              "</td>" +
              "<input id=\'com-parent" + i + "\' class=\"parent-box\" type=\"hidden\" name=\"parent\" value=\"" + post.pk + "\">" +
            "</tr>" +
            "</table>" +
          "</div>" +
          "<br>" +
          "<br>" +
        "</div>"
      );
    } else { // comment
      $("#" + post.fields.parent).append(
        "<div class='post-common'>" + 
          "<p>" + sanitize(post.fields.text) + "</p>" + 
          "<form action=" + "\'/profile\'" + " method=\"GET\">" + 
            "<input type=\"hidden\" name=\"user\" value=" + user.fields.username + ">" + 
            "<table>" + 
            "<tr>" + 
              "<td>" + 
              "<img id=\"pp" + i + "\" src=\"/get_photo/" + post.fields.user + "\" alt=\"medium-rare pepe\" width=\"16px\">" + 
              "</td>" + 
              "<td> | </td>" + 
              "<td>" + post.pk + "</td>" + 
              "<td> | </td>" + 
              "<td><input class=\"plain\" type=\"submit\" value=" + user.fields.username + "></td>" + 
              "<td> | </td>" + 
              "<td>" + post.fields.datetime + "</td>" + 
            "</tr>" + 
            "</table>" + 
          "</form>" + 
        "</div>"
      );
    }

    // replace any non-existant profile pics with the default pepe
    $("#pp" + i)
        .on('error', function(){
          $("#pp" + i).attr("src", "/static/user_default.jpg");})
    ;

  });
}

function lazy(i) {
  var temp = prompt("Please enter your comment text");
  if(temp != null) {
    $("#comment" + i).innerHTML = temp;
  }
}

function sanitize(s) {
  // Be sure to replace ampersand first
  return s.replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
}

function displayError(message) {
  $("#error").html(message);
}

function getCSRFToken() {
  var cookies = document.cookie.split(";");
  for (var i = 0; i < cookies.length; i++) {
    if (cookies[i].startsWith("csrftoken=")) {
      return cookies[i].substring("csrftoken=".length, cookies[i].length);
    }
  }
  return "unknown";
}

function addComment(i) {
  var textValue   = prompt("Please enter your comment text");
  var parentElement = $("#com-parent" + i);
  var parentValue   = parentElement.val();

  displayError('');

  $.ajax({
    url: "/add_comment",
    type: "POST",
    data: {'text': textValue,
           'parent': parentValue,
           'csrfmiddlewaretoken': getCSRFToken() },
    dataType : "json",
    success: function(response) {
      if (Array.isArray(response)) {
        getPosts;
      } else {
        displayError(response.error);
      }
    }
  });
}

window.onload = getPosts;

window.setInterval(getPosts, 5000);
