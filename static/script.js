$(document).ready(function () {
    var fen = $('#hidden-info').text();
    var board = ChessBoard('board', fen);
});
