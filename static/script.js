$(document).ready(function () {
    var fen = $('#hidden-info').text();
    var isBlacksTurn = fen.split(' ')[1] === 'b'; // Check if it's Black's turn

    // Determine the orientation based on the turn
    var orientation = isBlacksTurn ? 'black' : 'white';

    var board = ChessBoard('board', {
        position: fen,
        orientation: orientation // Set the board orientation
    });
});

