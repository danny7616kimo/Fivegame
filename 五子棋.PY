# app.py
from flask import Flask, render_template, request, jsonify
import numpy as np

app = Flask(__name__)

# 初始化遊戲板
board = np.zeros((15, 15), dtype=int)
current_player = 1

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/move', methods=['POST'])
def make_move():
    global board, current_player
    data = request.json
    row, col = data['row'], data['col']
    
    if board[row][col] == 0:
        board[row][col] = current_player
        winner = check_winner(row, col)
        current_player = 3 - current_player  # 切換玩家 (1 -> 2 或 2 -> 1)
        return jsonify({'board': board.tolist(), 'winner': winner})
    else:
        return jsonify({'error': 'Invalid move'}), 400

def check_winner(row, col):
    player = board[row][col]
    directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
    
    for dr, dc in directions:
        count = 1
        for i in range(1, 5):
            r, c = row + i*dr, col + i*dc
            if 0 <= r < 15 and 0 <= c < 15 and board[r][c] == player:
                count += 1
            else:
                break
        for i in range(1, 5):
            r, c = row - i*dr, col - i*dc
            if 0 <= r < 15 and 0 <= c < 15 and board[r][c] == player:
                count += 1
            else:
                break
        if count >= 5:
            return player
    return 0

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

# templates/index.html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>五子棋</title>
    <style>
        #board {
            display: grid;
            grid-template-columns: repeat(15, 30px);
            grid-gap: 1px;
            background-color: #deb887;
            padding: 10px;
        }
        .cell {
            width: 30px;
            height: 30px;
            background-color: #deb887;
            border: 1px solid #000;
            cursor: pointer;
        }
        .black {
            background-color: #000;
            border-radius: 50%;
        }
        .white {
            background-color: #fff;
            border-radius: 50%;
        }
    </style>
</head>
<body>
    <h1>五子棋</h1>
    <div id="board"></div>
    <p id="message"></p>

    <script>
        const board = document.getElementById('board');
        const message = document.getElementById('message');
        let gameBoard = Array(15).fill().map(() => Array(15).fill(0));

        function createBoard() {
            for (let i = 0; i < 15; i++) {
                for (let j = 0; j < 15; j++) {
                    const cell = document.createElement('div');
                    cell.className = 'cell';
                    cell.dataset.row = i;
                    cell.dataset.col = j;
                    cell.addEventListener('click', handleMove);
                    board.appendChild(cell);
                }
            }
        }

        function handleMove(event) {
            const row = parseInt(event.target.dataset.row);
            const col = parseInt(event.target.dataset.col);

            fetch('/move', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ row, col }),
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    message.textContent = data.error;
                } else {
                    updateBoard(data.board);
                    if (data.winner) {
                        message.textContent = `Player ${data.winner} wins!`;
                        board.removeEventListener('click', handleMove);
                    }
                }
            });
        }

        function updateBoard(newBoard) {
            gameBoard = newBoard;
            const cells = board.getElementsByClassName('cell');
            for (let i = 0; i < 15; i++) {
                for (let j = 0; j < 15; j++) {
                    const cell = cells[i * 15 + j];
                    cell.className = 'cell';
                    if (newBoard[i][j] === 1) {
                        cell.classList.add('black');
                    } else if (newBoard[i][j] === 2) {
                        cell.classList.add('white');
                    }
                }
            }
        }

        createBoard();
    </script>
</body>
</html>

# requirements.txt
Flask==2.0.1
numpy==1.21.0
gunicorn==20.1.0

# Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]