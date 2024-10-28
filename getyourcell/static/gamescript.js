document.addEventListener("DOMContentLoaded", function () {
    const boardElement = document.getElementById("game-board");
    const boardSize = 5; // 5x5 grid

    // Initialiser le plateau de jeu
    function initializeBoard(board) {
        boardElement.innerHTML = "";  // Vide le plateau
        board.forEach((row, x) => {
            row.forEach((cell, y) => {
                const cellDiv = document.createElement("div");
                cellDiv.classList.add("cell");
                cellDiv.dataset.x = x;
                cellDiv.dataset.y = y;

                if (cell === 1) {
                    cellDiv.classList.add("player1");
                } else if (cell === 2) {
                    cellDiv.classList.add("player2");
                }

                cellDiv.addEventListener("click", () => handleCellClick(x, y));
                boardElement.appendChild(cellDiv);
            });
        });
    }

    // Gérer le clic sur une case
    function handleCellClick(x, y) {
        fetch('/move', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ game_id: 1, player_id: 1, new_x: x, new_y: y })  // Exemple de données
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                initializeBoard(data.board);  // Met à jour l'interface avec le plateau reçu
            } else {
                alert(data.error);
            }
        });
    }

    // Charger l'état initial du plateau depuis le serveur
    fetch('/get_board')
        .then(response => response.json())
        .then(data => {
            initializeBoard(data.board);
        });
});
