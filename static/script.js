$(document).ready(function () {
    var fen = $('#hidden-info').text();
    var board;
    var game = new Chess(fen); // Initialize the Chess game with the initial FEN position

    // Configuration for Chessboard.js
    var boardConfig = {
        draggable: true,
        position: fen,
        onDragStart: onDragStart,
        onDrop: onDrop,
        onMouseoutSquare: onMouseoutSquare,
    };

    board = ChessBoard('board', boardConfig);

    function onDragStart(source, piece, position, orientation) {
        // Allow dragging only if it's the player's turn based on the FEN
        if (game.turn() === 'w' && piece.search(/^b/) !== -1) {
            return false;
        } else if (game.turn() === 'b' && piece.search(/^w/) !== -1) {
            return false;
        }
    }

    function onDrop(source, target) {
        // Check if the move is valid
        var move = game.move({
            from: source,
            to: target,
            promotion: 'q', // promote to queen by default
        });

        // If the move is not valid, snap the piece back to the source square
        if (move === null) {
            return 'snapback';
        }

        // Create a FormData object and append your variables
        var formData = new FormData();

        var whiteValue = document.querySelector('input[name="white"]').value;
        formData.append('white', whiteValue);

        var blackValue = document.querySelector('input[name="black"]').value;
        formData.append('black', blackValue);

        var fenValue = document.querySelector('input[name="fen"]').value;
        formData.append('fen', fenValue);

        var gmmoveValue = document.querySelector('input[name="gmmove"]').value;
        formData.append('gmmove', gmmoveValue);

        var bestValue = document.querySelector('input[name="best_moves"]').value;
        formData.append('best_moves', bestValue);

        var gmevalValue = document.querySelector('input[name="gmeval"]').value;
        formData.append('gmeval', gmevalValue);

        var moveValue = move.from + move.to;
        formData.append('move', moveValue);

        // Create a hidden form element and append it to the document
        var form = document.createElement('form');
        form.method = 'POST';
        form.action = '/play'; // Set the form's action URL to your server endpoint
        form.style.display = 'none'; // Hide the form

        // Append the form data to the hidden form
        for (var pair of formData.entries()) {
            var input = document.createElement('input');
            input.type = 'hidden';
            input.name = pair[0];
            input.value = pair[1];
            form.appendChild(input);
        }

        // Append the form to the document and submit it
        document.body.appendChild(form);
        form.submit();
    }



    function onMouseoutSquare(square, piece) {
        // Remove any highlights when the mouse moves out of a square
        removeHighlights(square);
    }

    function removeHighlights(square) {
        var squareEl = $('#board .square-' + square);
        squareEl.css('background', '');
    }

    // You can use this function to highlight squares, e.g., for valid moves
    function highlightSquare(square) {
        var squareEl = $('#board .square-' + square);
        var highlightColor = '#a9a9a9';

        squareEl.css('background', highlightColor);
    }

    // Dynamically set the board's orientation based on the side to move
    function setBoardOrientation() {
        boardConfig.orientation = game.turn() === 'w' ? 'white' : 'black';
        board = ChessBoard('board', boardConfig);
    }

    // Call setBoardOrientation initially to set the orientation
    setBoardOrientation();

    // Add an event listener to update the board's orientation when moves are made
    game.on('move', function () {
        setBoardOrientation();
    });
});

function validateForm() {
    var name = document.getElementById("move").value;

    if (name === "") {
        alert("Please fill out the move field.");
        return false;
    }

    return true; // Return true if the field is not empty
}

function submitForm(event) {
    event.preventDefault();  // Prevent the default form submission

    if (validateForm()) {
        var formData = new FormData(document.getElementById("moveForm"));

        fetch("/play", {
            method: "POST",
            body: formData
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error("Network response was not ok");
                }
                return response.text();
            })
            .then(data => {
                console.log("Server response:", data);
            })
            .catch(error => {
                console.error("Error:", error);
            });
    } else {
        alert("Invalid Move!");
    }
}
